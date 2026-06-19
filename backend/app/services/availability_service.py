from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.repositories.appointment_repository import get_appointments_for_doctor_on_date
from app.services.schedule_service import generate_daily_slots


def _booked_start_times_for_date(session: Session, doctor_id: int, slot_date: date) -> set[str]:
    appointments = get_appointments_for_doctor_on_date(
        session,
        doctor_id=doctor_id,
        appointment_date=slot_date,
    )
    return {appointment.appointment_time for appointment in appointments}


def _generate_available_slots(
    *,
    slot_date: date,
    booked_start_times: set[str],
) -> list[dict[str, object]]:
    return generate_daily_slots(
        slot_date,
        booked_start_times=booked_start_times,
    )


def get_doctor_available_slots(
    session: Session,
    doctor_id: int,
    *,
    slot_date: date,
) -> dict[str, object]:
    booked_start_times = _booked_start_times_for_date(session, doctor_id, slot_date)
    available_slots = _generate_available_slots(
        slot_date=slot_date,
        booked_start_times=booked_start_times,
    )

    return {
        "date": slot_date.isoformat(),
        "doctor_id": doctor_id,
        "available_slots": available_slots,
    }


def get_available_slots(
    session: Session,
    doctor_id: int,
    available_date: date | None = None,
) -> list[dict[str, object]]:
    slot_date = available_date or date.today()
    return get_doctor_available_slots(session, doctor_id, slot_date=slot_date)["available_slots"]
