from __future__ import annotations

import re
from datetime import datetime
from time import perf_counter

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.schemas.appointment import AppointmentConfirmationResponse, AppointmentCreateRequest, PatientInput
from app.schemas.chat import (
    ChatConversationContext,
    ChatIntent,
    ChatResponse,
    ChatSearchFilters,
    ChatWorkflowAppointmentSummary,
    ChatWorkflowDraft,
    ChatWorkflowResult,
    ChatWorkflowState,
    ChatWorkflowStatus,
    ChatWorkflowType,
)
from app.schemas.doctor import AppointmentType, DoctorResponse
from app.services.appointment_service import (
    cancel_appointment_booking,
    create_appointment_booking,
    get_appointment_confirmation_by_reference,
)
from app.services.chat_entity_extractor import extract_target_date, normalize_text
from app.services.doctor_service import list_doctors
from app.llm.runtime_trace import AIRuntimeTraceSession

HELP_KEYWORDS = ("help", "how do i", "how to", "steps")
BOOKING_ACTION_KEYWORDS = ("book", "booking", "schedule", "reserve")
CANCELLATION_ACTION_KEYWORDS = ("cancel", "cancellation")
CONFIRMATION_ACTION_KEYWORDS = (
    "confirmation",
    "confirm my appointment",
    "appointment details",
    "show my appointment",
    "my appointment",
)
WORKFLOW_SWITCH_KEYWORDS = ("start over", "switch", "something else", "different question")


def _contains_keyword(normalized_message: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in normalized_message for keyword in keywords)


def _extract_confirmation_code(message: str) -> str | None:
    match = re.search(r"\bCN-\d{5}-[A-Z0-9]{2}\b", message.upper())
    return match.group(0) if match else None


def _extract_appointment_id(normalized_message: str) -> int | None:
    match = re.search(r"\bappointment(?:\s+id)?\s*#?\s*(\d+)\b", normalized_message)
    if match:
        return int(match.group(1))
    return None


def _extract_patient_email(message: str) -> str | None:
    match = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", message, re.IGNORECASE)
    return match.group(0) if match else None


def _extract_patient_phone(message: str) -> str | None:
    match = re.search(r"\b(?:\+?\d[\d\s-]{7,}\d)\b", message)
    if not match:
        return None
    return re.sub(r"\s+", "", match.group(0))


def _extract_patient_name(message: str) -> str | None:
    patterns = (
        r"\bmy name is\s+([A-Za-z]+(?: [A-Za-z]+){1,3})\b",
        r"\bi am\s+([A-Za-z]+(?: [A-Za-z]+){1,3})\b",
        r"\bfor\s+([A-Za-z]+(?: [A-Za-z]+){1,3})\b",
        r"\b(?:patient\s+)?full name\s*[:\-]\s*([A-Za-z]+(?: [A-Za-z]+){1,3})\b",
        r"\b(?:patient\s+)?name\s*[:\-]\s*([A-Za-z]+(?: [A-Za-z]+){1,3})\b",
    )
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return " ".join(part.capitalize() for part in match.group(1).split())
    return None


def _extract_bare_patient_name(message: str) -> str | None:
    stripped_message = message.strip()
    if not stripped_message or "@" in stripped_message or any(character.isdigit() for character in stripped_message):
        return None
    if len(stripped_message.split()) < 2 or len(stripped_message.split()) > 4:
        return None
    if re.search(r"[^A-Za-z\s'’-]", stripped_message):
        return None
    return " ".join(part.capitalize() for part in stripped_message.replace("’", "'").split())


