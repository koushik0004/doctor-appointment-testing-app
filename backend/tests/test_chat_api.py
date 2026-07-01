import importlib
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


TEST_DB = Path(__file__).resolve().parent / "test_chat_api.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.db import database as database_module  # noqa: E402
from app.schemas.chat import (  # noqa: E402
    ChatConversationRequest,
    ChatConversationStatus,
    ChatIntent,
    ChatRequest,
    ChatRoutingTarget,
    ChatSearchFilters,
    ChatWorkflowStatus,
    ChatWorkflowType,
)
from app.knowledge.documents import (  # noqa: E402
    KnowledgeDocument,
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
)
from app.knowledge.retrieval import KnowledgeRetrievalMatch  # noqa: E402
from app.schemas.appointment import AppointmentCreateRequest, PatientInput  # noqa: E402
from app.schemas.doctor import AppointmentType  # noqa: E402
from app.services.appointment_service import create_appointment_booking  # noqa: E402
from app.services.chat_service import create_chat_response  # noqa: E402

get_settings.cache_clear()
database_module.get_engine.cache_clear()
database_module.get_session_factory.cache_clear()


@pytest.fixture()
def client():
    os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
    if TEST_DB.exists():
        TEST_DB.unlink()
    database_module.get_engine.cache_clear()
    database_module.get_session_factory.cache_clear()

    app_main_module = importlib.reload(importlib.import_module("app.main"))

    with TestClient(app_main_module.app) as test_client:
        yield test_client

    database_module.get_engine.cache_clear()
    database_module.get_session_factory.cache_clear()
    if TEST_DB.exists():
        TEST_DB.unlink()


def _session() -> Session:
    return database_module.get_session_factory()()


