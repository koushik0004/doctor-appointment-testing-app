from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.availability import DoctorAvailabilityResponse
from app.services.availability_service import get_doctor_available_slots

router = APIRouter(prefix="/doctors", tags=["availability"])


@router.get(
    "/{doctor_id}/availability",
    response_model=DoctorAvailabilityResponse,
)
def read_doctor_availability(
    doctor_id: int,
    date: date = Query(...),
    session: Session = Depends(get_db),
) -> DoctorAvailabilityResponse:
    return get_doctor_available_slots(
        session,
        doctor_id,
        slot_date=date,
    )
