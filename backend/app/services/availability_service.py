from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories.appointment_repository import (
    get_appointments_for_doctor_in_range,
)
from app.schemas.doctor import AppointmentType, DoctorResponse
from app.services.doctor_service import get_doctor
from app.services.schedule_service import generate_daily_slots, group_slots_by_session


def _default_window() -> tuple[date, date]:
    today = date.today()
    return today, today + timedelta(days=29)


def _appointments_by_date(
    appointments,
) -> dict[date, set[str]]:
    booked: dict[date, set[str]] = {}
    for appointment in appointments:
        booked.setdefault(appointment.appointment_date, set()).add(appointment.appointment_time)
    return booked


def _generate_slots_for_range(
    *,
    date_from: date,
    date_to: date,
    appointment_type: str,
    booked_times: dict[date, set[str]],
) -> tuple[list[date], list[dict[str, object]]]:
    available_dates: list[date] = []
    slots: list[dict[str, object]] = []

    current = date_from
    while current <= date_to:
        daily_slots = generate_daily_slots(
            current,
            appointment_type=appointment_type,
            booked_start_times=booked_times.get(current, set()),
        )
        if daily_slots:
            available_dates.append(current)
            slots.extend(daily_slots)
        current += timedelta(days=1)

    return available_dates, slots


def _resolve_appointment_type(
    doctor: DoctorResponse,
    appointment_type: AppointmentType | None,
) -> str:
    if appointment_type is not None:
        return appointment_type.value
    return doctor.appointment_types[0] if doctor.appointment_types else AppointmentType.IN_PERSON.value


def _build_window_response(
    *,
    session: Session,
    doctor_id: int,
    date_from: date,
    date_to: date,
    appointment_type: AppointmentType | None = None,
) -> dict[str, object]:
    doctor: DoctorResponse = get_doctor(session, doctor_id)
    resolved_type = _resolve_appointment_type(doctor, appointment_type)
    appointments = get_appointments_for_doctor_in_range(
        session,
        doctor_id=doctor_id,
        date_from=date_from,
        date_to=date_to,
    )
    booked_times = _appointments_by_date(appointments)
    available_dates, slots = _generate_slots_for_range(
        date_from=date_from,
        date_to=date_to,
        appointment_type=resolved_type,
        booked_times=booked_times,
    )

    grouped_slots = group_slots_by_session(slots)
    return {
        "doctor_id": doctor_id,
        "doctor": doctor.model_dump(),
        "available_dates": [item.isoformat() for item in available_dates],
        **grouped_slots,
    }


def get_doctor_availability(session: Session, doctor_id: int) -> dict[str, object]:
    date_from, date_to = _default_window()
    return _build_window_response(
        session=session,
        doctor_id=doctor_id,
        date_from=date_from,
        date_to=date_to,
    )


def get_doctor_availability_window(
    session: Session,
    doctor_id: int,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    appointment_type: AppointmentType | None = None,
) -> dict[str, object]:
    if date_from is None and date_to is None:
        date_from, date_to = _default_window()
    elif date_from is None:
        date_from = date_to
    elif date_to is None:
        date_to = date_from

    if date_from is None or date_to is None:
        date_from, date_to = _default_window()

    if date_to < date_from:
        date_from, date_to = date_to, date_from

    return _build_window_response(
        session=session,
        doctor_id=doctor_id,
        date_from=date_from,
        date_to=date_to,
        appointment_type=appointment_type,
    )


def get_available_dates(session: Session, doctor_id: int) -> list[date]:
    date_from, date_to = _default_window()
    response = get_doctor_availability_window(
        session,
        doctor_id,
        date_from=date_from,
        date_to=date_to,
    )
    return [date.fromisoformat(item) for item in response["available_dates"]]


def get_available_slots(
    session: Session,
    doctor_id: int,
    available_date: date | None = None,
    appointment_type: AppointmentType | None = None,
) -> list[dict[str, object]]:
    if available_date is None:
        date_from, date_to = _default_window()
    else:
        date_from = available_date
        date_to = available_date

    response = get_doctor_availability_window(
        session,
        doctor_id,
        date_from=date_from,
        date_to=date_to,
        appointment_type=appointment_type,
    )
    return [*response["morning_slots"], *response["afternoon_slots"]]
