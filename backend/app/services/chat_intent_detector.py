from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.schemas.chat import ChatIntent
from app.services.chat_entity_extractor import extract_specialization, extract_target_date, normalize_text

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


def _contains_keyword(normalized_message: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in normalized_message for keyword in keywords)


def detect_chat_intent(message: str) -> ChatIntentMatch:
    normalized_message = normalize_text(message)
    specialty = extract_specialization(normalized_message)
    target_date = extract_target_date(normalized_message)

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
