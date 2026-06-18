from datetime import date

from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from app.models.availability import DoctorAvailability


def get_available_dates(session: Session, doctor_id: int) -> list[date]:
    statement = (
        select(distinct(DoctorAvailability.available_date))
        .where(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.is_booked.is_(False),
        )
        .order_by(DoctorAvailability.available_date.asc())
    )
    return [row[0] for row in session.execute(statement).all()]


def get_available_slots(
    session: Session,
    doctor_id: int,
    available_date: date | None = None,
) -> list[DoctorAvailability]:
    statement = select(DoctorAvailability).where(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.is_booked.is_(False),
    )

    if available_date is not None:
        statement = statement.where(DoctorAvailability.available_date == available_date)

    statement = statement.order_by(
        DoctorAvailability.available_date.asc(),
        DoctorAvailability.start_time.asc(),
        DoctorAvailability.id.asc(),
    )
    return list(session.scalars(statement).all())


def get_availability_by_id(session: Session, availability_id: int) -> DoctorAvailability | None:
    return session.get(DoctorAvailability, availability_id)


def mark_slot_booked(session: Session, availability_id: int) -> DoctorAvailability | None:
    slot = session.get(DoctorAvailability, availability_id)
    if slot is None:
        return None

    slot.is_booked = True
    session.flush()
    session.refresh(slot)
    return slot
