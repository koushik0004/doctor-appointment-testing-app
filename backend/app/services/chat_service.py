from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Protocol

from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.doctor import DoctorResponse
from app.services.availability_service import get_available_slots
from app.services.doctor_service import list_doctors


class ChatResponder(Protocol):
    def generate(self, message: str) -> str:
        ...


SPECIALTY_ALIASES = {
    "cardiologist": "Cardiology",
    "cardiologists": "Cardiology",
    "cardiology": "Cardiology",
    "dermatologist": "Dermatology",
    "dermatologists": "Dermatology",
    "dermatology": "Dermatology",
    "pediatrician": "Pediatrics",
    "pediatricians": "Pediatrics",
    "pediatrics": "Pediatrics",
    "general practitioner": "General Practice",
    "general practitioners": "General Practice",
    "general practice": "General Practice",
    "gp": "General Practice",
    "internal medicine": "Internal Medicine",
    "internist": "Internal Medicine",
    "internists": "Internal Medicine",
}


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", value.lower()).strip()


def _format_fee_range(doctor: DoctorResponse) -> str:
    if doctor.consultation_fee_min == doctor.consultation_fee_max:
        return f"${doctor.consultation_fee_min}"
    return f"${doctor.consultation_fee_min}-${doctor.consultation_fee_max}"


def _format_doctor_summary(doctor: DoctorResponse) -> str:
    return (
        f"{doctor.name} ({doctor.specialty}) - fee {_format_fee_range(doctor)}, "
        f"next available {doctor.next_available_slot}"
    )


class RuleBasedChatResponder:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._reply_rules: tuple[tuple[tuple[str, ...], str], ...] = (
            (("hello", "hi", "hey"), "Hello, I am your AI Assistant."),
            (
                ("book", "appointment"),
                "I can help you book an appointment with an available doctor.",
            ),
        )

    def _list_all_doctors(self) -> list[DoctorResponse]:
        return list_doctors(self._session).items

    def _extract_specialty(self, message: str, doctors: list[DoctorResponse]) -> str | None:
        normalized_message = _normalize_text(message)
        for alias, specialty in SPECIALTY_ALIASES.items():
            if alias in normalized_message:
                return specialty

        for doctor in doctors:
            if doctor.specialty.lower() in normalized_message:
                return doctor.specialty

        return None

    def _extract_doctor(self, message: str, doctors: list[DoctorResponse]) -> DoctorResponse | None:
        normalized_message = _normalize_text(message)
        normalized_tokens = set(normalized_message.split())

        for doctor in sorted(doctors, key=lambda item: len(item.name), reverse=True):
            full_name = _normalize_text(doctor.name)
            name_without_prefix = _normalize_text(doctor.name.removeprefix("Dr. "))
            full_name_tokens = set(full_name.split())
            bare_name_tokens = set(name_without_prefix.split())

            if full_name and full_name in normalized_message:
                return doctor
            if name_without_prefix and name_without_prefix in normalized_message:
                return doctor
            if bare_name_tokens and bare_name_tokens.issubset(normalized_tokens):
                return doctor
            if full_name_tokens and full_name_tokens.issubset(normalized_tokens):
                return doctor

        return None

    def _respond_with_specialties(self, doctors: list[DoctorResponse]) -> str:
        specialties = sorted({doctor.specialty for doctor in doctors})
        return "Available specializations: " + ", ".join(specialties) + "."

    def _respond_with_doctors(self, doctors: list[DoctorResponse], specialty: str | None = None) -> str:
        if not doctors:
            if specialty:
                return f"No available doctors were found for {specialty}."
            return "No available doctors were found."

        intro = (
            f"Available {specialty} doctors: "
            if specialty
            else "Available doctors: "
        )
        return intro + "; ".join(_format_doctor_summary(doctor) for doctor in doctors[:5]) + "."

    def _respond_with_fee(self, doctor: DoctorResponse | None) -> str:
        if not doctor:
            return "Please mention the doctor's name to check the consultation fee."
        return f"{doctor.name} charges {_format_fee_range(doctor)} for a consultation."

    def _respond_with_slots(self, doctor: DoctorResponse | None) -> str:
        if not doctor:
            doctors = self._list_all_doctors()[:5]
            return "Next available appointment slots: " + "; ".join(
                f"{item.name}: {item.next_available_slot}" for item in doctors
            ) + "."

        slot_date = date.today() + timedelta(days=1)
        slots = get_available_slots(
            self._session,
            doctor.id,
            available_date=slot_date,
        )
        if not slots:
            return f"No open appointment slots were found for {doctor.name} on {slot_date.isoformat()}."

        slot_times = ", ".join(slot["start_time"] for slot in slots[:5])
        return (
            f"Available appointment slots for {doctor.name} on {slot_date.isoformat()}: "
            f"{slot_times}."
        )

    def generate(self, message: str) -> str:
        normalized_message = message.strip().lower()

        for keywords, reply in self._reply_rules:
            if any(keyword in normalized_message for keyword in keywords):
                return reply

        doctors = self._list_all_doctors()
        specialty = self._extract_specialty(message, doctors)
        doctor = self._extract_doctor(message, doctors)

        if any(keyword in normalized_message for keyword in ("specialization", "specializations", "specialty", "specialties")):
            return self._respond_with_specialties(doctors)

        if any(keyword in normalized_message for keyword in ("fee", "fees", "consultation cost", "consultation fee", "price", "cost")):
            return self._respond_with_fee(doctor)

        if any(keyword in normalized_message for keyword in ("slot", "slots", "schedule", "available time", "appointment time")):
            return self._respond_with_slots(doctor)

        if specialty:
            matching_doctors = [item for item in doctors if item.specialty == specialty]
            return self._respond_with_doctors(matching_doctors, specialty=specialty)

        if "available doctors" in normalized_message or "show doctors" in normalized_message:
            return self._respond_with_doctors(doctors)

        return "I can help with available doctors, specializations, consultation fees, and appointment slots."


def create_chat_response(
    session: Session,
    request: ChatRequest,
    responder: ChatResponder | None = None,
) -> ChatResponse:
    chat_responder = responder or RuleBasedChatResponder(session)
    return ChatResponse(response=chat_responder.generate(request.message))
