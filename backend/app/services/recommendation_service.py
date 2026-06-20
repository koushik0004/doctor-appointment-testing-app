from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import appointment_not_found, doctor_not_found
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.repositories.appointment_repository import get_appointment_by_id
from app.services.availability_service import get_available_slots
from app.schemas.recommendation import (
    RecommendedDoctorResponse,
    RecommendedDoctorsResponse,
    RecommendationReason,
)

MAX_RECOMMENDATIONS = 5
RELATED_SPECIALTIES: dict[str, list[str]] = {
    "General Practice": ["Family Medicine", "Internal Medicine"],
    "General Physician": ["Family Medicine", "Internal Medicine"],
    "Family Medicine": ["General Practice", "Internal Medicine"],
    "Internal Medicine": ["General Practice", "Family Medicine"],
    "Cardiology": ["Internal Medicine", "General Practice"],
    "Pediatrics": ["Family Medicine", "General Practice"],
    "Dermatology": ["General Practice", "Internal Medicine"],
}
LOOKAHEAD_DAYS = 30


def _today() -> date:
    return date.today()


def _format_slot_time(start_time: str) -> str:
    return datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p").lstrip("0")


def _find_next_available_slot(session: Session, doctor_id: int) -> tuple[date, str] | None:
    start_date = _today()

    for offset in range(LOOKAHEAD_DAYS + 1):
        search_date = start_date + timedelta(days=offset)
        slots = get_available_slots(session, doctor_id, available_date=search_date)
        if slots:
            first_slot = slots[0]
            return search_date, _format_slot_time(str(first_slot["start_time"]))

    return None


def _load_source_doctor(session: Session, appointment_id: int) -> tuple[Appointment, Doctor]:
    appointment = get_appointment_by_id(session, appointment_id)
    if appointment is None:
        raise appointment_not_found(appointment_id)

    doctor = session.get(Doctor, appointment.doctor_id)
    if doctor is None:
        raise doctor_not_found(appointment.doctor_id)

    return appointment, doctor


def _specialty_pool(source_specialty: str, same_specialty_count: int) -> list[str]:
    if same_specialty_count >= 3:
        return [source_specialty]

    related = RELATED_SPECIALTIES.get(source_specialty, [])
    pool: list[str] = [source_specialty]
    for specialty in related:
        if specialty not in pool:
            pool.append(specialty)
    return pool


def _fetch_candidate_doctors(
    session: Session,
    *,
    specialties: list[str],
    exclude_doctor_id: int,
) -> list[Doctor]:
    if not specialties:
        return []

    statement = (
        select(Doctor)
        .where(
            Doctor.is_active.is_(True),
            Doctor.id != exclude_doctor_id,
            Doctor.specialty.in_(specialties),
        )
    )
    return list(session.scalars(statement).all())


def _sort_candidates(
    doctors: list[tuple[Doctor, RecommendationReason, date, str]],
) -> list[tuple[Doctor, RecommendationReason, date, str]]:
    return sorted(
        doctors,
        key=lambda item: (
            -item[0].rating,
            -item[0].review_count,
            item[0].name.lower(),
        ),
    )


def _to_response_item(
    doctor: Doctor,
    *,
    recommendation_reason: RecommendationReason,
    next_available_date: date,
    next_available_slot: str,
) -> RecommendedDoctorResponse:
    return RecommendedDoctorResponse(
        doctor_id=doctor.id,
        doctor_name=doctor.name,
        specialty=doctor.specialty,
        rating=doctor.rating,
        review_count=doctor.review_count,
        next_available_date=next_available_date,
        next_available_slot=next_available_slot,
        profile_image=doctor.image_url,
        clinic_name=doctor.clinic_name,
        recommendation_reason=recommendation_reason,
    )


def get_recommended_doctors(
    session: Session,
    appointment_id: int,
) -> RecommendedDoctorsResponse:
    _, source_doctor = _load_source_doctor(session, appointment_id)
    source_specialty = source_doctor.specialty.strip()

    same_specialty_doctors = _fetch_candidate_doctors(
        session,
        specialties=[source_specialty],
        exclude_doctor_id=source_doctor.id,
    )
    specialty_pool = _specialty_pool(source_specialty, len(same_specialty_doctors))
    candidate_doctors = _fetch_candidate_doctors(
        session,
        specialties=specialty_pool,
        exclude_doctor_id=source_doctor.id,
    )

    scored_candidates: list[tuple[Doctor, RecommendationReason, date, str]] = []
    for doctor in candidate_doctors:
        availability = _find_next_available_slot(session, doctor.id)
        if availability is None:
            continue

        next_available_date, next_available_slot = availability
        recommendation_reason = (
            RecommendationReason.SAME_SPECIALTY
            if doctor.specialty == source_specialty
            else RecommendationReason.RELATED_SPECIALTY
        )
        scored_candidates.append(
            (
                doctor,
                recommendation_reason,
                next_available_date,
                next_available_slot,
            )
        )

    sorted_candidates = _sort_candidates(scored_candidates)
    recommendations = [
        _to_response_item(
            doctor,
            recommendation_reason=recommendation_reason,
            next_available_date=next_available_date,
            next_available_slot=next_available_slot,
        )
        for doctor, recommendation_reason, next_available_date, next_available_slot in sorted_candidates[
            :MAX_RECOMMENDATIONS
        ]
    ]

    return RecommendedDoctorsResponse(
        appointment_id=appointment_id,
        specialty=source_specialty,
        recommended_doctors=recommendations,
    )
