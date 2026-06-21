from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Protocol

from sqlalchemy.orm import Session

from app.schemas.chat import (
    ChatAvailabilityCard,
    ChatDoctorCard,
    ChatIntent,
    ChatRequest,
    ChatResponse,
)
from app.schemas.doctor import DoctorResponse
from app.services.chat_intent_detector import ChatIntentMatch, detect_chat_intent
from app.services.availability_service import get_available_slots
from app.services.doctor_service import list_doctors

GREETING_KEYWORDS = ("hello", "hi", "hey")


class ChatResponder(Protocol):
    def generate(self, message: str) -> ChatResponse:
        ...


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", value.lower()).strip()


def _format_fee_range(doctor: DoctorResponse) -> str:
    if doctor.consultation_fee_min == doctor.consultation_fee_max:
        return f"${doctor.consultation_fee_min}"
    return f"${doctor.consultation_fee_min}-${doctor.consultation_fee_max}"


def _doctor_to_card(doctor: DoctorResponse) -> ChatDoctorCard:
    return ChatDoctorCard(
        doctor_id=doctor.id,
        doctor_name=doctor.name,
        specialty=doctor.specialty,
        consultation_fee_min=doctor.consultation_fee_min,
        consultation_fee_max=doctor.consultation_fee_max,
        next_available_slot=doctor.next_available_slot,
        clinic_name=doctor.clinic_name,
        location=doctor.location,
    )


def _doctor_matches_query(doctor: DoctorResponse, message: str) -> bool:
    normalized_message = _normalize_text(message)
    normalized_full_name = _normalize_text(doctor.name)
    normalized_name_without_prefix = _normalize_text(
        doctor.name.removeprefix("Dr. ").removeprefix("Dr ")
    )

    normalized_tokens = set(normalized_message.split())
    full_name_tokens = set(normalized_full_name.split())
    bare_name_tokens = set(normalized_name_without_prefix.split())

    if normalized_full_name and normalized_full_name in normalized_message:
        return True
    if normalized_name_without_prefix and normalized_name_without_prefix in normalized_message:
        return True
    if bare_name_tokens and bare_name_tokens.issubset(normalized_tokens):
        return True
    if full_name_tokens and full_name_tokens.issubset(normalized_tokens):
        return True

    return False


def _find_matching_doctor(message: str, doctors: list[DoctorResponse]) -> DoctorResponse | None:
    for doctor in sorted(doctors, key=lambda item: len(item.name), reverse=True):
        if _doctor_matches_query(doctor, message):
            return doctor
    return None


def _available_doctor_cards(
    session: Session,
    doctors: list[DoctorResponse],
    slot_date: date,
) -> list[ChatAvailabilityCard]:
    cards: list[ChatAvailabilityCard] = []
    for doctor in doctors:
        slots = get_available_slots(
            session,
            doctor.id,
            available_date=slot_date,
        )
        if not slots:
            continue

        for slot in slots:
            cards.append(
                ChatAvailabilityCard(
                    doctor_id=doctor.id,
                    doctor_name=doctor.name,
                    specialty=doctor.specialty,
                    available_date=slot_date,
                    available_time=str(slot["start_time"]),
                )
            )
    return cards


def _build_response(
    intent: ChatIntent,
    message: str,
    data: list[ChatDoctorCard | ChatAvailabilityCard] | None = None,
) -> ChatResponse:
    return ChatResponse(
        intent=intent,
        message=message,
        data=data or [],
    )


