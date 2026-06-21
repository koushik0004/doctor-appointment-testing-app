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
from app.schemas.chat import ChatIntent, ChatRequest  # noqa: E402
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
    assert payload["message"] == (
        "I can help you book an appointment. Share a doctor, preferred date, time, and appointment type."
    )
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


def test_chat_service_returns_default_fallback(client):
    with _session() as session:
        result = create_chat_response(session, ChatRequest(message="Need some help"))

    assert result.intent == ChatIntent.UNKNOWN
    assert result.message == (
        "I can help with available doctors, specializations, consultation fees, and appointment slots."
    )
    assert result.response == result.message
    assert result.data == []
