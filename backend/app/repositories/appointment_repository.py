from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment


def create_appointment(session: Session, appointment: Appointment) -> Appointment:
    session.add(appointment)
    session.flush()
    session.refresh(appointment)
    return appointment


def save_appointment(session: Session, appointment: Appointment) -> Appointment:
    session.add(appointment)
    session.flush()
    session.refresh(appointment)
    return appointment


def get_appointment_by_id(session: Session, appointment_id: int) -> Appointment | None:
    return session.get(Appointment, appointment_id)


def get_appointment_by_confirmation_code(
    session: Session,
    confirmation_code: str,
) -> Appointment | None:
    statement = select(Appointment).where(Appointment.confirmation_code == confirmation_code)
    return session.scalars(statement).first()


def get_appointment_by_doctor_date_time(
    session: Session,
    *,
    doctor_id: int,
    appointment_date: date,
    appointment_time: str,
) -> Appointment | None:
    statement = select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
    )
    return session.scalars(statement).first()


def get_appointments_for_doctor_on_date(
    session: Session,
    *,
    doctor_id: int,
    appointment_date: date,
) -> list[Appointment]:
    statement = select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
    )
    return list(session.scalars(statement).all())


def get_appointments_for_doctor_in_range(
    session: Session,
    *,
    doctor_id: int,
    date_from: date,
    date_to: date,
) -> list[Appointment]:
    statement = select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= date_from,
        Appointment.appointment_date <= date_to,
    )
    return list(session.scalars(statement).all())