def test_chat_endpoint_returns_structured_specialty_response(client):
    response = client.post("/api/chat", json={"message": "Show cardiologists"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION.value
    assert payload["message"] == "Found 2 doctors for Cardiology."
    assert payload["response"] == payload["message"]
    assert len(payload["data"]) == 2
    assert payload["data"][0]["doctor_name"] == "Dr. Sarah Jenkins"
    assert payload["data"][1]["doctor_name"] == "Dr. Daniel Park"
    assert payload["conversation"]["routed_to"] == ChatRoutingTarget.DETERMINISTIC_ENGINE.value
    assert payload["conversation"]["status"] == ChatConversationStatus.ACTIVE.value


def test_chat_endpoint_returns_structured_filtered_search_response(client):
    response = client.post("/api/chat", json={"message": "Need a female cardiologist tomorrow"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_AVAILABLE_DOCTORS.value
    assert payload["search_filters"]["specialization"] == "Cardiology"
    assert payload["search_filters"]["gender"] == "Female"
    assert payload["search_filters"]["date"] == (date.today() + timedelta(days=1)).isoformat()
    assert payload["message"] == f"Found 6 available slots for Dr. Sarah Jenkins on {(date.today() + timedelta(days=1)).isoformat()}."
    assert payload["response"] == payload["message"]
    assert len(payload["data"]) == 6
    assert payload["data"][0]["doctor_name"] == "Dr. Sarah Jenkins"
    assert payload["data"][0]["available_date"] == (date.today() + timedelta(days=1)).isoformat()


def test_chat_endpoint_returns_structured_availability_response(client):
    response = client.post("/api/v1/chat", json={"message": "What slots does Dr. Sarah Jenkins have?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_AVAILABLE_DOCTORS.value
    assert payload["message"] == f"Found 6 available slots for Dr. Sarah Jenkins on {(date.today() + timedelta(days=1)).isoformat()}."
    assert payload["response"] == payload["message"]
    assert len(payload["data"]) == 6
    assert payload["data"][0]["doctor_name"] == "Dr. Sarah Jenkins"
    assert payload["data"][0]["available_date"] == (date.today() + timedelta(days=1)).isoformat()
    assert payload["data"][0]["available_time"] == "08:00"


def test_chat_endpoint_returns_structured_time_filtered_availability_response(client):
    response = client.post("/api/chat", json={"message": "Need appointment after 5 PM"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_AVAILABLE_DOCTORS.value
    assert payload["search_filters"]["time_preference"] == "After 5:00 PM"
    assert payload["message"] == (
        f"Found {len(payload['data'])} doctors available on {(date.today() + timedelta(days=1)).isoformat()}."
    )
    assert payload["response"] == payload["message"]
    assert len(payload["data"]) > 0
    assert {item["available_time"] for item in payload["data"]} == {"18:00"}


def test_chat_endpoint_returns_structured_doctor_details_response(client):
    response = client.post("/api/chat", json={"message": "What is Dr. Sarah Jenkins fee?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_DOCTOR_DETAILS.value
    assert payload["message"] == "Dr. Sarah Jenkins consultation fee is $120-$200. Next available slot: Today, 10:30 AM."
    assert payload["response"] == payload["message"]
    assert len(payload["data"]) == 1
    assert payload["data"][0]["doctor_name"] == "Dr. Sarah Jenkins"
    assert payload["data"][0]["consultation_fee_min"] == 120
    assert payload["data"][0]["consultation_fee_max"] == 200


def test_chat_endpoint_returns_doctor_details_for_partial_dr_name_query(client):
    response = client.post("/api/chat", json={"message": "Tell me about Dr. Sofia"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_DOCTOR_DETAILS.value
    assert payload["response"] == payload["message"]
    assert len(payload["data"]) == 1
    assert payload["data"][0]["doctor_name"] == "Dr. Sofia Martinez"
    assert payload["conversation"]["routed_to"] == ChatRoutingTarget.DETERMINISTIC_ENGINE.value


def test_chat_endpoint_routes_who_is_dr_query_to_doctor_details(client):
    response = client.post("/api/chat", json={"message": "Who is Dr. Sofia?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_DOCTOR_DETAILS.value
    assert payload["response"] == payload["message"]
    assert len(payload["data"]) == 1
    assert payload["data"][0]["doctor_name"] == "Dr. Sofia Martinez"


def test_doctor_list_endpoint_supports_gender_and_fee_filters(client):
    response = client.get("/api/doctors", params={"gender": "Female", "maximum_fee": 200})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert {item["name"] for item in payload["items"]} == {
        "Dr. Sarah Jenkins",
        "Dr. Aisha Khan",
        "Dr. Lucy Bennett",
        "Dr. Priya Nair",
    }


def test_chat_endpoint_returns_appointment_help_response(client):
    response = client.post("/api/chat", json={"message": "How do I book an appointment?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.APPOINTMENT_HELP.value
    assert payload["message"] == "Here is how to book an appointment in the app."
    assert payload["response"] == payload["message"]
    assert payload["data"] == []
    assert payload["help_steps"] == [
        "Choose a doctor.",
        "Select an available date.",
        "Choose a time slot.",
        "Enter patient details.",
        "Confirm the appointment.",
    ]


def test_chat_endpoint_returns_cancellation_help_response(client):
    response = client.post("/api/chat", json={"message": "How do I cancel my booking?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.CANCEL_APPOINTMENT_HELP.value
    assert payload["message"] == (
        "Appointment cancellation is not supported through AI chat. Please use the app's existing cancellation flow or contact support for help."
    )
    assert payload["response"] == payload["message"]
    assert payload["data"] == []
    assert payload["help_steps"] == [
        "Open the existing cancellation flow in the app.",
        "Find your booked appointment details.",
        "Follow the cancellation instructions shown there.",
        "If you cannot access the booking, contact support.",
    ]


def test_chat_endpoint_clarifies_fee_query_without_doctor_name(client):
    response = client.post("/api/chat", json={"message": "Consultation fee"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.SHOW_DOCTOR_DETAILS.value
    assert payload["message"] == "Which doctor's consultation fee would you like to know?"
    assert payload["response"] == payload["message"]
    assert payload["data"] == []


def test_chat_endpoint_returns_greeting_response(client):
    response = client.post("/api/chat", json={"message": "Hello"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == ChatIntent.UNKNOWN.value
    assert payload["message"] == "Hello, I am your AI Assistant."
    assert payload["response"] == payload["message"]
    assert payload["data"] == []


def test_chat_endpoint_rejects_blank_messages(client):
    response = client.post("/api/chat", json={"message": "   "})

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "message"]
    assert error["type"] == "string_too_short"


def test_chat_service_returns_available_specialties(client):
    with _session() as session:
        result = create_chat_response(session, ChatRequest(message="What specializations are available?"))

    assert result.intent == ChatIntent.UNKNOWN
    assert result.message == (
        "Available specializations: Cardiology, Dermatology, General Practice, Internal Medicine, Pediatrics."
    )
    assert result.response == result.message
    assert result.data == []
    assert result.conversation is not None
    assert result.conversation.routed_to == ChatRoutingTarget.DETERMINISTIC_ENGINE


def test_chat_service_maintains_conversation_filters_across_turns(client):
    with _session() as session:
        first_result = create_chat_response(
            session,
            ChatRequest(message="Show cardiologists"),
        )

        second_result = create_chat_response(
            session,
            ChatRequest(
                message="What about female doctors tomorrow?",
                conversation=ChatConversationRequest(
                    conversation_id=first_result.conversation.conversation_id if first_result.conversation else None,
                    context=first_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Show cardiologists",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters,
                        },
                        {
                            "role": "user",
                            "text": "What about female doctors tomorrow?",
                        },
                    ],
                ),
            ),
        )

    assert second_result.intent == ChatIntent.SHOW_AVAILABLE_DOCTORS
    assert second_result.search_filters is not None
    assert second_result.search_filters.specialization == "Cardiology"
    assert second_result.search_filters.gender == "Female"
    assert second_result.search_filters.date == date.today() + timedelta(days=1)
    assert second_result.message == (
        f"Found 6 available slots for Dr. Sarah Jenkins on {(date.today() + timedelta(days=1)).isoformat()}."
    )
    assert second_result.conversation is not None
    assert second_result.conversation.active_filters is not None
    assert second_result.conversation.active_filters.specialization == "Cardiology"
    assert second_result.conversation.turn_count == 2


def test_chat_service_resolves_follow_up_doctor_reference_from_conversation_context(client):
    with _session() as session:
        first_result = create_chat_response(
            session,
            ChatRequest(message="Need a female cardiologist tomorrow"),
        )

        second_result = create_chat_response(
            session,
            ChatRequest(
                message="What is the consultation fee?",
                conversation=ChatConversationRequest(
                    conversation_id=first_result.conversation.conversation_id if first_result.conversation else None,
                    context=first_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "What is the consultation fee?",
                        },
                    ],
                ),
            ),
        )

    assert first_result.conversation is not None
    assert first_result.conversation.selected_doctor_name == "Dr. Sarah Jenkins"
    assert second_result.intent == ChatIntent.SHOW_DOCTOR_DETAILS
    assert second_result.message == "Dr. Sarah Jenkins consultation fee is $120-$200. Next available slot: Today, 10:30 AM."
    assert second_result.conversation is not None
    assert second_result.conversation.selected_doctor_name == "Dr. Sarah Jenkins"


def test_chat_service_detects_missing_booking_workflow_fields(client):
    with _session() as session:
        first_result = create_chat_response(
            session,
            ChatRequest(message="Need a female cardiologist tomorrow"),
        )

        second_result = create_chat_response(
            session,
            ChatRequest(
                message="Book this appointment",
                conversation=ChatConversationRequest(
                    conversation_id=first_result.conversation.conversation_id if first_result.conversation else None,
                    context=first_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book this appointment",
                        },
                    ],
                ),
            ),
        )

    assert second_result.intent == ChatIntent.BOOK_APPOINTMENT
    assert second_result.workflow is not None
    assert second_result.workflow.workflow_type == ChatWorkflowType.BOOK_APPOINTMENT
    assert second_result.workflow.status == ChatWorkflowStatus.INPUT_REQUIRED
    assert second_result.workflow.missing_fields == [
        "start_time",
        "patient_full_name",
        "patient_email",
    ]
    assert second_result.conversation is not None
    assert second_result.conversation.routed_to == ChatRoutingTarget.WORKFLOW_ENGINE
    assert second_result.conversation.current_workflow is not None
    assert second_result.conversation.current_workflow.status == ChatWorkflowStatus.INPUT_REQUIRED


def test_chat_service_books_appointment_through_workflow(client):
    with _session() as session:
        first_result = create_chat_response(
            session,
            ChatRequest(message="Need a female cardiologist tomorrow"),
        )

        second_result = create_chat_response(
            session,
            ChatRequest(
                message=(
                    "Book 10:00 AM. My name is John Doe. "
                    "john.doe@example.com. Phone 9999999999."
                ),
                conversation=ChatConversationRequest(
                    conversation_id=first_result.conversation.conversation_id if first_result.conversation else None,
                    context=first_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book 10:00 AM. My name is John Doe. john.doe@example.com. Phone 9999999999.",
                        },
                    ],
                ),
            ),
        )

    assert second_result.intent == ChatIntent.BOOK_APPOINTMENT
    assert second_result.workflow is not None
    assert second_result.workflow.status == ChatWorkflowStatus.COMPLETED
    assert second_result.workflow.appointment is not None
    assert second_result.workflow.appointment.confirmation_code.startswith("CN-")
    assert second_result.workflow.appointment.patient_name == "John Doe"
    assert second_result.conversation is not None
    assert second_result.conversation.routed_to == ChatRoutingTarget.WORKFLOW_ENGINE
    assert second_result.conversation.current_workflow is not None
    assert second_result.conversation.current_workflow.status == ChatWorkflowStatus.COMPLETED


def test_chat_service_continues_booking_workflow_across_incremental_turns(client):
    with _session() as session:
        first_result = create_chat_response(
            session,
            ChatRequest(message="Need a female cardiologist tomorrow"),
        )

        second_result = create_chat_response(
            session,
            ChatRequest(
                message="Book this appointment",
                conversation=ChatConversationRequest(
                    conversation_id=first_result.conversation.conversation_id if first_result.conversation else None,
                    context=first_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book this appointment",
                        },
                    ],
                ),
            ),
        )

        third_result = create_chat_response(
            session,
            ChatRequest(
                message="10:00 AM",
                conversation=ChatConversationRequest(
                    conversation_id=second_result.conversation.conversation_id if second_result.conversation else None,
                    context=second_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book this appointment",
                        },
                        {
                            "role": "assistant",
                            "text": second_result.message,
                            "intent": second_result.intent,
                            "search_filters": second_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": second_result.conversation.selected_doctor_id if second_result.conversation else None,
                            "selected_doctor_name": second_result.conversation.selected_doctor_name if second_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "10:00 AM",
                        },
                    ],
                ),
            ),
        )

        fourth_result = create_chat_response(
            session,
            ChatRequest(
                message="John Doe",
                conversation=ChatConversationRequest(
                    conversation_id=third_result.conversation.conversation_id if third_result.conversation else None,
                    context=third_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book this appointment",
                        },
                        {
                            "role": "assistant",
                            "text": second_result.message,
                            "intent": second_result.intent,
                            "search_filters": second_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": second_result.conversation.selected_doctor_id if second_result.conversation else None,
                            "selected_doctor_name": second_result.conversation.selected_doctor_name if second_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "10:00 AM",
                        },
                        {
                            "role": "assistant",
                            "text": third_result.message,
                            "intent": third_result.intent,
                            "search_filters": third_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": third_result.conversation.selected_doctor_id if third_result.conversation else None,
                            "selected_doctor_name": third_result.conversation.selected_doctor_name if third_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "John Doe",
                        },
                    ],
                ),
            ),
        )

        final_result = create_chat_response(
            session,
            ChatRequest(
                message="john.doe@example.com",
                conversation=ChatConversationRequest(
                    conversation_id=fourth_result.conversation.conversation_id if fourth_result.conversation else None,
                    context=fourth_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book this appointment",
                        },
                        {
                            "role": "assistant",
                            "text": second_result.message,
                            "intent": second_result.intent,
                            "search_filters": second_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": second_result.conversation.selected_doctor_id if second_result.conversation else None,
                            "selected_doctor_name": second_result.conversation.selected_doctor_name if second_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "10:00 AM",
                        },
                        {
                            "role": "assistant",
                            "text": third_result.message,
                            "intent": third_result.intent,
                            "search_filters": third_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": third_result.conversation.selected_doctor_id if third_result.conversation else None,
                            "selected_doctor_name": third_result.conversation.selected_doctor_name if third_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "John Doe",
                        },
                        {
                            "role": "assistant",
                            "text": fourth_result.message,
                            "intent": fourth_result.intent,
                            "search_filters": fourth_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": fourth_result.conversation.selected_doctor_id if fourth_result.conversation else None,
                            "selected_doctor_name": fourth_result.conversation.selected_doctor_name if fourth_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "john.doe@example.com",
                        },
                    ],
                ),
            ),
        )

    assert second_result.workflow is not None
    assert second_result.workflow.status == ChatWorkflowStatus.INPUT_REQUIRED
    assert second_result.workflow.missing_fields == [
        "start_time",
        "patient_full_name",
        "patient_email",
    ]

    assert third_result.intent == ChatIntent.BOOK_APPOINTMENT
    assert third_result.workflow is not None
    assert third_result.workflow.status == ChatWorkflowStatus.INPUT_REQUIRED
    assert third_result.workflow.draft.start_time == "10:00"
    assert third_result.workflow.missing_fields == [
        "patient_full_name",
        "patient_email",
    ]

    assert fourth_result.intent == ChatIntent.BOOK_APPOINTMENT
    assert fourth_result.workflow is not None
    assert fourth_result.workflow.status == ChatWorkflowStatus.INPUT_REQUIRED
    assert fourth_result.workflow.draft.start_time == "10:00"
    assert fourth_result.workflow.draft.patient_full_name == "John Doe"
    assert fourth_result.workflow.missing_fields == ["patient_email"]
    assert fourth_result.conversation is not None
    assert fourth_result.conversation.routed_to == ChatRoutingTarget.WORKFLOW_ENGINE
    assert fourth_result.conversation.current_workflow is not None
    assert fourth_result.conversation.current_workflow.draft.patient_full_name == "John Doe"

    assert final_result.intent == ChatIntent.BOOK_APPOINTMENT
    assert final_result.workflow is not None
    assert final_result.workflow.status == ChatWorkflowStatus.COMPLETED
    assert final_result.workflow.appointment is not None
    assert final_result.workflow.appointment.patient_name == "John Doe"
    assert final_result.workflow.appointment.confirmation_code.startswith("CN-")


def test_chat_service_cancels_appointment_through_workflow(client):
    with _session() as session:
        created = create_appointment_booking(
            session,
            AppointmentCreateRequest(
                doctor_id=1,
                appointment_date=date.today() + timedelta(days=1),
                start_time="10:00",
                appointment_type=AppointmentType.IN_PERSON,
                patient=PatientInput(
                    full_name="Jane Doe",
                    email="jane.doe@example.com",
                    phone="8888888888",
                ),
                health_description="Routine checkup.",
            ),
        )

        result = create_chat_response(
            session,
            ChatRequest(message=f"Cancel appointment {created.id}"),
        )

    assert result.intent == ChatIntent.CANCEL_APPOINTMENT
    assert result.workflow is not None
    assert result.workflow.workflow_type == ChatWorkflowType.CANCEL_APPOINTMENT
    assert result.workflow.status == ChatWorkflowStatus.COMPLETED
    assert result.workflow.appointment is not None
    assert result.workflow.appointment.status == "CANCELLED"
    assert "has been cancelled" in result.message
    assert result.conversation is not None
    assert result.conversation.routed_to == ChatRoutingTarget.WORKFLOW_ENGINE


def test_chat_service_returns_confirmation_through_workflow(client):
    with _session() as session:
        created = create_appointment_booking(
            session,
            AppointmentCreateRequest(
                doctor_id=1,
                appointment_date=date.today() + timedelta(days=1),
                start_time="10:00",
                appointment_type=AppointmentType.IN_PERSON,
                patient=PatientInput(
                    full_name="Alex Doe",
                    email="alex.doe@example.com",
                    phone="7777777777",
                ),
                health_description="Routine checkup.",
            ),
        )

        result = create_chat_response(
            session,
            ChatRequest(message=f"Show my appointment confirmation for {created.confirmation_code}"),
        )

    assert result.intent == ChatIntent.APPOINTMENT_CONFIRMATION
    assert result.workflow is not None
    assert result.workflow.workflow_type == ChatWorkflowType.APPOINTMENT_CONFIRMATION
    assert result.workflow.status == ChatWorkflowStatus.COMPLETED
    assert result.workflow.appointment is not None
    assert result.workflow.appointment.confirmation_code == created.confirmation_code
    assert "is confirmed" in result.message


def test_chat_service_returns_default_fallback(client):
    with _session() as session:
        result = create_chat_response(session, ChatRequest(message="Need some help"))

    assert result.intent == ChatIntent.UNKNOWN
    assert result.message == (
        "I can help with available doctors, specializations, consultation fees, and appointment slots."
    )
    assert result.response == result.message
    assert result.data == []


def test_chat_service_uses_knowledge_retrieval_before_default_fallback(client, monkeypatch):
    knowledge_document = KnowledgeDocument(
        id="capabilities.assistant.v1",
        title="Assistant Capabilities",
        source_type=KnowledgeDocumentSourceType.JSON,
        source_path="backend/app/knowledge/sources/structured/assistant-capabilities.json",
        domain=KnowledgeDocumentDomain.CAPABILITY,
        audience=KnowledgeDocumentAudience.ASSISTANT,
        status=KnowledgeDocumentStatus.ACTIVE,
        version="1.0",
        tags=["assistant", "capabilities"],
        priority=30,
        summary="Defines current supported assistant capabilities.",
        content={
            "can_help_with": [
                "doctor discovery",
                "appointment availability",
            ],
        },
    )

    class FakeKnowledgeService:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def retrieve_top_match(self, query: str):
            self.calls.append(query)
            if "assistant capabilities" in query.lower():
                return KnowledgeRetrievalMatch(
                    document=knowledge_document,
                    score=20,
                    matched_terms=("assistant", "capabilities"),
                )
            return None

    fake_service = FakeKnowledgeService()
    monkeypatch.setattr("app.services.chat_service._knowledge_retrieval_service", lambda: fake_service)

    with _session() as session:
        result = create_chat_response(session, ChatRequest(message="assistant capabilities"))

    assert fake_service.calls == ["assistant capabilities"]
    assert result.intent == ChatIntent.UNKNOWN
    assert result.message == "I can help with doctor discovery and appointment availability."
    assert result.conversation is not None
    assert result.conversation.routed_to == ChatRoutingTarget.FUTURE_AI_LAYER


def test_chat_service_skips_knowledge_retrieval_during_active_workflow(client, monkeypatch):
    class FakeKnowledgeService:
        def __init__(self) -> None:
            self.calls = 0

        def retrieve_top_match(self, query: str):
            self.calls += 1
            return None

    fake_service = FakeKnowledgeService()
    monkeypatch.setattr("app.services.chat_service._knowledge_retrieval_service", lambda: fake_service)

    with _session() as session:
        first_result = create_chat_response(
            session,
            ChatRequest(message="Need a female cardiologist tomorrow"),
        )

        second_result = create_chat_response(
            session,
            ChatRequest(
                message="Book this appointment",
                conversation=ChatConversationRequest(
                    conversation_id=first_result.conversation.conversation_id if first_result.conversation else None,
                    context=first_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book this appointment",
                        },
                    ],
                ),
            ),
        )

        fake_service.calls = 0
        third_result = create_chat_response(
            session,
            ChatRequest(
                message="assistant capabilities",
                conversation=ChatConversationRequest(
                    conversation_id=second_result.conversation.conversation_id if second_result.conversation else None,
                    context=second_result.conversation,
                    history=[
                        {
                            "role": "user",
                            "text": "Need a female cardiologist tomorrow",
                        },
                        {
                            "role": "assistant",
                            "text": first_result.message,
                            "intent": first_result.intent,
                            "search_filters": first_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": first_result.conversation.selected_doctor_id if first_result.conversation else None,
                            "selected_doctor_name": first_result.conversation.selected_doctor_name if first_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "Book this appointment",
                        },
                        {
                            "role": "assistant",
                            "text": second_result.message,
                            "intent": second_result.intent,
                            "search_filters": second_result.search_filters or ChatSearchFilters(),
                            "selected_doctor_id": second_result.conversation.selected_doctor_id if second_result.conversation else None,
                            "selected_doctor_name": second_result.conversation.selected_doctor_name if second_result.conversation else None,
                        },
                        {
                            "role": "user",
                            "text": "assistant capabilities",
                        },
                    ],
                ),
            ),
        )

    assert fake_service.calls == 0
    assert third_result.conversation is not None
    assert third_result.conversation.routed_to == ChatRoutingTarget.WORKFLOW_ENGINE
