from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment


def create_appointment(session: Session, appointment: Appointment) -> Appointment:
    session.add(appointment)
    session.commit()
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
