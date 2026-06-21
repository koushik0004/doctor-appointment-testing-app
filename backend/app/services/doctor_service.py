from sqlalchemy.orm import Session

from app.core.errors import doctor_not_found
from app.repositories.doctor_repository import (
    get_doctor_by_id,
    get_doctors_by_filters,
)
from app.schemas.doctor import AppointmentType, DoctorListResponse, DoctorResponse


def _to_doctor_response(doctor) -> DoctorResponse:
    return DoctorResponse(
        id=doctor.id,
        name=doctor.name,
        specialty=doctor.specialty,
        gender=doctor.gender or "Unspecified",
        rating=doctor.rating,
        review_count=doctor.review_count,
        clinic_name=doctor.clinic_name,
        location=doctor.location,
        consultation_fee_min=doctor.consultation_fee_min,
        consultation_fee_max=doctor.consultation_fee_max,
        next_available_slot=doctor.next_available_slot,
        appointment_types=doctor.decode_list(doctor.appointment_types),
        languages=doctor.decode_list(doctor.languages),
        description=doctor.description,
        image_url=doctor.image_url,
    )


def list_doctors(
    session: Session,
    specialty: str | None = None,
    appointment_type: AppointmentType | None = None,
    gender: str | None = None,
    location: str | None = None,
    minimum_fee: int | None = None,
    maximum_fee: int | None = None,
) -> DoctorListResponse:
    specialty_value = specialty.strip() if specialty else None
    doctors = get_doctors_by_filters(
        session,
        specialty=specialty_value,
        appointment_type=appointment_type,
        gender=gender,
        location=location,
        minimum_fee=minimum_fee,
        maximum_fee=maximum_fee,
    )
    return DoctorListResponse(
        items=[_to_doctor_response(doctor) for doctor in doctors],
        total=len(doctors),
    )


def get_doctor(session: Session, doctor_id: int) -> DoctorResponse:
    doctor = get_doctor_by_id(session, doctor_id)
    if not doctor:
        raise doctor_not_found(doctor_id)
    return _to_doctor_response(doctor)
