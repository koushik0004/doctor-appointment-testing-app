from datetime import date

from sqlalchemy.orm import Session

from app.repositories.availability_repository import (
    get_available_dates as get_available_dates_for_doctor,
    get_available_slots as get_available_slots_for_doctor,
    mark_slot_booked as mark_availability_slot_booked,
)
from app.schemas.doctor import DoctorResponse
from app.services.doctor_service import get_doctor


def _group_slots_by_session(slots: list) -> dict[str, list[dict[str, object]]]:
    morning_slots: list[dict[str, object]] = []
    afternoon_slots: list[dict[str, object]] = []

    for slot in slots:
        payload = {
            "id": slot.id,
            "available_date": slot.available_date.isoformat(),
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "appointment_type": slot.appointment_type,
            "is_booked": slot.is_booked,
        }
        hour = int(slot.start_time.split(":", maxsplit=1)[0])
        if hour < 12:
            morning_slots.append(payload)
        else:
            afternoon_slots.append(payload)

    return {
        "morning_slots": morning_slots,
        "afternoon_slots": afternoon_slots,
    }


def get_doctor_availability(session: Session, doctor_id: int) -> dict[str, object]:
    doctor: DoctorResponse = get_doctor(session, doctor_id)
    available_dates = get_available_dates_for_doctor(session, doctor_id)
    available_slots = get_available_slots_for_doctor(session, doctor_id)

    grouped_slots = _group_slots_by_session(available_slots)
    return {
        "doctor": doctor.model_dump(),
        "available_dates": [available_date.isoformat() for available_date in available_dates],
        **grouped_slots,
    }


def get_available_dates(session: Session, doctor_id: int) -> list[date]:
    get_doctor(session, doctor_id)
    return get_available_dates_for_doctor(session, doctor_id)


def get_available_slots(
    session: Session,
    doctor_id: int,
    available_date: date | None = None,
) -> list[dict[str, object]]:
    get_doctor(session, doctor_id)
    slots = get_available_slots_for_doctor(session, doctor_id, available_date=available_date)
    return [
        {
            "id": slot.id,
            "available_date": slot.available_date.isoformat(),
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "appointment_type": slot.appointment_type,
            "is_booked": slot.is_booked,
        }
        for slot in slots
    ]


def mark_slot_booked(session: Session, availability_id: int) -> dict[str, object] | None:
    slot = mark_availability_slot_booked(session, availability_id)
    if slot is None:
        return None

    return {
        "id": slot.id,
        "doctor_id": slot.doctor_id,
        "available_date": slot.available_date.isoformat(),
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "appointment_type": slot.appointment_type,
        "is_booked": slot.is_booked,
    }
