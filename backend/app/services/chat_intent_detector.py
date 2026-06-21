from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta

from app.schemas.chat import ChatIntent


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

APPOINTMENT_HELP_KEYWORDS = (
    "book",
    "booking",
    "appointment",
    "appointments",
    "schedule",
    "reschedule",
    "cancel",
)

AVAILABILITY_KEYWORDS = (
    "available doctor",
    "available doctors",
    "available",
    "availability",
    "slot",
    "slots",
    "open slots",
    "open time",
    "open times",
    "who is free",
    "who's free",
)

DOCTOR_DETAILS_KEYWORDS = (
    "consultation fee",
    "consultation fees",
    "fee",
    "fees",
    "price",
    "prices",
    "cost",
    "costs",
    "details",
    "detail",
    "about",
)


@dataclass(frozen=True)
class ChatIntentMatch:
    intent: ChatIntent
    specialty: str | None = None
    target_date: date | None = None


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", value.lower()).strip()


def _extract_specialty(normalized_message: str) -> str | None:
    for alias, specialty in SPECIALTY_ALIASES.items():
        if alias in normalized_message:
            return specialty
    return None


def _extract_target_date(normalized_message: str) -> date | None:
    today = date.today()
    if "day after tomorrow" in normalized_message:
        return today + timedelta(days=2)
    if "tomorrow" in normalized_message:
        return today + timedelta(days=1)
    if "today" in normalized_message:
        return today
    return None


def _contains_keyword(normalized_message: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in normalized_message for keyword in keywords)


def detect_chat_intent(message: str) -> ChatIntentMatch:
    normalized_message = _normalize_text(message)
    specialty = _extract_specialty(normalized_message)
    target_date = _extract_target_date(normalized_message)

    if _contains_keyword(normalized_message, APPOINTMENT_HELP_KEYWORDS):
        return ChatIntentMatch(
            intent=ChatIntent.APPOINTMENT_HELP,
            specialty=specialty,
            target_date=target_date,
        )

    if _contains_keyword(normalized_message, AVAILABILITY_KEYWORDS):
        return ChatIntentMatch(
            intent=ChatIntent.SHOW_AVAILABLE_DOCTORS,
            specialty=specialty,
            target_date=target_date or (date.today() + timedelta(days=1)),
        )

    if _contains_keyword(normalized_message, DOCTOR_DETAILS_KEYWORDS):
        return ChatIntentMatch(
            intent=ChatIntent.SHOW_DOCTOR_DETAILS,
            specialty=specialty,
            target_date=target_date,
        )

    if specialty is not None:
        return ChatIntentMatch(
            intent=ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
            specialty=specialty,
            target_date=target_date,
        )

    return ChatIntentMatch(intent=ChatIntent.UNKNOWN)