def _extract_health_description(message: str) -> str | None:
    patterns = (
        r"\b(?:reason|issue|symptoms?)\s*(?:is|:)\s*(.+)$",
        r"\bfor\s+(fever|cold|checkup|follow up|follow-up|headache|rash|pain|consultation)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, normalize_text(message))
        if match:
            value = match.group(1).strip()
            if value:
                return value.capitalize()
    return None


def _extract_appointment_type(normalized_message: str) -> str | None:
    if any(keyword in normalized_message for keyword in ("telemedicine", "video", "online", "virtual")):
        return AppointmentType.TELEMEDICINE.value
    if any(keyword in normalized_message for keyword in ("in person", "in-person", "clinic visit")):
        return AppointmentType.IN_PERSON.value
    return None


def _extract_start_time(message: str) -> str | None:
    match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", message, re.IGNORECASE)
    if not match:
        military_match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", message)
        if military_match:
            return f"{int(military_match.group(1)):02d}:{military_match.group(2)}"
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    meridiem = match.group(3).lower()
    if meridiem == "pm" and hour != 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


def _doctor_matches_query(doctor: DoctorResponse, message: str) -> bool:
    normalized_message = normalize_text(message)
    normalized_name = normalize_text(doctor.name)
    normalized_bare_name = normalize_text(doctor.name.removeprefix("Dr. ").removeprefix("Dr "))
    return normalized_name in normalized_message or normalized_bare_name in normalized_message


def _find_matching_doctor(message: str, doctors: list[DoctorResponse]) -> DoctorResponse | None:
    for doctor in sorted(doctors, key=lambda item: len(item.name), reverse=True):
        if _doctor_matches_query(doctor, message):
            return doctor
    return None


def _contains_doctor_reference(message: str) -> bool:
    return re.search(r"\bdr\.?\s+[A-Za-z]+(?:\s+[A-Za-z]+){0,2}\b", message, re.IGNORECASE) is not None


def _resolve_doctor_from_context(
    doctors: list[DoctorResponse],
    *,
    message: str,
    current_workflow: ChatWorkflowState | None,
    conversation_context: ChatConversationContext,
) -> tuple[int | None, str | None]:
    matched_doctor = _find_matching_doctor(message, doctors)
    if matched_doctor is not None:
        return matched_doctor.id, matched_doctor.name

    draft = current_workflow.draft if current_workflow is not None else ChatWorkflowDraft()
    if draft.doctor_id is not None or draft.doctor_name is not None:
        return draft.doctor_id, draft.doctor_name

    return conversation_context.selected_doctor_id, conversation_context.selected_doctor_name


def _missing_name_from_workflow(current_workflow: ChatWorkflowState | None) -> bool:
    return current_workflow is not None and "patient_full_name" in current_workflow.missing_fields


def _build_draft(
    message: str,
    *,
    current_workflow: ChatWorkflowState | None,
    conversation_context: ChatConversationContext,
    search_filters: ChatSearchFilters | None,
    doctors: list[DoctorResponse],
) -> ChatWorkflowDraft:
    existing = current_workflow.draft.model_copy(deep=True) if current_workflow is not None else ChatWorkflowDraft()
    doctor_id, doctor_name = _resolve_doctor_from_context(
        doctors,
        message=message,
        current_workflow=current_workflow,
        conversation_context=conversation_context,
    )

    normalized_message = normalize_text(message)
    patient_name = _extract_patient_name(message)
    if patient_name is None and _missing_name_from_workflow(current_workflow):
        patient_name = _extract_bare_patient_name(message)

    return ChatWorkflowDraft(
        doctor_id=doctor_id,
        doctor_name=doctor_name,
        appointment_date=(
            extract_target_date(normalized_message)
            or existing.appointment_date
            or (search_filters.date if search_filters is not None else None)
            or (conversation_context.active_filters.date if conversation_context.active_filters is not None else None)
        ),
        start_time=_extract_start_time(message) or existing.start_time,
        appointment_type=(
            _extract_appointment_type(normalized_message)
            or existing.appointment_type
            or AppointmentType.IN_PERSON.value
        ),
        patient_full_name=patient_name or existing.patient_full_name,
        patient_email=_extract_patient_email(message) or existing.patient_email,
        patient_phone=_extract_patient_phone(message) or existing.patient_phone,
        health_description=_extract_health_description(message) or existing.health_description,
        appointment_id=_extract_appointment_id(normalized_message) or existing.appointment_id,
        confirmation_code=_extract_confirmation_code(message) or existing.confirmation_code,
    )


def _is_help_request(normalized_message: str) -> bool:
    return _contains_keyword(normalized_message, HELP_KEYWORDS)


def _looks_like_workflow_follow_up(message: str) -> bool:
    normalized_message = normalize_text(message)
    return any(
        value is not None
        for value in (
            _extract_confirmation_code(message),
            _extract_appointment_id(normalized_message),
            _extract_patient_email(message),
            _extract_patient_phone(message),
            _extract_patient_name(message),
            _extract_bare_patient_name(message),
            _extract_start_time(message),
            extract_target_date(normalized_message),
            _extract_health_description(message),
        )
    ) or _contains_doctor_reference(message)


def _resolve_workflow_type(
    message: str,
    current_workflow: ChatWorkflowState | None,
    conversation_context: ChatConversationContext,
) -> ChatWorkflowType | None:
    normalized_message = normalize_text(message)

    if current_workflow is not None and current_workflow.status != ChatWorkflowStatus.COMPLETED:
        if any(keyword in normalized_message for keyword in WORKFLOW_SWITCH_KEYWORDS):
            return None
        if _contains_keyword(normalized_message, CANCELLATION_ACTION_KEYWORDS) and not _is_help_request(normalized_message):
            return ChatWorkflowType.CANCEL_APPOINTMENT
        if _contains_keyword(normalized_message, CONFIRMATION_ACTION_KEYWORDS) and not _is_help_request(normalized_message):
            return ChatWorkflowType.APPOINTMENT_CONFIRMATION
        if current_workflow.workflow_type == ChatWorkflowType.BOOK_APPOINTMENT:
            return current_workflow.workflow_type
        if _looks_like_workflow_follow_up(message):
            return current_workflow.workflow_type

    if _contains_keyword(normalized_message, CANCELLATION_ACTION_KEYWORDS) and not _is_help_request(normalized_message):
        return ChatWorkflowType.CANCEL_APPOINTMENT

    if _contains_keyword(normalized_message, CONFIRMATION_ACTION_KEYWORDS) and not _is_help_request(normalized_message):
        return ChatWorkflowType.APPOINTMENT_CONFIRMATION

    if _contains_keyword(normalized_message, BOOKING_ACTION_KEYWORDS) and not _is_help_request(normalized_message):
        if conversation_context.selected_doctor_id is not None or _looks_like_workflow_follow_up(message):
            return ChatWorkflowType.BOOK_APPOINTMENT

    return None


def _missing_fields_for_workflow(
    workflow_type: ChatWorkflowType,
    draft: ChatWorkflowDraft,
) -> list[str]:
    if workflow_type == ChatWorkflowType.BOOK_APPOINTMENT:
        missing_fields: list[str] = []
        if draft.doctor_id is None:
            missing_fields.append("doctor")
        if draft.appointment_date is None:
            missing_fields.append("appointment_date")
        if draft.start_time is None:
            missing_fields.append("start_time")
        if draft.patient_full_name is None:
            missing_fields.append("patient_full_name")
        if draft.patient_email is None:
            missing_fields.append("patient_email")
        return missing_fields

    if draft.appointment_id is None and draft.confirmation_code is None:
        return ["appointment_reference"]

    return []


def _build_appointment_summary(
    confirmation: AppointmentConfirmationResponse,
) -> ChatWorkflowAppointmentSummary:
    return ChatWorkflowAppointmentSummary(
        appointment_id=confirmation.id,
        confirmation_code=confirmation.confirmation_code,
        status=confirmation.status.value,
        doctor_name=confirmation.doctor.name,
        appointment_date=confirmation.appointment_date,
        start_time=confirmation.start_time,
        end_time=confirmation.end_time,
        appointment_type=confirmation.appointment_type.value,
        patient_name=confirmation.patient.full_name,
    )


def _input_required_message(workflow_type: ChatWorkflowType, missing_fields: list[str]) -> str:
    labels = ", ".join(field.replace("_", " ") for field in missing_fields)
    if workflow_type == ChatWorkflowType.BOOK_APPOINTMENT:
        return f"I can book the appointment once you share: {labels}."
    if workflow_type == ChatWorkflowType.CANCEL_APPOINTMENT:
        return "I can cancel the appointment once you share the appointment id or confirmation code."
    return "I can look up the appointment confirmation once you share the appointment id or confirmation code."


def _workflow_intent(workflow_type: ChatWorkflowType) -> ChatIntent:
    if workflow_type == ChatWorkflowType.BOOK_APPOINTMENT:
        return ChatIntent.BOOK_APPOINTMENT
    if workflow_type == ChatWorkflowType.CANCEL_APPOINTMENT:
        return ChatIntent.CANCEL_APPOINTMENT
    return ChatIntent.APPOINTMENT_CONFIRMATION


def _booking_validation_response(
    *,
    draft: ChatWorkflowDraft,
    workflow_type: ChatWorkflowType,
    search_filters: ChatSearchFilters | None,
    message: str,
    missing_fields: list[str],
) -> ChatResponse:
    workflow = ChatWorkflowResult(
        workflow_type=workflow_type,
        status=ChatWorkflowStatus.INPUT_REQUIRED,
        missing_fields=missing_fields,
        draft=draft,
    )
    return ChatResponse(
        intent=ChatIntent.BOOK_APPOINTMENT,
        message=message,
        workflow=workflow,
        search_filters=search_filters,
    )


def _booking_validation_failure_response(
    *,
    draft: ChatWorkflowDraft,
    search_filters: ChatSearchFilters | None,
    exc: Exception,
) -> ChatResponse | None:
    if isinstance(exc, ValidationError):
        missing_fields: list[str] = []
        updated_draft = draft.model_copy(deep=True)
        issues: list[str] = []

        for error in exc.errors():
            field_path = tuple(str(part) for part in error.get("loc", ()))
            if field_path in {("patient", "full_name"), ("full_name",)}:
                updated_draft.patient_full_name = None
                if "patient_full_name" not in missing_fields:
                    missing_fields.append("patient_full_name")
                issues.append("a valid patient full name")
            elif field_path in {("patient", "email"), ("email",)}:
                updated_draft.patient_email = None
                if "patient_email" not in missing_fields:
                    missing_fields.append("patient_email")
                issues.append("a valid patient email")
            elif field_path == ("start_time",):
                updated_draft.start_time = None
                if "start_time" not in missing_fields:
                    missing_fields.append("start_time")
                issues.append("a valid appointment time")

        if missing_fields:
            return _booking_validation_response(
                draft=updated_draft,
                workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
                search_filters=search_filters,
                message=(
                    "I couldn't complete the booking because I need "
                    + " and ".join(issues)
                    + "."
                ),
                missing_fields=missing_fields,
            )
        return None

    if not isinstance(exc, HTTPException):
        return None

    updated_draft = draft.model_copy(deep=True)
    detail = str(exc.detail)

    if exc.status_code == status.HTTP_404_NOT_FOUND and detail.startswith("Doctor "):
        updated_draft.doctor_id = None
        updated_draft.doctor_name = None
        return _booking_validation_response(
            draft=updated_draft,
            workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
            search_filters=search_filters,
            message="I couldn't find that doctor for booking. Please choose a valid doctor.",
            missing_fields=["doctor"],
        )

    if exc.status_code == status.HTTP_409_CONFLICT and "already booked" in detail.lower():
        updated_draft.start_time = None
        return _booking_validation_response(
            draft=updated_draft,
            workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
            search_filters=search_filters,
            message="That appointment slot is already booked. Please share another time.",
            missing_fields=["start_time"],
        )

    if exc.status_code != status.HTTP_400_BAD_REQUEST:
        return None

    normalized_detail = detail.lower()

    if "already passed" in normalized_detail:
        if updated_draft.appointment_date is not None and updated_draft.appointment_date < datetime.now().date():
            updated_draft.appointment_date = None
            return _booking_validation_response(
                draft=updated_draft,
                workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
                search_filters=search_filters,
                message="I can't book an appointment in the past. Please share a future appointment date.",
                missing_fields=["appointment_date"],
            )

        updated_draft.start_time = None
        return _booking_validation_response(
            draft=updated_draft,
            workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
            search_filters=search_filters,
            message="That appointment time has already passed. Please share another time.",
            missing_fields=["start_time"],
        )

    if "not available for the chosen date" in normalized_detail:
        updated_draft.start_time = None
        return _booking_validation_response(
            draft=updated_draft,
            workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
            search_filters=search_filters,
            message="That appointment time is not available for the selected date. Please share another time.",
            missing_fields=["start_time"],
        )

    if "appointment type is not supported" in normalized_detail:
        updated_draft.appointment_type = None
        return _booking_validation_response(
            draft=updated_draft,
            workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
            search_filters=search_filters,
            message="That appointment type is not supported for the selected doctor. Please choose another appointment type.",
            missing_fields=[],
        )

    if "patient record" in normalized_detail:
        return _booking_validation_response(
            draft=updated_draft,
            workflow_type=ChatWorkflowType.BOOK_APPOINTMENT,
            search_filters=search_filters,
            message="I couldn't complete the booking because the patient information is invalid. Please share the patient details again.",
            missing_fields=["patient_full_name", "patient_email"],
        )

    return None


class WorkflowEngine:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _list_all_doctors(self) -> list[DoctorResponse]:
        return list_doctors(self._session).items

    def handle(
        self,
        message: str,
        *,
        conversation_context: ChatConversationContext,
        search_filters: ChatSearchFilters | None = None,
        runtime_trace: AIRuntimeTraceSession | None = None,
    ) -> ChatResponse | None:
        started_at = perf_counter()
        if runtime_trace is not None:
            runtime_trace.update_stage(
                "workflow_engine",
                {
                    "entered": True,
                    "completed": False,
                },
            )

        try:
            workflow_type = _resolve_workflow_type(
                message,
                conversation_context.current_workflow,
                conversation_context,
            )
            if workflow_type is None:
                return None

            doctors = self._list_all_doctors()
            draft = _build_draft(
                message,
                current_workflow=conversation_context.current_workflow,
                conversation_context=conversation_context,
                search_filters=search_filters,
                doctors=doctors,
            )
            missing_fields = _missing_fields_for_workflow(workflow_type, draft)
            if missing_fields:
                workflow = ChatWorkflowResult(
                    workflow_type=workflow_type,
                    status=ChatWorkflowStatus.INPUT_REQUIRED,
                    missing_fields=missing_fields,
                    draft=draft,
                )
                return ChatResponse(
                    intent=_workflow_intent(workflow_type),
                    message=_input_required_message(workflow_type, missing_fields),
                    workflow=workflow,
                    search_filters=search_filters,
                )

            if workflow_type == ChatWorkflowType.BOOK_APPOINTMENT:
                try:
                    created = create_appointment_booking(
                        self._session,
                        AppointmentCreateRequest(
                            doctor_id=draft.doctor_id,
                            appointment_date=draft.appointment_date,
                            start_time=draft.start_time,
                            appointment_type=AppointmentType(
                                draft.appointment_type or AppointmentType.IN_PERSON.value
                            ),
                            patient=PatientInput(
                                full_name=draft.patient_full_name or "",
                                email=draft.patient_email or "",
                                phone=draft.patient_phone,
                            ),
                            health_description=draft.health_description,
                        ),
                    )
                except (HTTPException, ValidationError) as exc:
                    response = _booking_validation_failure_response(
                        draft=draft,
                        search_filters=search_filters,
                        exc=exc,
                    )
                    if response is not None:
                        return response
                    raise
                confirmation = get_appointment_confirmation_by_reference(
                    self._session,
                    appointment_id=created.id,
                )
                summary = _build_appointment_summary(confirmation)
                workflow = ChatWorkflowResult(
                    workflow_type=workflow_type,
                    status=ChatWorkflowStatus.COMPLETED,
                    draft=draft,
                    appointment=summary,
                )
                return ChatResponse(
                    intent=ChatIntent.BOOK_APPOINTMENT,
                    message=(
                        f"Appointment booked for {summary.doctor_name} on "
                        f"{summary.appointment_date.isoformat()} at {summary.start_time}. "
                        f"Confirmation code: {summary.confirmation_code}."
                    ),
                    workflow=workflow,
                    search_filters=search_filters,
                )

            if workflow_type == ChatWorkflowType.CANCEL_APPOINTMENT:
                confirmation = cancel_appointment_booking(
                    self._session,
                    appointment_id=draft.appointment_id,
                    confirmation_code=draft.confirmation_code,
                )
                summary = _build_appointment_summary(confirmation)
                workflow = ChatWorkflowResult(
                    workflow_type=workflow_type,
                    status=ChatWorkflowStatus.COMPLETED,
                    draft=draft,
                    appointment=summary,
                )
                return ChatResponse(
                    intent=ChatIntent.CANCEL_APPOINTMENT,
                    message=(
                        f"Appointment {summary.confirmation_code} for {summary.doctor_name} on "
                        f"{summary.appointment_date.isoformat()} at {summary.start_time} has been cancelled."
                    ),
                    workflow=workflow,
                    search_filters=search_filters,
                )

            confirmation = get_appointment_confirmation_by_reference(
                self._session,
                appointment_id=draft.appointment_id,
                confirmation_code=draft.confirmation_code,
            )
            summary = _build_appointment_summary(confirmation)
            workflow = ChatWorkflowResult(
                workflow_type=workflow_type,
                status=ChatWorkflowStatus.COMPLETED,
                draft=draft,
                appointment=summary,
            )
            status_label = summary.status.lower()
            return ChatResponse(
                intent=ChatIntent.APPOINTMENT_CONFIRMATION,
                message=(
                    f"Appointment {summary.confirmation_code} is {status_label} for "
                    f"{summary.doctor_name} on {summary.appointment_date.isoformat()} at {summary.start_time}."
                ),
                workflow=workflow,
                search_filters=search_filters,
            )
        except Exception as exc:
            if runtime_trace is not None:
                runtime_trace.record_exception("workflow_engine", exc)
            raise
        finally:
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "workflow_engine",
                    {
                        "completed": True,
                        "duration_ms": round((perf_counter() - started_at) * 1000, 3),
                    },
                )
