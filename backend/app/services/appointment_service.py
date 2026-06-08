from __future__ import annotations

import secrets
import string
from datetime import date

from sqlalchemy.orm import Session

from app.core.errors import (
    appointment_not_found,
    availability_not_found,
    booking_conflict,
    invalid_booking_request,
)
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.repositories.appointment_repository import (
    create_appointment as persist_appointment,
    get_appointment_by_id,
    get_appointment_by_confirmation_code,
)
from app.repositories.availability_repository import (
    get_availability_by_id,
    mark_slot_booked as persist_slot_booked,
)
from app.repositories.patient_repository import create_patient, get_patient_by_email
from app.schemas.appointment import (
    AppointmentConfirmationResponse,
    AppointmentCreateRequest,
    AppointmentCreateResponse,
)
from app.services.doctor_service import get_doctor


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


def _validate_slot(
    session: Session,
    *,
    doctor_id: int,
    availability_id: int,
    appointment_date: date,
    start_time: str,
    appointment_type: str,
):
    slot = get_availability_by_id(session, availability_id)
    if slot is None:
        raise availability_not_found(availability_id)

    if slot.doctor_id != doctor_id:
        raise invalid_booking_request("Selected slot does not belong to the chosen doctor.")

    if slot.is_booked:
        raise booking_conflict("Selected slot is already booked.")

    if slot.available_date != appointment_date:
        raise invalid_booking_request("Selected slot date does not match the availability slot.")

    if slot.start_time != start_time:
        raise invalid_booking_request("Selected slot time does not match the availability slot.")

    if slot.appointment_type != appointment_type:
        raise invalid_booking_request("Selected appointment type does not match the availability slot.")

    return slot


def create_appointment_booking(
    session: Session,
    request: AppointmentCreateRequest,
) -> AppointmentCreateResponse:
    response_data: dict[str, object]
    with session.begin():
        get_doctor(session, request.doctor_id)
        slot = _validate_slot(
            session,
            doctor_id=request.doctor_id,
            availability_id=request.availability_id,
            appointment_date=request.appointment_date,
            start_time=request.start_time,
            appointment_type=request.appointment_type.value,
        )

        patient = _get_or_create_patient(session, request.patient)
        appointment = Appointment(
            confirmation_code=_generate_confirmation_code(session),
            doctor_id=request.doctor_id,
            patient_id=patient.id,
            availability_id=slot.id,
            appointment_date=request.appointment_date,
            appointment_time=request.start_time,
            appointment_type=request.appointment_type.value,
            health_description=request.health_description,
            status=AppointmentStatus.CONFIRMED.value,
        )
        created = persist_appointment(session, appointment)
        persist_slot_booked(session, slot.id)
        response_data = {
            "id": created.id,
            "confirmation_code": created.confirmation_code,
            "status": AppointmentStatus(created.status),
            "doctor_id": created.doctor_id,
            "patient_id": created.patient_id,
            "appointment_date": created.appointment_date,
            "start_time": created.appointment_time,
            "end_time": slot.end_time,
        }

    return AppointmentCreateResponse(**response_data)


def get_appointment_confirmation(session: Session, appointment_id: int) -> AppointmentConfirmationResponse:
    appointment = get_appointment_by_id(session, appointment_id)
    if appointment is None:
        raise appointment_not_found(appointment_id)

    doctor = get_doctor(session, appointment.doctor_id)
    slot = get_availability_by_id(session, appointment.availability_id) if appointment.availability_id else None

    if slot is None:
        raise invalid_booking_request("Appointment is missing its booked availability slot.")

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
        end_time=slot.end_time,
        appointment_type=appointment.appointment_type,
        health_description=appointment.health_description,
    )
