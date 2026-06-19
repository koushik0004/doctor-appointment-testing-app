from __future__ import annotations

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment_search import (
    AppointmentSearchStatus,
    AppointmentSearchRequest,
    AppointmentSearchResponse,
    AppointmentSearchResult,
)


def _normalize_public_status(status: str) -> AppointmentSearchStatus:
    normalized_status = status.upper()
    if normalized_status in {AppointmentStatus.PENDING.value, AppointmentStatus.CONFIRMED.value}:
        return AppointmentSearchStatus.BOOKED
    if normalized_status == AppointmentStatus.CANCELLED.value:
        return AppointmentSearchStatus.CANCELLED
    if normalized_status == "COMPLETED":
        return AppointmentSearchStatus.COMPLETED
    raise ValueError(f"Unsupported appointment status: {status}")


def _to_search_result(
    appointment: Appointment,
    patient: Patient,
    doctor: Doctor,
) -> AppointmentSearchResult:
    return AppointmentSearchResult(
        appointment_id=appointment.id,
        patient_name=patient.full_name,
        patient_email=patient.email,
        patient_phone=patient.phone,
        doctor_name=doctor.name,
        doctor_specialty=doctor.specialty,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        appointment_type=appointment.appointment_type,
        status=_normalize_public_status(appointment.status),
    )


def search_appointments(
    session: Session,
    request: AppointmentSearchRequest,
) -> AppointmentSearchResponse:
    conditions = []

    if request.name is not None:
        conditions.append(func.lower(Patient.full_name).like(f"%{request.name.lower()}%"))
    if request.email is not None:
        conditions.append(func.lower(Patient.email) == request.email.lower())
    if request.phone is not None:
        conditions.append(Patient.phone == request.phone)

    statement = (
        select(Appointment, Patient, Doctor)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .where(and_(*conditions))
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
    )

    rows = session.execute(statement).all()
    appointments = [
        _to_search_result(appointment=row[0], patient=row[1], doctor=row[2]) for row in rows
    ]

    return AppointmentSearchResponse(
        count=len(appointments),
        appointments=appointments,
    )
