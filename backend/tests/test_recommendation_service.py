from datetime import date, timedelta
from pathlib import Path
import sys

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


TEST_DB = Path(__file__).resolve().parent / "test_recommendation.sqlite3"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base  # noqa: E402
from app.models.appointment import Appointment, AppointmentStatus  # noqa: E402
from app.models.doctor import Doctor  # noqa: E402
from app.models.patient import Patient  # noqa: E402
import app.services.recommendation_service as recommendation_service  # noqa: E402
from app.services.recommendation_service import get_recommended_doctors  # noqa: E402


def _create_doctor(
    session,
    *,
    name: str,
    specialty: str,
    rating: float,
    review_count: int,
    active: bool = True,
) -> Doctor:
    doctor = Doctor(
        name=name,
        specialty=specialty,
        rating=rating,
        review_count=review_count,
        clinic_name=f"{name} Clinic",
        location="Test City",
        consultation_fee_min=100,
        consultation_fee_max=200,
        next_available_slot="Tomorrow, 10:00 AM",
        appointment_types=Doctor.encode_list(["IN_PERSON", "TELEMEDICINE"]),
        languages=Doctor.encode_list(["English"]),
        description="Recommendation test doctor.",
        image_url=f"/avatars/{name.lower().replace(' ', '-')}.svg",
        is_active=active,
    )
    session.add(doctor)
    session.flush()
    return doctor


def _create_patient(session, *, full_name: str, email: str) -> Patient:
    patient = Patient(full_name=full_name, email=email, phone="1234567890")
    session.add(patient)
    session.flush()
    return patient


def _create_appointment(
    session,
    *,
    doctor_id: int,
    patient_id: int,
    appointment_date: date,
) -> Appointment:
    appointment = Appointment(
        confirmation_code=f"CN-{doctor_id}-{patient_id}-{appointment_date:%Y%m%d}",
        doctor_id=doctor_id,
        patient_id=patient_id,
        appointment_date=appointment_date,
        appointment_time="10:00",
        appointment_type="IN_PERSON",
        health_description=None,
        status=AppointmentStatus.CONFIRMED.value,
    )
    session.add(appointment)
    session.flush()
    return appointment


def test_recommended_doctors_uses_same_specialty_when_enough_candidates():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            source_doctor = _create_doctor(
                session,
                name="Dr. Source Cardio",
                specialty="Cardiology",
                rating=4.6,
                review_count=50,
            )
            patient = _create_patient(session, full_name="Test Patient", email="patient@example.com")
            appointment = _create_appointment(
                session,
                doctor_id=source_doctor.id,
                patient_id=patient.id,
                appointment_date=date.today() + timedelta(days=1),
            )

            _create_doctor(
                session,
                name="Dr. Bravo Cardio",
                specialty="Cardiology",
                rating=4.9,
                review_count=25,
            )
            _create_doctor(
                session,
                name="Dr. Alpha Cardio",
                specialty="Cardiology",
                rating=4.9,
                review_count=20,
            )
            _create_doctor(
                session,
                name="Dr. Charlie Cardio",
                specialty="Cardiology",
                rating=4.8,
                review_count=40,
            )
            _create_doctor(
                session,
                name="Dr. Related Medicine",
                specialty="Internal Medicine",
                rating=5.0,
                review_count=200,
            )
            session.commit()

            response = get_recommended_doctors(session, appointment.id)

            assert response.appointment_id == appointment.id
            assert response.specialty == "Cardiology"
            assert [item.doctor_name for item in response.recommended_doctors] == [
                "Dr. Bravo Cardio",
                "Dr. Alpha Cardio",
                "Dr. Charlie Cardio",
            ]
            assert all(
                item.recommendation_reason.value == "same_specialty"
                for item in response.recommended_doctors
            )
            assert all(item.specialty == "Cardiology" for item in response.recommended_doctors)
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()


def test_recommended_doctors_falls_back_to_related_specialties_when_needed():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            source_doctor = _create_doctor(
                session,
                name="Dr. Source GP",
                specialty="General Practice",
                rating=4.7,
                review_count=30,
            )
            patient = _create_patient(session, full_name="Test Patient", email="patient@example.com")
            appointment = _create_appointment(
                session,
                doctor_id=source_doctor.id,
                patient_id=patient.id,
                appointment_date=date.today() + timedelta(days=1),
            )

            _create_doctor(
                session,
                name="Dr. Same GP",
                specialty="General Practice",
                rating=4.6,
                review_count=22,
            )
            _create_doctor(
                session,
                name="Dr. Family Medicine",
                specialty="Family Medicine",
                rating=4.95,
                review_count=100,
            )
            _create_doctor(
                session,
                name="Dr. Internal Medicine",
                specialty="Internal Medicine",
                rating=4.8,
                review_count=80,
            )
            session.commit()

            response = get_recommended_doctors(session, appointment.id)

            assert response.specialty == "General Practice"
            assert len(response.recommended_doctors) == 3
            assert any(
                item.recommendation_reason.value == "same_specialty"
                for item in response.recommended_doctors
            )
            assert any(
                item.recommendation_reason.value == "related_specialty"
                for item in response.recommended_doctors
            )
            assert {item.specialty for item in response.recommended_doctors} == {
                "General Practice",
                "Family Medicine",
                "Internal Medicine",
            }
            assert all(item.doctor_id != source_doctor.id for item in response.recommended_doctors)
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()


def test_recommended_doctors_returns_empty_list_when_no_doctors_are_bookable(monkeypatch):
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            source_doctor = _create_doctor(
                session,
                name="Dr. Source Derm",
                specialty="Dermatology",
                rating=4.7,
                review_count=30,
            )
            patient = _create_patient(session, full_name="Test Patient", email="patient@example.com")
            appointment = _create_appointment(
                session,
                doctor_id=source_doctor.id,
                patient_id=patient.id,
                appointment_date=date.today() + timedelta(days=1),
            )
            _create_doctor(
                session,
                name="Dr. Related GP",
                specialty="General Practice",
                rating=4.9,
                review_count=60,
            )
            session.commit()

            monkeypatch.setattr(
                recommendation_service,
                "_find_next_available_slot",
                lambda session, doctor_id: None,
            )

            response = get_recommended_doctors(session, appointment.id)

            assert response.recommended_doctors == []
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()


def test_recommended_doctors_allows_inactive_source_doctor():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            source_doctor = _create_doctor(
                session,
                name="Dr. Inactive GP",
                specialty="General Practice",
                rating=4.7,
                review_count=30,
                active=False,
            )
            patient = _create_patient(session, full_name="Test Patient", email="patient@example.com")
            appointment = _create_appointment(
                session,
                doctor_id=source_doctor.id,
                patient_id=patient.id,
                appointment_date=date.today() + timedelta(days=1),
            )
            _create_doctor(
                session,
                name="Dr. Related Medicine",
                specialty="Internal Medicine",
                rating=4.9,
                review_count=50,
            )
            session.commit()

            response = get_recommended_doctors(session, appointment.id)

            assert response.specialty == "General Practice"
            assert len(response.recommended_doctors) == 1
            assert response.recommended_doctors[0].recommendation_reason.value == "related_specialty"
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()


def test_recommended_doctors_raises_for_missing_appointment():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            with pytest.raises(HTTPException) as exc_info:
                get_recommended_doctors(session, 999)
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Appointment 999 not found"
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()
