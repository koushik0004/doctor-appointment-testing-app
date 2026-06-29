from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Protocol

from sqlalchemy.orm import Session

from app.schemas.chat import (
    ChatAvailabilityCard,
    ChatConversationContext,
    ChatDoctorCard,
    ChatIntent,
    ChatRequest,
    ChatResponse,
    ChatSearchFilters,
)
from app.schemas.doctor import DoctorResponse
from app.services.availability_service import get_available_slots
from app.services.chat_entity_extractor import extract_chat_search_filters, normalize_text
from app.services.chat_intent_detector import ChatIntentMatch, detect_chat_intent
from app.services.doctor_service import list_doctors

GREETING_KEYWORDS = ("hello", "hi", "hey")
EXPLICIT_DOCTOR_DETAIL_KEYWORDS = (
    "consultation fee",
    "consultation fees",
    "consultation charges",
    "doctor charges",
    "doctor fee",
    "doctor fees",
    "fee",
    "fees",
    "price",
    "prices",
    "cost",
    "costs",
    "profile",
)


def _extract_doctor_name_fragments(normalized_message: str) -> list[set[str]]:
    fragments: list[set[str]] = []
    for match in re.finditer(r"\bdr\s+([a-z]+(?:\s+[a-z]+){0,2})\b", normalized_message):
        tokens = {token for token in match.group(1).split() if token}
        if tokens:
            fragments.append(tokens)
    return fragments


class ChatResponder(Protocol):
    def generate(
        self,
        message: str,
        *,
        intent_match: ChatIntentMatch | None = None,
        search_filters: ChatSearchFilters | None = None,
        selected_doctor_name: str | None = None,
        conversation_context: ChatConversationContext | None = None,
    ) -> ChatResponse:
        ...


def _format_fee_range(doctor: DoctorResponse) -> str:
    if doctor.consultation_fee_min == doctor.consultation_fee_max:
        return f"${doctor.consultation_fee_min}"
    return f"${doctor.consultation_fee_min}-${doctor.consultation_fee_max}"


def _doctor_to_card(doctor: DoctorResponse) -> ChatDoctorCard:
    return ChatDoctorCard(
        doctor_id=doctor.id,
        doctor_name=doctor.name,
        specialty=doctor.specialty,
        gender=doctor.gender or "Unspecified",
        consultation_fee_min=doctor.consultation_fee_min,
        consultation_fee_max=doctor.consultation_fee_max,
        next_available_slot=doctor.next_available_slot,
        clinic_name=doctor.clinic_name,
        location=doctor.location,
    )


