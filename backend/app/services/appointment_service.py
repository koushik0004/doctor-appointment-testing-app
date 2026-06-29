from __future__ import annotations

import secrets
import string
from datetime import date, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import (
    appointment_not_found,
    booking_conflict,
    invalid_booking_request,
)
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.repositories.appointment_repository import (
    create_appointment as persist_appointment,
    get_appointment_by_doctor_date_time,
    get_appointment_by_id,
    get_appointment_by_confirmation_code,
    save_appointment,
)
from app.repositories.patient_repository import create_patient, get_patient_by_email
from app.schemas.appointment import (
    AppointmentConfirmationResponse,
    AppointmentDetailsResponse,
    AppointmentCreateRequest,
    AppointmentCreateResponse,
)
from app.services.doctor_service import get_doctor
from app.services.schedule_service import SLOT_DURATION_MINUTES, generate_daily_slots


def _generate_confirmation_code(session: Session) -> str:
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "CN-" + "".join(secrets.choice(string.digits) for _ in range(5)) + "-" + "".join(
            secrets.choice(alphabet) for _ in range(2)
        )
        if get_appointment_by_confirmation_code(session, code) is None:
            return code


def _get_or_create_patient(session: Session, patient_data) -> Patient:
    patient = get_patient_by_email(session, str(patient_data.email))
    if patient is not None:
        patient.full_name = patient_data.full_name
        patient.phone = patient_data.phone
        session.flush()
        session.refresh(patient)
        return patient

    patient = Patient(
        full_name=patient_data.full_name,
        email=str(patient_data.email),
        phone=patient_data.phone,
    )
    return create_patient(session, patient)


def _slot_end_time(start_time: str) -> str:
    start_datetime = datetime.strptime(start_time, "%H:%M")
    return (start_datetime + timedelta(minutes=SLOT_DURATION_MINUTES)).strftime("%H:%M")


def _validate_slot(
    session: Session,
    *,
    doctor_id: int,
    appointment_date: date,
    start_time: str,
    appointment_type: str,
):
    doctor = get_doctor(session, doctor_id)

    if appointment_type not in doctor.appointment_types:
        raise invalid_booking_request("Selected appointment type is not supported by the chosen doctor.")

    slot_datetime = datetime.combine(appointment_date, datetime.strptime(start_time, "%H:%M").time())
    if slot_datetime <= datetime.now():
        raise invalid_booking_request("Selected slot has already passed.")

    valid_slots = {
        slot["start_time"]
        for slot in generate_daily_slots(
            appointment_date,
            reference_datetime=datetime.now(),
        )
    }
    if start_time not in valid_slots:
        raise invalid_booking_request("Selected slot is not available for the chosen date.")

    existing_appointment = get_appointment_by_doctor_date_time(
        session,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=start_time,
    )
    if existing_appointment is not None:
        raise booking_conflict("Selected slot is already booked.")

    return {
        "doctor": doctor,
        "appointment_date": appointment_date,
        "start_time": start_time,
        "end_time": _slot_end_time(start_time),
    }


def create_appointment_booking(
    session: Session,
    request: AppointmentCreateRequest,
) -> AppointmentCreateResponse:
    response_data: dict[str, object]
    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    with transaction:
        slot = _validate_slot(
            session,
            doctor_id=request.doctor_id,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
            appointment_type=request.appointment_type.value,
        )

        patient = _get_or_create_patient(session, request.patient)
        appointment = Appointment(
            confirmation_code=_generate_confirmation_code(session),
            doctor_id=slot["doctor"].id,
            patient_id=patient.id,
            appointment_date=slot["appointment_date"],
            appointment_time=slot["start_time"],
            appointment_type=request.appointment_type.value,
            health_description=request.health_description,
            status=AppointmentStatus.CONFIRMED.value,
        )
        try:
            created = persist_appointment(session, appointment)
        except IntegrityError as exc:  # pragma: no cover - database constraint fallback
            raise booking_conflict("Selected slot is already booked.") from exc
        response_data = {
            "id": created.id,
            "confirmation_code": created.confirmation_code,
            "status": AppointmentStatus(created.status),
            "doctor_id": created.doctor_id,
            "patient_id": created.patient_id,
            "appointment_date": created.appointment_date,
            "start_time": created.appointment_time,
            "end_time": slot["end_time"],
        }

    return AppointmentCreateResponse(**response_data)


