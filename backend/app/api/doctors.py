from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.doctor import AppointmentType, DoctorListResponse, DoctorResponse
from app.services.doctor_service import get_doctor, list_doctors

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=DoctorListResponse)
def read_doctors(
    specialty: str | None = Query(default=None),
    appointment_type: AppointmentType | None = Query(default=None),
    gender: str | None = Query(default=None),
    location: str | None = Query(default=None),
    minimum_fee: int | None = Query(default=None, ge=0),
    maximum_fee: int | None = Query(default=None, ge=0),
    session: Session = Depends(get_db),
) -> DoctorListResponse:
    return list_doctors(
        session,
        specialty=specialty,
        appointment_type=appointment_type,
        gender=gender,
        location=location,
        minimum_fee=minimum_fee,
        maximum_fee=maximum_fee,
    )


@router.get("/{doctor_id}", response_model=DoctorResponse)
def read_doctor(
    doctor_id: int,
    session: Session = Depends(get_db),
) -> DoctorResponse:
    return get_doctor(session, doctor_id)
