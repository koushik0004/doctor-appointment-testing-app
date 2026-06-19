from datetime import date, datetime
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


TEST_DB = Path(__file__).resolve().parent / "test_availability.sqlite3"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base  # noqa: E402
from app.models.appointment import Appointment, AppointmentStatus  # noqa: E402
from app.models.doctor import Doctor  # noqa: E402
from app.models.patient import Patient  # noqa: E402
from app.services.availability_service import (  # noqa: E402
    get_available_dates,
    get_available_slots,
    get_doctor_availability_window,
)
from app.services.schedule_service import generate_daily_slots  # noqa: E402


def test_generate_daily_slots_hides_elapsed_slots_for_today():
    slots = generate_daily_slots(
        date(2026, 6, 19),
        appointment_type="IN_PERSON",
        reference_datetime=datetime(2026, 6, 19, 13, 0),
    )

    assert [slot["start_time"] for slot in slots] == ["14:00", "16:00", "18:00"]


def test_availability_service_groups_runtime_slots_and_marks_booked():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            doctor = Doctor(
                name="Dr. Availability Doctor",
                specialty="General Practice",
                rating=4.9,
                review_count=12,
                clinic_name="Availability Clinic",
                location="Test City",
                consultation_fee_min=90,
                consultation_fee_max=140,
                next_available_slot="Today, 10:00 AM",
                appointment_types=Doctor.encode_list(["IN_PERSON", "TELEMEDICINE"]),
                languages=Doctor.encode_list(["English"]),
                description="Availability coverage doctor.",
                image_url="/avatars/test-doctor.svg",
                is_active=True,
            )
            session.add(doctor)
            patient = Patient(
                full_name="Test Patient",
                email="patient@example.com",
                phone="1234567890",
            )
            session.add(patient)
            session.flush()

            future_date = date(2026, 6, 20)
            booked_appointment = Appointment(
                confirmation_code="CN-TEST-0001",
                doctor_id=doctor.id,
                patient_id=patient.id,
                appointment_date=future_date,
                appointment_time="10:00",
                appointment_type="IN_PERSON",
                health_description=None,
                status=AppointmentStatus.CONFIRMED.value,
            )
            session.add(booked_appointment)
            session.commit()

            slots = get_available_slots(session, doctor.id, available_date=future_date)
            assert len(slots) == 6
            assert any(
                slot["start_time"] == "10:00" and slot["is_booked"] is True
                for slot in slots
            )

            availability = get_doctor_availability_window(
                session,
                doctor.id,
                date_from=future_date,
                date_to=future_date,
            )
            assert availability["doctor"]["name"] == "Dr. Availability Doctor"
            assert availability["available_dates"] == ["2026-06-20"]
            assert len(availability["morning_slots"]) == 2
            assert len(availability["afternoon_slots"]) == 4
            assert any(
                slot["start_time"] == "10:00" and slot["is_booked"] is True
                for slot in availability["morning_slots"]
            )

            dates = get_available_dates(session, doctor.id)
            assert date(2026, 6, 20) in dates
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()