def get_appointment_confirmation(session: Session, appointment_id: int) -> AppointmentConfirmationResponse:
    appointment = get_appointment_by_id(session, appointment_id)
    if appointment is None:
        raise appointment_not_found(appointment_id)

    doctor = get_doctor(session, appointment.doctor_id)

    patient_model = session.get(Patient, appointment.patient_id)
    if patient_model is None:
        raise invalid_booking_request("Appointment is missing its patient record.")

    return AppointmentConfirmationResponse(
        id=appointment.id,
        confirmation_code=appointment.confirmation_code,
        status=AppointmentStatus(appointment.status),
        doctor={
            "name": doctor.name,
            "specialty": doctor.specialty,
            "clinic_name": doctor.clinic_name,
            "location": doctor.location,
        },
        patient={
            "full_name": patient_model.full_name,
            "email": patient_model.email,
            "phone": patient_model.phone,
        },
        appointment_date=appointment.appointment_date,
        start_time=appointment.appointment_time,
        end_time=_slot_end_time(appointment.appointment_time),
        appointment_type=appointment.appointment_type,
        health_description=appointment.health_description,
    )


def get_appointment_confirmation_by_reference(
    session: Session,
    *,
    appointment_id: int | None = None,
    confirmation_code: str | None = None,
) -> AppointmentConfirmationResponse:
    if appointment_id is not None:
        return get_appointment_confirmation(session, appointment_id)

    if confirmation_code is None:
        raise invalid_booking_request("Appointment reference is required.")

    appointment = get_appointment_by_confirmation_code(session, confirmation_code)
    if appointment is None:
        raise invalid_booking_request("Appointment confirmation code was not found.")

    return get_appointment_confirmation(session, appointment.id)


def cancel_appointment_booking(
    session: Session,
    *,
    appointment_id: int | None = None,
    confirmation_code: str | None = None,
) -> AppointmentConfirmationResponse:
    if appointment_id is not None:
        appointment = get_appointment_by_id(session, appointment_id)
    elif confirmation_code is not None:
        appointment = get_appointment_by_confirmation_code(session, confirmation_code)
    else:
        raise invalid_booking_request("Appointment reference is required.")

    if appointment is None:
        if appointment_id is not None:
            raise appointment_not_found(appointment_id)
        raise invalid_booking_request("Appointment confirmation code was not found.")

    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    with transaction:
        appointment.status = AppointmentStatus.CANCELLED.value
        save_appointment(session, appointment)

    return get_appointment_confirmation(session, appointment.id)


def get_appointment_details(session: Session, appointment_id: int) -> AppointmentDetailsResponse:
    appointment = get_appointment_by_id(session, appointment_id)
    if appointment is None:
        raise appointment_not_found(appointment_id)

    doctor = get_doctor(session, appointment.doctor_id)

    patient_model = session.get(Patient, appointment.patient_id)
    if patient_model is None:
        raise invalid_booking_request("Appointment is missing its patient record.")

    return AppointmentDetailsResponse(
        appointment_id=appointment.id,
        doctor={
            "name": doctor.name,
            "specialty": doctor.specialty,
            "clinic_name": doctor.clinic_name,
            "location": doctor.location,
        },
        patient={
            "full_name": patient_model.full_name,
            "email": patient_model.email,
            "phone": patient_model.phone,
        },
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        appointment_type=appointment.appointment_type,
        status=AppointmentStatus(appointment.status),
        created_at=appointment.created_at,
    )