def _doctor_matches_query(doctor: DoctorResponse, message: str) -> bool:
    normalized_message = normalize_text(message)
    normalized_full_name = normalize_text(doctor.name)
    normalized_name_without_prefix = normalize_text(
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
    for fragment_tokens in _extract_doctor_name_fragments(normalized_message):
        if fragment_tokens.issubset(bare_name_tokens) or fragment_tokens.issubset(full_name_tokens):
            return True

    return False


def _find_matching_doctor(message: str, doctors: list[DoctorResponse]) -> DoctorResponse | None:
    for doctor in sorted(doctors, key=lambda item: len(item.name), reverse=True):
        if _doctor_matches_query(doctor, message):
            return doctor
    return None


def _has_explicit_doctor_detail_keyword(normalized_message: str) -> bool:
    return any(keyword in normalized_message for keyword in EXPLICIT_DOCTOR_DETAIL_KEYWORDS)


def _describe_search_filters(search_filters: ChatSearchFilters) -> str:
    parts: list[str] = []
    if search_filters.specialization:
        parts.append(search_filters.specialization)
    if search_filters.gender:
        parts.append(search_filters.gender)
    if search_filters.minimum_fee is not None and search_filters.maximum_fee is not None:
        parts.append(f"between ${search_filters.minimum_fee} and ${search_filters.maximum_fee}")
    elif search_filters.minimum_fee is not None:
        parts.append(f"from ${search_filters.minimum_fee}")
    elif search_filters.maximum_fee is not None:
        parts.append(f"under ${search_filters.maximum_fee}")
    if search_filters.clinic_location:
        parts.append(f"in {search_filters.clinic_location}")
    if search_filters.date:
        parts.append(search_filters.date.isoformat())
    if search_filters.time_preference:
        parts.append(search_filters.time_preference)
    return ", ".join(parts)


def _doctor_matches_filters(doctor: DoctorResponse, search_filters: ChatSearchFilters) -> bool:
    if search_filters.specialization and doctor.specialty != search_filters.specialization:
        return False
    if search_filters.gender and doctor.gender != search_filters.gender:
        return False
    if search_filters.clinic_location:
        location_value = search_filters.clinic_location.lower()
        if location_value not in doctor.location.lower() and location_value not in doctor.clinic_name.lower():
            return False
    if search_filters.minimum_fee is not None and search_filters.maximum_fee is not None:
        if doctor.consultation_fee_max < search_filters.minimum_fee:
            return False
        if doctor.consultation_fee_min > search_filters.maximum_fee:
            return False
    elif search_filters.minimum_fee is not None:
        if doctor.consultation_fee_min < search_filters.minimum_fee:
            return False
    elif search_filters.maximum_fee is not None:
        if doctor.consultation_fee_max > search_filters.maximum_fee:
            return False
    return True


def _filter_doctors(doctors: list[DoctorResponse], search_filters: ChatSearchFilters) -> list[DoctorResponse]:
    return [doctor for doctor in doctors if _doctor_matches_filters(doctor, search_filters)]


def _parse_time_value(value: str) -> time | None:
    match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", value.lower())
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    meridiem = match.group(3)

    if meridiem == "pm" and hour != 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    return time(hour=hour, minute=minute)


def _time_in_preference_window(slot_time: str, time_preference: str | None) -> bool:
    if not time_preference:
        return True

    parsed_slot_time = datetime.strptime(slot_time, "%H:%M").time()
    normalized = time_preference.lower()

    if normalized == "morning":
        return time(6, 0) <= parsed_slot_time < time(12, 0)
    if normalized == "afternoon":
        return time(12, 0) <= parsed_slot_time < time(17, 0)
    if normalized == "evening":
        return time(17, 0) <= parsed_slot_time < time(21, 0)
    if normalized == "night":
        return time(21, 0) <= parsed_slot_time <= time(23, 59)

    after_match = re.match(r"^after\s+(.+)$", normalized)
    if after_match:
        threshold = _parse_time_value(after_match.group(1))
        if threshold:
            return parsed_slot_time >= threshold
        return True

    before_match = re.match(r"^before\s+(.+)$", normalized)
    if before_match:
        threshold = _parse_time_value(before_match.group(1))
        if threshold:
            return parsed_slot_time <= threshold
        return True

    between_match = re.match(r"^between\s+(.+)\s+and\s+(.+)$", normalized)
    if between_match:
        start = _parse_time_value(between_match.group(1))
        end = _parse_time_value(between_match.group(2))
        if start and end:
            return start <= parsed_slot_time <= end
        return True

    exact_time = _parse_time_value(normalized)
    if exact_time:
        return parsed_slot_time == exact_time

    return True


def _available_doctor_cards(
    session: Session,
    doctors: list[DoctorResponse],
    slot_date: date,
    time_preference: str | None = None,
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
            slot_time = str(slot["start_time"])
            if not _time_in_preference_window(slot_time, time_preference):
                continue
            cards.append(
                ChatAvailabilityCard(
                    doctor_id=doctor.id,
                    doctor_name=doctor.name,
                    specialty=doctor.specialty,
                    available_date=slot_date,
                    available_time=slot_time,
                )
            )
    return cards


def _build_response(
    intent: ChatIntent,
    message: str,
    data: list[ChatDoctorCard | ChatAvailabilityCard] | None = None,
    search_filters: ChatSearchFilters | None = None,
    help_steps: list[str] | None = None,
) -> ChatResponse:
    return ChatResponse(
        intent=intent,
        message=message,
        data=data or [],
        search_filters=search_filters,
        help_steps=help_steps or [],
    )


class RuleBasedChatResponder:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _list_all_doctors(self) -> list[DoctorResponse]:
        return list_doctors(self._session).items

    def _respond_with_specialties(
        self,
        specialty: str,
        doctors: list[DoctorResponse],
        search_filters: ChatSearchFilters | None = None,
    ) -> ChatResponse:
        if not doctors:
            return _build_response(
                ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
                f"No doctors were found for {specialty}.",
                search_filters=search_filters,
            )

        return _build_response(
            ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
            f"Found {len(doctors)} doctors for {specialty}.",
            data=[_doctor_to_card(doctor) for doctor in doctors],
            search_filters=search_filters,
        )

    def _respond_with_availability(
        self,
        message: str,
        intent_match: ChatIntentMatch,
        search_filters: ChatSearchFilters,
        doctors: list[DoctorResponse],
        selected_doctor_name: str | None = None,
    ) -> ChatResponse:
        selected_doctors = _filter_doctors(doctors, search_filters)
        matched_doctor = _find_matching_doctor(message, selected_doctors)
        if matched_doctor is None and selected_doctor_name:
            matched_doctor = _find_matching_doctor(selected_doctor_name, selected_doctors) or _find_matching_doctor(
                selected_doctor_name,
                doctors,
            )
        if matched_doctor is None and len(selected_doctors) == 1:
            matched_doctor = selected_doctors[0]
        slot_doctors = [matched_doctor] if matched_doctor is not None else selected_doctors

        slot_date = intent_match.target_date or search_filters.date or (date.today() + timedelta(days=1))
        data = _available_doctor_cards(
            self._session,
            slot_doctors,
            slot_date,
            time_preference=search_filters.time_preference,
        )

        if not data:
            if matched_doctor is not None:
                return _build_response(
                    ChatIntent.SHOW_AVAILABLE_DOCTORS,
                    f"No open appointment slots were found for {matched_doctor.name} on {slot_date.isoformat()}.",
                    search_filters=search_filters,
                )

            if search_filters.specialization is not None:
                return _build_response(
                    ChatIntent.SHOW_AVAILABLE_DOCTORS,
                    f"No {search_filters.specialization.lower()} doctors were available on {slot_date.isoformat()}.",
                    search_filters=search_filters,
                )

            return _build_response(
                ChatIntent.SHOW_AVAILABLE_DOCTORS,
                f"No doctors were available on {slot_date.isoformat()}.",
                search_filters=search_filters,
            )

        if matched_doctor is not None:
            return _build_response(
                ChatIntent.SHOW_AVAILABLE_DOCTORS,
                f"Found {len(data)} available slots for {matched_doctor.name} on {slot_date.isoformat()}.",
                data=data,
                search_filters=search_filters,
            )

        if search_filters.specialization is not None:
            return _build_response(
                ChatIntent.SHOW_AVAILABLE_DOCTORS,
                f"Found {len(data)} {search_filters.specialization.lower()} doctors available on {slot_date.isoformat()}.",
                data=data,
                search_filters=search_filters,
            )

        return _build_response(
            ChatIntent.SHOW_AVAILABLE_DOCTORS,
            f"Found {len(data)} doctors available on {slot_date.isoformat()}.",
            data=data,
            search_filters=search_filters,
        )

    def _respond_with_doctor_details(
        self,
        message: str,
        search_filters: ChatSearchFilters,
        doctors: list[DoctorResponse],
        selected_doctor_name: str | None = None,
    ) -> ChatResponse:
        candidate_doctors = _filter_doctors(doctors, search_filters)
        doctor = _find_matching_doctor(message, candidate_doctors) or _find_matching_doctor(message, doctors)
        if doctor is None and selected_doctor_name:
            doctor = _find_matching_doctor(selected_doctor_name, candidate_doctors) or _find_matching_doctor(
                selected_doctor_name,
                doctors,
            )
        if doctor is None:
            return _build_response(
                ChatIntent.SHOW_DOCTOR_DETAILS,
                "Which doctor's consultation fee would you like to know?",
                search_filters=search_filters,
            )

        return _build_response(
            ChatIntent.SHOW_DOCTOR_DETAILS,
            (
                f"{doctor.name} consultation fee is {_format_fee_range(doctor)}. "
                f"Next available slot: {doctor.next_available_slot}."
            ),
            data=[_doctor_to_card(doctor)],
            search_filters=search_filters,
        )

    def _respond_with_appointment_help(self, search_filters: ChatSearchFilters | None = None) -> ChatResponse:
        return _build_response(
            ChatIntent.APPOINTMENT_HELP,
            "Here is how to book an appointment in the app.",
            search_filters=search_filters,
            help_steps=[
                "Choose a doctor.",
                "Select an available date.",
                "Choose a time slot.",
                "Enter patient details.",
                "Confirm the appointment.",
            ],
        )

    def _respond_with_cancellation_help(
        self,
        search_filters: ChatSearchFilters | None = None,
    ) -> ChatResponse:
        return _build_response(
            ChatIntent.CANCEL_APPOINTMENT_HELP,
            "Appointment cancellation is not supported through AI chat. Please use the app's existing cancellation flow or contact support for help.",
            search_filters=search_filters,
            help_steps=[
                "Open the existing cancellation flow in the app.",
                "Find your booked appointment details.",
                "Follow the cancellation instructions shown there.",
                "If you cannot access the booking, contact support.",
            ],
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

    def generate(
        self,
        message: str,
        *,
        intent_match: ChatIntentMatch | None = None,
        search_filters: ChatSearchFilters | None = None,
        selected_doctor_name: str | None = None,
        conversation_context: ChatConversationContext | None = None,
    ) -> ChatResponse:
        del conversation_context

        resolved_intent_match = intent_match or detect_chat_intent(message)
        doctors = self._list_all_doctors()
        resolved_search_filters = search_filters or extract_chat_search_filters(message)

        normalized_message = normalize_text(message)
        if any(keyword in normalized_message for keyword in GREETING_KEYWORDS):
            return self._respond_with_greeting()

        if any(keyword in normalized_message for keyword in ("specialization", "specializations", "specialty", "specialties")):
            return self._respond_with_specialty_overview()

        if resolved_intent_match.intent == ChatIntent.APPOINTMENT_HELP:
            return self._respond_with_appointment_help(resolved_search_filters)

        if resolved_intent_match.intent == ChatIntent.CANCEL_APPOINTMENT_HELP:
            return self._respond_with_cancellation_help(resolved_search_filters)

        if (
            resolved_intent_match.intent == ChatIntent.SHOW_DOCTOR_DETAILS
            and (
                _has_explicit_doctor_detail_keyword(normalized_message)
                or selected_doctor_name is not None
                or _find_matching_doctor(message, doctors) is not None
            )
        ):
            return self._respond_with_doctor_details(
                message,
                resolved_search_filters,
                doctors,
                selected_doctor_name=selected_doctor_name,
            )

        if (
            resolved_intent_match.intent == ChatIntent.SHOW_AVAILABLE_DOCTORS
            or resolved_search_filters.date is not None
            or resolved_search_filters.time_preference is not None
        ):
            return self._respond_with_availability(
                message,
                resolved_intent_match,
                resolved_search_filters,
                doctors,
                selected_doctor_name=selected_doctor_name,
            )

        if (
            resolved_intent_match.intent == ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION
            and (
                resolved_intent_match.specialty is not None
                or resolved_search_filters.specialization is not None
            )
        ):
            specialty = resolved_intent_match.specialty or resolved_search_filters.specialization
            specialty_doctors = [
                doctor for doctor in doctors if doctor.specialty == specialty
            ]
            specialty_doctors = _filter_doctors(specialty_doctors, resolved_search_filters)
            return self._respond_with_specialties(specialty or "", specialty_doctors, resolved_search_filters)

        if any(
            keyword in normalized_message
            for keyword in ("show doctors", "find doctors", "find doctor", "doctor search", "search doctors")
        ) or any(
            value is not None
            for value in (
                resolved_search_filters.specialization,
                resolved_search_filters.gender,
                resolved_search_filters.minimum_fee,
                resolved_search_filters.maximum_fee,
                resolved_search_filters.clinic_location,
            )
        ):
            matching_doctors = _filter_doctors(doctors, resolved_search_filters)
            filter_summary = _describe_search_filters(resolved_search_filters)
            if matching_doctors:
                message_text = f"Found {len(matching_doctors)} matching doctors."
                if filter_summary:
                    message_text = f"Found {len(matching_doctors)} matching doctors for {filter_summary}."
                return _build_response(
                    ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
                    message_text,
                    data=[_doctor_to_card(doctor) for doctor in matching_doctors],
                    search_filters=resolved_search_filters,
                )

            if filter_summary:
                return _build_response(
                    ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
                    f"No matching doctors were found for {filter_summary}.",
                    search_filters=resolved_search_filters,
                )

            return _build_response(
                ChatIntent.SHOW_DOCTORS_BY_SPECIALIZATION,
                "I can help you search for doctors by specialization, location, fee, or availability.",
                search_filters=resolved_search_filters,
            )

        return self._respond_with_unknown()


def create_chat_response(
    session: Session,
    request: ChatRequest,
    responder: ChatResponder | None = None,
) -> ChatResponse:
    from app.services.conversation_manager import ConversationManager

    chat_responder = responder or RuleBasedChatResponder(session)
    manager = ConversationManager(
        session,
        deterministic_engine=chat_responder,
    )
    return manager.handle(request)
