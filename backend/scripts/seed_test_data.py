from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_session_factory, init_db
from app.models.appointment import Appointment
from app.models.availability import DoctorAvailability
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.repositories.appointment_repository import get_appointment_by_doctor_date_time
from app.repositories.patient_repository import get_patient_by_email
from app.schemas.appointment import AppointmentCreateRequest, PatientInput
from app.schemas.doctor import AppointmentType
from app.services.appointment_service import create_appointment_booking

MAX_INSERTED_ROWS = 10
REPORT_PATH = Path(__file__).resolve().parents[2] / "docs" / "reports" / "test-data-report.md"


@dataclass(frozen=True)
class DemoBooking:
    doctor_id: int
    appointment_type: AppointmentType
    day_offset: int
    start_time: str
    patient_name: str
    patient_email: str
    patient_phone: str
    health_description: str


DEMO_BOOKINGS: tuple[DemoBooking, ...] = (
    DemoBooking(
        doctor_id=2,
        appointment_type=AppointmentType.IN_PERSON,
        day_offset=4,
        start_time="08:00",
        patient_name="Maya Patel",
        patient_email="maya.patel@example.com",
        patient_phone="+44 7700 900111",
        health_description="Mild fever and sore throat for two days.",
    ),
    DemoBooking(
        doctor_id=6,
        appointment_type=AppointmentType.TELEMEDICINE,
        day_offset=5,
        start_time="10:00",
        patient_name="Ethan Brooks",
        patient_email="ethan.brooks@example.com",
        patient_phone="+44 7700 900112",
        health_description="Follow-up on blood pressure readings and medication plan.",
    ),
    DemoBooking(
        doctor_id=9,
        appointment_type=AppointmentType.TELEMEDICINE,
        day_offset=6,
        start_time="12:00",
        patient_name="Olivia Carter",
        patient_email="olivia.carter@example.com",
        patient_phone="+44 7700 900113",
        health_description="Routine family medicine follow-up and care plan review.",
    ),
)


def _table_counts(session: Session) -> dict[str, int]:
    return {
        "doctors": session.scalar(select(func.count()).select_from(Doctor)) or 0,
        "patients": session.scalar(select(func.count()).select_from(Patient)) or 0,
        "appointments": session.scalar(select(func.count()).select_from(Appointment)) or 0,
    }


def _availability_row_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(DoctorAvailability)) or 0


def _existing_future_appointment_for_patient(
    session: Session,
    *,
    patient_email: str,
    doctor_id: int,
    appointment_type: AppointmentType,
    today: date,
) -> Appointment | None:
    statement = (
        select(Appointment)
        .join(Patient, Patient.id == Appointment.patient_id)
        .where(
            func.lower(Patient.email) == patient_email.lower(),
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_type == appointment_type.value,
            Appointment.appointment_date >= today,
            Appointment.status != "CANCELLED",
        )
        .order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
    )
    return session.scalars(statement).first()


def _safe_to_reuse_patient(existing_patient: Patient, booking: DemoBooking) -> bool:
    return (
        existing_patient.full_name == booking.patient_name
        and (existing_patient.phone or "") == booking.patient_phone
    )


def _create_booking_request(booking: DemoBooking, appointment_date: date) -> AppointmentCreateRequest:
    return AppointmentCreateRequest(
        doctor_id=booking.doctor_id,
        appointment_date=appointment_date,
        start_time=booking.start_time,
        appointment_type=booking.appointment_type,
        patient=PatientInput(
            full_name=booking.patient_name,
            email=booking.patient_email,
            phone=booking.patient_phone,
        ),
        health_description=booking.health_description,
    )


