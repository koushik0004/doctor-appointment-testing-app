from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.appointment import (
    AppointmentConfirmationResponse,
    AppointmentCreateRequest,
    AppointmentCreateResponse,
)
from app.services.appointment_service import (
    create_appointment_booking,
    get_appointment_confirmation,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentCreateResponse, status_code=201)
def create_appointment(
    payload: AppointmentCreateRequest,
    session: Session = Depends(get_db),
) -> AppointmentCreateResponse:
    return create_appointment_booking(session, payload)


@router.get("/{appointment_id}", response_model=AppointmentConfirmationResponse)
def read_appointment(
    appointment_id: int,
    session: Session = Depends(get_db),
) -> AppointmentConfirmationResponse:
    return get_appointment_confirmation(session, appointment_id)
