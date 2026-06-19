from datetime import date, timedelta
from pathlib import Path
import sys

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker


TEST_DB = Path(__file__).resolve().parent / "test_appointments.sqlite3"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import Base  # noqa: E402
from app.models.appointment import Appointment, AppointmentStatus  # noqa: E402
from app.models.doctor import Doctor  # noqa: E402
from app.models.patient import Patient  # noqa: E402
from app.repositories.appointment_repository import (  # noqa: E402
    create_appointment,
    get_appointment_by_confirmation_code,
    get_appointment_by_id,
)


def test_appointment_tables_and_repository_round_trip():
    engine = create_engine(f"sqlite:///{TEST_DB}")
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    try:
        Base.metadata.create_all(bind=engine)

        table_names = set(inspect(engine).get_table_names())
        assert {"doctors", "patients", "appointments"}.issubset(table_names)
        assert "doctor_availability" not in table_names

        appointment_columns = {
            column["name"] for column in inspect(engine).get_columns("appointments")
        }
        assert {
            "confirmation_code",
            "doctor_id",
            "patient_id",
            "appointment_date",
            "appointment_time",
            "appointment_type",
            "health_description",
            "status",
            "created_at",
            "updated_at",
        }.issubset(appointment_columns)
        assert "availability_id" not in appointment_columns

        unique_constraints = inspect(engine).get_unique_constraints("appointments")
        assert any(
            constraint["name"] == "uq_appointments_doctor_date_time"
            for constraint in unique_constraints
        )

        patient_indexes = inspect(engine).get_indexes("patients")
        patient_index_names = {index["name"] for index in patient_indexes}
        assert "ix_patients_full_name" in patient_index_names
        assert "ix_patients_phone" in patient_index_names

        with SessionLocal() as session:
            doctor = Doctor(
                name="Dr. Test Doctor",
                specialty="General Practice",
                rating=5.0,
                review_count=1,
                clinic_name="Test Clinic",
                location="Test City",
                consultation_fee_min=100,
                consultation_fee_max=150,
                next_available_slot="Today, 10:00 AM",
                appointment_types=Doctor.encode_list(["IN_PERSON"]),
                languages=Doctor.encode_list(["English"]),
                description="Test doctor for repository coverage.",
                image_url="/avatars/test-doctor.svg",
                is_active=True,
            )
            patient = Patient(
                full_name="Test Patient",
                email="patient@example.com",
                phone="1234567890",
            )
            session.add_all([doctor, patient])
            session.flush()

            appointment = Appointment(
                confirmation_code="CN-TEST-0001",
                doctor_id=doctor.id,
                patient_id=patient.id,
                appointment_date=date.today() + timedelta(days=1),
                appointment_time="10:00",
                appointment_type="IN_PERSON",
                health_description="Routine checkup",
                status=AppointmentStatus.CONFIRMED.value,
            )

            created = create_appointment(session, appointment)

            assert created.id is not None
            assert created.confirmation_code == "CN-TEST-0001"
            assert get_appointment_by_id(session, created.id).id == created.id
            assert get_appointment_by_confirmation_code(session, "CN-TEST-0001").id == created.id
    finally:
        engine.dispose()
        if TEST_DB.exists():
            TEST_DB.unlink()
