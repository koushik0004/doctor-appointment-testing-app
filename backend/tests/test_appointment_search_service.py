from datetime import date
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


TEST_DB = Path(__file__).resolve().parent / "test_appointment_search.sqlite3"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base  # noqa: E402
from app.models.appointment import Appointment, AppointmentStatus  # noqa: E402
from app.models.doctor import Doctor  # noqa: E402
from app.models.patient import Patient  # noqa: E402
from app.schemas.appointment_search import AppointmentSearchRequest  # noqa: E402
from app.services.appointment_search_service import (  # noqa: E402
    search_appointments,
)


def _create_doctor(session, name: str = "Dr. Search Doctor") -> Doctor:
    doctor = Doctor(
        name=name,
        specialty="Cardiology",
        rating=4.9,
        review_count=22,
        clinic_name="Search Clinic",
        location="Test City",
        consultation_fee_min=100,
        consultation_fee_max=200,
        next_available_slot="Tomorrow, 10:00 AM",
        appointment_types=Doctor.encode_list(["IN_PERSON", "TELEMEDICINE"]),
        languages=Doctor.encode_list(["English"]),
        description="Doctor used for search tests.",
        image_url="/avatars/search-doctor.svg",
        is_active=True,
    )
    session.add(doctor)
    session.flush()
    return doctor


def _create_patient(session, full_name: str, email: str, phone: str | None) -> Patient:
    patient = Patient(full_name=full_name, email=email, phone=phone)
    session.add(patient)
    session.flush()
    return patient


def _create_appointment(
    session,
    *,
    doctor_id: int,
    patient_id: int,
    appointment_date: date,
    appointment_time: str,
    status: str,
) -> Appointment:
    appointment = Appointment(
        confirmation_code=f"CN-{doctor_id}-{patient_id}-{appointment_time.replace(':', '')}",
        doctor_id=doctor_id,
        patient_id=patient_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        appointment_type="IN_PERSON",
        health_description=None,
        status=status,
    )
    session.add(appointment)
    session.flush()
    return appointment


def test_search_appointments_filters_and_orders_results():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            doctor = _create_doctor(session)
            john = _create_patient(
                session,
                full_name="John Doe",
                email="john.doe@example.com",
                phone="9999999999",
            )
            johnathan = _create_patient(
                session,
                full_name="Johnathan Doe",
                email="johnathan.doe@example.com",
                phone="8888888888",
            )
            _create_patient(
                session,
                full_name="Alice Example",
                email="alice@example.com",
                phone="7777777777",
            )

            first = _create_appointment(
                session,
                doctor_id=doctor.id,
                patient_id=john.id,
                appointment_date=date(2026, 6, 20),
                appointment_time="09:00",
                status=AppointmentStatus.CONFIRMED.value,
            )
            second = _create_appointment(
                session,
                doctor_id=doctor.id,
                patient_id=johnathan.id,
                appointment_date=date(2026, 6, 21),
                appointment_time="10:00",
                status=AppointmentStatus.PENDING.value,
            )
            third = _create_appointment(
                session,
                doctor_id=doctor.id,
                patient_id=john.id,
                appointment_date=date(2026, 6, 19),
                appointment_time="11:00",
                status=AppointmentStatus.CANCELLED.value,
            )
            session.commit()

            request = AppointmentSearchRequest.model_validate(
                {
                    "name": "  john  ",
                }
            )
            response = search_appointments(session, request)

            assert response.count == 3
            assert [item.appointment_id for item in response.appointments] == [
                second.id,
                first.id,
                third.id,
            ]
            assert [item.status.value for item in response.appointments] == [
                "booked",
                "booked",
                "cancelled",
            ]
            assert response.appointments[0].patient_name == "Johnathan Doe"
            assert response.appointments[1].patient_name == "John Doe"
            assert response.appointments[2].patient_name == "John Doe"

            email_request = AppointmentSearchRequest.model_validate(
                {
                    "email": " JOHN.DOE@EXAMPLE.COM ",
                }
            )
            email_response = search_appointments(session, email_request)
            assert email_response.count == 2
            assert [item.appointment_id for item in email_response.appointments] == [
                first.id,
                third.id,
            ]

            phone_request = AppointmentSearchRequest.model_validate(
                {
                    "phone": " 9999999999 ",
                }
            )
            phone_response = search_appointments(session, phone_request)
            assert phone_response.count == 2
            assert [item.appointment_id for item in phone_response.appointments] == [
                first.id,
                third.id,
            ]

            combined_request = AppointmentSearchRequest.model_validate(
                {
                    "name": "john",
                    "email": "johnathan.doe@example.com",
                }
            )
            combined_response = search_appointments(session, combined_request)
            assert combined_response.count == 1
            assert combined_response.appointments[0].appointment_id == second.id
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()


def test_search_appointments_returns_empty_list_when_no_matches():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            doctor = _create_doctor(session, name="Dr. Empty Search")
            patient = _create_patient(
                session,
                full_name="Existing Patient",
                email="existing@example.com",
                phone="1234567890",
            )
            _create_appointment(
                session,
                doctor_id=doctor.id,
                patient_id=patient.id,
                appointment_date=date(2026, 6, 20),
                appointment_time="12:00",
                status=AppointmentStatus.CONFIRMED.value,
            )
            session.commit()

            request = AppointmentSearchRequest.model_validate({"name": "missing"})
            response = search_appointments(session, request)

            assert response.count == 0
            assert response.appointments == []
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()