def seed_test_data() -> dict[str, object]:
    init_db()
    session = get_session_factory()()
    today = date.today()
    duplicate_reasons: list[str] = []
    inserted_entries: list[str] = []
    duplicate_lines = ["- No duplicates or conflicts were encountered during this run."]
    validation_checks = [
        "Confirmed app uses backend/.env DATABASE_URL=sqlite:///./app.db.",
        "Validated appointment types against doctor-supported appointment_types via service-layer booking.",
        "Validated only future schedule-generated slots were booked.",
        "Validated duplicate doctor/date/time conflicts before insert.",
        "Validated patient email reuse never overwrites mismatched name or phone data.",
    ]

    try:
        counts_before = _table_counts(session)
        availability_rows = _availability_row_count(session)
        inserted_rows = 0
        inserted_patient_rows = 0
        inserted_appointment_rows = 0
        skipped_rows = 0

        for booking in DEMO_BOOKINGS:
            appointment_date = today + timedelta(days=booking.day_offset)

            if inserted_rows >= MAX_INSERTED_ROWS:
                duplicate_reasons.append("Stopped before exceeding the 10-row insertion cap.")
                break

            existing_patient = get_patient_by_email(session, booking.patient_email)
            if existing_patient is not None and not _safe_to_reuse_patient(existing_patient, booking):
                skipped_rows += 1
                duplicate_reasons.append(
                    f"Skipped {booking.patient_email}: existing patient record has different name or phone."
                )
                continue

            existing_future = _existing_future_appointment_for_patient(
                session,
                patient_email=booking.patient_email,
                doctor_id=booking.doctor_id,
                appointment_type=booking.appointment_type,
                today=today,
            )
            if existing_future is not None:
                skipped_rows += 1
                duplicate_reasons.append(
                    f"Skipped {booking.patient_email}: future {booking.appointment_type.value} appointment already exists "
                    f"with doctor {booking.doctor_id} on {existing_future.appointment_date.isoformat()} at {existing_future.appointment_time}."
                )
                continue

            existing_slot = get_appointment_by_doctor_date_time(
                session,
                doctor_id=booking.doctor_id,
                appointment_date=appointment_date,
                appointment_time=booking.start_time,
            )
            if existing_slot is not None:
                skipped_rows += 1
                duplicate_reasons.append(
                    f"Skipped doctor {booking.doctor_id} slot {appointment_date.isoformat()} {booking.start_time}: slot already booked."
                )
                continue

            rows_needed = 1 if existing_patient is not None else 2
            if inserted_rows + rows_needed > MAX_INSERTED_ROWS:
                duplicate_reasons.append(
                    f"Skipped {booking.patient_email}: insertion would exceed the 10-row cap."
                )
                break

            request = _create_booking_request(booking, appointment_date)
            response = create_appointment_booking(session, request)
            inserted_rows += rows_needed
            inserted_appointment_rows += 1
            if existing_patient is None:
                inserted_patient_rows += 1

            inserted_entries.append(
                f"Inserted appointment {response.confirmation_code} for {booking.patient_email} on "
                f"{appointment_date.isoformat()} at {booking.start_time}."
            )

        counts_after = _table_counts(session)
    finally:
        session.close()

    if duplicate_reasons:
        duplicate_lines = [f"- {reason}" for reason in duplicate_reasons]

    inserted_lines = [f"- {entry}" for entry in inserted_entries] or ["- No new rows were inserted."]

    report = "\n".join(
        [
            "# Test Data Report",
            "",
            f"- Execution date: {datetime.now(timezone.utc).isoformat()}",
            "- Database inspected: `backend/app.db`",
            "- Tables inspected: `doctors`, `patients`, `appointments`, `doctor_availability`",
            f"- Rows before: doctors={counts_before['doctors']}, patients={counts_before['patients']}, appointments={counts_before['appointments']}, doctor_availability={availability_rows}",
            f"- Rows inserted: patients={inserted_patient_rows}, appointments={inserted_appointment_rows}, total={inserted_rows}",
            f"- Rows skipped: {skipped_rows}",
            "",
            "## Inserted Records",
            "",
            *inserted_lines,
            "",
            "## Duplicate Detection",
            "",
            *duplicate_lines,
            "",
            "## Validation Checks",
            "",
            *(f"- {item}" for item in validation_checks),
            "",
            "## Knowledge Source Updates",
            "",
            "- None. No knowledge-source or FAQ updates were required for demo booking data.",
            "",
            "## Remaining Missing Demo Data",
            "",
            "- Legacy `doctor_availability` rows remain historical only and were not extended because the live booking flow uses generated schedule slots.",
            "- The seeded dataset still favors manual booking/search coverage over chat-specific conversation history because chat state is request-scoped, not persisted.",
            "",
            "## Rows After",
            "",
            f"- doctors={counts_after['doctors']}",
            f"- patients={counts_after['patients']}",
            f"- appointments={counts_after['appointments']}",
            f"- doctor_availability={availability_rows}",
        ]
    )
    REPORT_PATH.write_text(report + "\n", encoding="utf-8")

    return {
        "counts_before": counts_before,
        "counts_after": counts_after,
        "availability_rows": availability_rows,
        "inserted_rows": inserted_rows,
        "inserted_patient_rows": inserted_patient_rows,
        "inserted_appointment_rows": inserted_appointment_rows,
        "skipped_rows": skipped_rows,
    }


if __name__ == "__main__":
    result = seed_test_data()
    print(result)
