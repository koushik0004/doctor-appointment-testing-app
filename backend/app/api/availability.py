from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.doctor import AppointmentType
from app.schemas.availability import DoctorAvailabilityResponse
from app.services.availability_service import get_doctor_availability_window

router = APIRouter(prefix="/doctors", tags=["availability"])


@router.get(
    "/{doctor_id}/availability",
    response_model=DoctorAvailabilityResponse,
)
def read_doctor_availability(
    doctor_id: int,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    appointment_type: AppointmentType | None = Query(default=None),
    session: Session = Depends(get_db),
) -> DoctorAvailabilityResponse:
    return get_doctor_availability_window(
        session,
        doctor_id,
        date_from=date_from,
        date_to=date_to,
        appointment_type=appointment_type,
    )
