from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient


def get_patient_by_email(session: Session, email: str) -> Patient | None:
    statement = select(Patient).where(Patient.email == email)
    return session.scalars(statement).first()


def create_patient(session: Session, patient: Patient) -> Patient:
    session.add(patient)
    session.flush()
    session.refresh(patient)
    return patient
