from __future__ import annotations

from datetime import date, datetime, time, timedelta

SLOT_START_TIMES = ("08:00", "10:00", "12:00", "14:00", "16:00", "18:00")
SLOT_DURATION_MINUTES = 30


def _build_slot_id(slot_date: date, start_time: str) -> int:
    return int(f"{slot_date:%Y%m%d}{start_time.replace(':', '')}")


def _build_slot_datetime(slot_date: date, start_time: str) -> datetime:
    return datetime.combine(slot_date, time.fromisoformat(start_time))


def format_slot_payload(
    *,
    slot_date: date,
    start_time: str,
    appointment_type: str,
    is_booked: bool,
) -> dict[str, object]:
    end_time = (
        _build_slot_datetime(slot_date, start_time)
        + timedelta(minutes=SLOT_DURATION_MINUTES)
    ).strftime("%H:%M")
    return {
        "id": _build_slot_id(slot_date, start_time),
        "available_date": slot_date.isoformat(),
        "start_time": start_time,
        "end_time": end_time,
        "appointment_type": appointment_type,
        "is_booked": is_booked,
    }


def generate_daily_slots(
    slot_date: date,
    *,
    appointment_type: str,
    booked_start_times: set[str] | None = None,
    reference_datetime: datetime | None = None,
) -> list[dict[str, object]]:
    now = reference_datetime or datetime.now()
    booked_start_times = booked_start_times or set()
    slots: list[dict[str, object]] = []

    for start_time in SLOT_START_TIMES:
        slot_datetime = _build_slot_datetime(slot_date, start_time)
        if slot_date < now.date():
            continue
        if slot_date == now.date() and slot_datetime <= now:
            continue

        slots.append(
            format_slot_payload(
                slot_date=slot_date,
                start_time=start_time,
                appointment_type=appointment_type,
                is_booked=start_time in booked_start_times,
            )
        )

    return slots


def group_slots_by_session(slots: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    morning_slots: list[dict[str, object]] = []
    afternoon_slots: list[dict[str, object]] = []

    for slot in slots:
        hour = int(str(slot["start_time"]).split(":", maxsplit=1)[0])
        if hour < 12:
            morning_slots.append(slot)
        else:
            afternoon_slots.append(slot)

    return {
        "morning_slots": morning_slots,
        "afternoon_slots": afternoon_slots,
    }
