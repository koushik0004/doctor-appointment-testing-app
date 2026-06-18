from datetime import date
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


TEST_DB = Path(__file__).resolve().parent / "test_availability.sqlite3"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base  # noqa: E402
from app.models.availability import DoctorAvailability  # noqa: E402
from app.models.doctor import Doctor  # noqa: E402
from app.services.availability_service import (  # noqa: E402
    get_available_dates,
    get_available_slots,
    get_doctor_availability,
    mark_slot_booked,
)


def test_availability_service_groups_and_filters_slots():
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
            session.flush()

            morning_slot = DoctorAvailability(
                doctor_id=doctor.id,
                available_date=date(2026, 6, 8),
                start_time="09:30",
                end_time="10:00",
                appointment_type="IN_PERSON",
                is_booked=False,
            )
            afternoon_slot = DoctorAvailability(
                doctor_id=doctor.id,
                available_date=date(2026, 6, 8),
                start_time="14:30",
                end_time="15:00",
                appointment_type="TELEMEDICINE",
                is_booked=False,
            )
            booked_slot = DoctorAvailability(
                doctor_id=doctor.id,
                available_date=date(2026, 6, 9),
                start_time="11:30",
                end_time="12:00",
                appointment_type="IN_PERSON",
                is_booked=True,
            )
            session.add_all([morning_slot, afternoon_slot, booked_slot])
            session.commit()

            dates = get_available_dates(session, doctor.id)
            assert dates == [date(2026, 6, 8)]

            slots = get_available_slots(session, doctor.id)
            assert len(slots) == 2
            assert all(slot["is_booked"] is False for slot in slots)

            availability = get_doctor_availability(session, doctor.id)
            assert availability["doctor"]["name"] == "Dr. Availability Doctor"
            assert availability["available_dates"] == ["2026-06-08"]
            assert len(availability["morning_slots"]) == 1
            assert len(availability["afternoon_slots"]) == 1

            booked_payload = mark_slot_booked(session, morning_slot.id)
            assert booked_payload is not None
            assert booked_payload["is_booked"] is True

            assert get_available_slots(session, doctor.id, available_date=date(2026, 6, 8)) == [
                {
                    "id": afternoon_slot.id,
                    "available_date": "2026-06-08",
                    "start_time": "14:30",
                    "end_time": "15:00",
                    "appointment_type": "TELEMEDICINE",
                    "is_booked": False,
                }
            ]
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()