class RuleBasedChatResponder:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _list_all_doctors(self) -> list[DoctorResponse]:
        return list_doctors(self._session).items

    def _respond_with_specialties(self, specialty: str, doctors: list[DoctorResponse]) -> ChatResponse:
        if not doctors:
            return _build_response(
                ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
                f"No doctors were found for {specialty}.",
            )

        return _build_response(
            ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
            f"Found {len(doctors)} doctors for {specialty}.",
            data=[_doctor_to_card(doctor) for doctor in doctors],
        )

    def _respond_with_availability(
        self,
        message: str,
        intent_match: ChatIntentMatch,
        doctors: list[DoctorResponse],
    ) -> ChatResponse:
        matched_doctor = _find_matching_doctor(message, doctors)
        selected_doctors = [matched_doctor] if matched_doctor is not None else doctors
        if intent_match.specialty is not None:
            selected_doctors = [
                doctor for doctor in selected_doctors if doctor.specialty == intent_match.specialty
            ]

        slot_date = intent_match.target_date or (date.today() + timedelta(days=1))
        data = _available_doctor_cards(self._session, selected_doctors, slot_date)

        if not data:
            if matched_doctor is not None:
                return _build_response(
                    ChatIntent.SHOW_AVAILABLE_DOCTORS,
                    f"No open appointment slots were found for {matched_doctor.name} on {slot_date.isoformat()}.",
                )

            if intent_match.specialty is not None:
                return _build_response(
                    ChatIntent.SHOW_AVAILABLE_DOCTORS,
                    f"No {intent_match.specialty.lower()} doctors were available on {slot_date.isoformat()}.",
                )

            return _build_response(
                ChatIntent.SHOW_AVAILABLE_DOCTORS,
                f"No doctors were available on {slot_date.isoformat()}.",
            )

        if matched_doctor is not None:
            return _build_response(
                ChatIntent.SHOW_AVAILABLE_DOCTORS,
                f"Found {len(data)} available slots for {matched_doctor.name} on {slot_date.isoformat()}.",
                data=data,
            )

        if intent_match.specialty is not None:
            return _build_response(
                ChatIntent.SHOW_AVAILABLE_DOCTORS,
                f"Found {len(data)} {intent_match.specialty.lower()} doctors available on {slot_date.isoformat()}.",
                data=data,
            )

        return _build_response(
            ChatIntent.SHOW_AVAILABLE_DOCTORS,
            f"Found {len(data)} doctors available on {slot_date.isoformat()}.",
            data=data,
        )

    def _respond_with_doctor_details(self, message: str, doctors: list[DoctorResponse]) -> ChatResponse:
        doctor = _find_matching_doctor(message, doctors)
        if doctor is None:
            return _build_response(
                ChatIntent.SHOW_DOCTOR_DETAILS,
                "Please mention the doctor's name to check the consultation fee.",
            )

        return _build_response(
            ChatIntent.SHOW_DOCTOR_DETAILS,
            (
                f"{doctor.name} consultation fee is {_format_fee_range(doctor)}. "
                f"Next available slot: {doctor.next_available_slot}."
            ),
            data=[_doctor_to_card(doctor)],
        )

    def _respond_with_appointment_help(self) -> ChatResponse:
        return _build_response(
            ChatIntent.APPOINTMENT_HELP,
            "I can help you book an appointment. Share a doctor, preferred date, time, and appointment type.",
        )

    def _respond_with_greeting(self) -> ChatResponse:
        return _build_response(
            ChatIntent.UNKNOWN,
            "Hello, I am your AI Assistant.",
        )

    def _respond_with_unknown(self) -> ChatResponse:
        return _build_response(
            ChatIntent.UNKNOWN,
            "I can help with available doctors, specializations, consultation fees, and appointment slots.",
        )

    def _respond_with_specialty_overview(self) -> ChatResponse:
        specialties = sorted({doctor.specialty for doctor in self._list_all_doctors()})
        return _build_response(
            ChatIntent.UNKNOWN,
            "Available specializations: " + ", ".join(specialties) + ".",
        )

    def generate(self, message: str) -> ChatResponse:
        intent_match = detect_chat_intent(message)
        doctors = self._list_all_doctors()

        normalized_message = _normalize_text(message)
        if any(keyword in normalized_message for keyword in GREETING_KEYWORDS):
            return self._respond_with_greeting()

        if any(keyword in normalized_message for keyword in ("specialization", "specializations", "specialty", "specialties")):
            return self._respond_with_specialty_overview()

        if intent_match.intent == ChatIntent.APPOINTMENT_HELP:
            return self._respond_with_appointment_help()

        if intent_match.intent == ChatIntent.SHOW_AVAILABLE_DOCTORS:
            return self._respond_with_availability(message, intent_match, doctors)

        if intent_match.intent == ChatIntent.SHOW_DOCTOR_DETAILS:
            return self._respond_with_doctor_details(message, doctors)

        if intent_match.intent == ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION and intent_match.specialty is not None:
            specialty_doctors = [
                doctor for doctor in doctors if doctor.specialty == intent_match.specialty
            ]
            return self._respond_with_specialties(intent_match.specialty, specialty_doctors)

        if "show doctors" in normalized_message or "find doctors" in normalized_message or "find doctor" in normalized_message:
            fallback_match = ChatIntentMatch(
                intent=ChatIntent.SHOW_AVAILABLE_DOCTORS,
                target_date=date.today() + timedelta(days=1),
            )
            return self._respond_with_availability(message, fallback_match, doctors)

        return self._respond_with_unknown()


def create_chat_response(
    session: Session,
    request: ChatRequest,
    responder: ChatResponder | None = None,
) -> ChatResponse:
    chat_responder = responder or RuleBasedChatResponder(session)
    return chat_responder.generate(request.message)
