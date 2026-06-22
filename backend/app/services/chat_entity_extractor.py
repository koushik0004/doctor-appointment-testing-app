from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from app.schemas.chat import ChatSearchFilters

SPECIALTY_ALIASES = {
    "cardiologist": "Cardiology",
    "cardiologists": "Cardiology",
    "cardiology": "Cardiology",
    "dermatologist": "Dermatology",
    "dermatologists": "Dermatology",
    "dermatology": "Dermatology",
    "neurologist": "Neurology",
    "neurologists": "Neurology",
    "neurology": "Neurology",
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

_TIME_OF_DAY_WINDOWS = {
    "morning": "Morning",
    "afternoon": "Afternoon",
    "evening": "Evening",
    "night": "Night",
}

_WEEKDAY_TO_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", value.lower()).strip()


def _title_phrase(value: str) -> str:
    titled = " ".join(part.capitalize() for part in value.split())
    return titled.replace("Uk", "UK").replace("Usa", "USA")


def extract_specialization(normalized_message: str) -> str | None:
    for alias, specialty in SPECIALTY_ALIASES.items():
        if alias in normalized_message:
            return specialty
    return None


def extract_gender(normalized_message: str) -> str | None:
    if any(keyword in normalized_message for keyword in ("female", "woman", "women", "lady")):
        return "Female"
    if any(keyword in normalized_message for keyword in ("male", "man", "men", "gentleman")):
        return "Male"
    return None


def extract_fee_range(normalized_message: str) -> tuple[int | None, int | None]:
    between_match = re.search(
        r"(?:between|from)\s*(?:rs\.?|inr|₹|\$)?\s*(\d+)\s*(?:and|to|-)\s*(?:rs\.?|inr|₹|\$)?\s*(\d+)",
        normalized_message,
    )
    if between_match:
        minimum_fee = int(between_match.group(1))
        maximum_fee = int(between_match.group(2))
        if minimum_fee > maximum_fee:
            minimum_fee, maximum_fee = maximum_fee, minimum_fee
        return minimum_fee, maximum_fee

    range_match = re.search(r"(?:rs\.?|inr|₹|\$)?\s*(\d+)\s*-\s*(?:rs\.?|inr|₹|\$)?\s*(\d+)", normalized_message)
    if range_match:
        minimum_fee = int(range_match.group(1))
        maximum_fee = int(range_match.group(2))
        if minimum_fee > maximum_fee:
            minimum_fee, maximum_fee = maximum_fee, minimum_fee
        return minimum_fee, maximum_fee

    lower_match = re.search(
        r"(?:under|below|less than|up to|max(?:imum)?(?: fee)?)\s*(?:rs\.?|inr|₹|\$)?\s*(\d+)",
        normalized_message,
    )
    if lower_match:
        return None, int(lower_match.group(1))

    upper_match = re.search(
        r"(?:over|above|more than|min(?:imum)?(?: fee)?)\s*(?:rs\.?|inr|₹|\$)?\s*(\d+)",
        normalized_message,
    )
    if upper_match:
        return int(upper_match.group(1)), None

    return None, None


def extract_target_date(normalized_message: str) -> date | None:
    today = date.today()
    if "day after tomorrow" in normalized_message:
        return today + timedelta(days=2)
    if "tomorrow" in normalized_message:
        return today + timedelta(days=1)
    if "today" in normalized_message:
        return today

    for weekday_name, weekday_index in _WEEKDAY_TO_INDEX.items():
        if weekday_name not in normalized_message:
            continue

        days_until_weekday = (weekday_index - today.weekday()) % 7
        if days_until_weekday == 0 and "next" in normalized_message:
            days_until_weekday = 7
        elif days_until_weekday == 0:
            days_until_weekday = 7
        return today + timedelta(days=days_until_weekday)

    return None


def _parse_explicit_time(value: str) -> str | None:
    time_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", value)
    if not time_match:
        return None

    hour = int(time_match.group(1))
    minute = int(time_match.group(2) or "0")
    meridiem = time_match.group(3).upper()

    if meridiem == "PM" and hour != 12:
        hour += 12
    if meridiem == "AM" and hour == 12:
        hour = 0

    parsed_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").strftime("%I:%M %p")
    return parsed_time.lstrip("0")


def extract_time_preference(normalized_message: str) -> str | None:
    for keyword, label in _TIME_OF_DAY_WINDOWS.items():
        if keyword in normalized_message:
            return label

    between_match = re.search(r"between\s+(.+?)\s+(?:and|to|-)\s+(.+)", normalized_message)
    if between_match:
        start = _parse_explicit_time(between_match.group(1))
        end = _parse_explicit_time(between_match.group(2))
        if start and end:
            return f"Between {start} and {end}"

    after_match = re.search(r"(?:after|from|later than|since)\s+(.+)", normalized_message)
    if after_match:
        time_value = _parse_explicit_time(after_match.group(1))
        if time_value:
            return f"After {time_value}"

    before_match = re.search(r"(?:before|until|up to|by)\s+(.+)", normalized_message)
    if before_match:
        time_value = _parse_explicit_time(before_match.group(1))
        if time_value:
            return f"Before {time_value}"

    explicit_time = _parse_explicit_time(normalized_message)
    if explicit_time:
        return explicit_time

    return None


def extract_clinic_location(normalized_message: str) -> str | None:
    location_match = re.search(
        r"\b(?:near|in|at|around)\b\s+([a-z0-9&'\- ]+?)(?:\s+(?:clinic|hospital|center|centre|medical|practice|hub|institute|facility))?(?:$|[?.!,])",
        normalized_message,
    )
    if not location_match:
        return None

    location = location_match.group(1).strip()
    if not location:
        return None
    return _title_phrase(location)


def extract_chat_search_filters(message: str) -> ChatSearchFilters:
    normalized_message = normalize_text(message)
    minimum_fee, maximum_fee = extract_fee_range(normalized_message)

    return ChatSearchFilters(
        specialization=extract_specialization(normalized_message),
        gender=extract_gender(normalized_message),
        minimum_fee=minimum_fee,
        maximum_fee=maximum_fee,
        date=extract_target_date(normalized_message),
        time_preference=extract_time_preference(normalized_message),
        clinic_location=extract_clinic_location(normalized_message),
    )
