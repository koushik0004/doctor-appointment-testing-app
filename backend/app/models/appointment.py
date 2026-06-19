from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppointmentStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    confirmation_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    doctor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    appointment_time: Mapped[str] = mapped_column(Text, nullable=False)
    appointment_type: Mapped[str] = mapped_column(Text, nullable=False)
    health_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text,
        default=AppointmentStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "appointment_type IN ('IN_PERSON', 'TELEMEDICINE')",
            name="ck_appointments_appointment_type",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'CONFIRMED', 'CANCELLED')",
            name="ck_appointments_status",
        ),
        Index(
            "ix_appointments_doctor_date_time",
            "doctor_id",
            "appointment_date",
            "appointment_time",
        ),
        UniqueConstraint(
            "doctor_id",
            "appointment_date",
            "appointment_time",
            name="uq_appointments_doctor_date_time",
        ),
    )
