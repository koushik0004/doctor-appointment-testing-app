from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.schemas.doctor import AppointmentType


def get_doctors(session: Session) -> list[Doctor]:
    statement = select(Doctor).where(Doctor.is_active.is_(True)).order_by(
        Doctor.rating.desc(),
        Doctor.review_count.desc(),
        Doctor.id.asc(),
    )
    return list(session.scalars(statement).all())


def get_doctors_by_filters(
    session: Session,
    specialty: str | None = None,
    appointment_type: AppointmentType | None = None,
) -> list[Doctor]:
    statement = select(Doctor).where(Doctor.is_active.is_(True))

    if specialty:
        statement = statement.where(Doctor.specialty == specialty)

    if appointment_type:
        statement = statement.where(Doctor.appointment_types.like(f'%"{appointment_type.value}"%'))

    statement = statement.order_by(
        Doctor.rating.desc(),
        Doctor.review_count.desc(),
        Doctor.id.asc(),
    )
    return list(session.scalars(statement).all())


def get_doctor_by_id(session: Session, doctor_id: int) -> Doctor | None:
    statement = select(Doctor).where(
        Doctor.id == doctor_id,
        Doctor.is_active.is_(True),
    )
    return session.scalars(statement).first()
