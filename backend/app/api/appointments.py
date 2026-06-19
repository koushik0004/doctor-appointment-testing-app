from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.appointment_search import (
    AppointmentSearchRequest,
    AppointmentSearchResponse,
)
from app.schemas.appointment import (
    AppointmentDetailsResponse,
    AppointmentCreateRequest,
    AppointmentCreateResponse,
)
from app.services.appointment_service import (
    create_appointment_booking,
    get_appointment_details,
)
from app.services.appointment_search_service import search_appointments as search_appointment_records

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentCreateResponse, status_code=201)
def create_appointment(
    payload: AppointmentCreateRequest,
    session: Session = Depends(get_db),
) -> AppointmentCreateResponse:
    return create_appointment_booking(session, payload)


@router.get(
    "/search",
    response_model=AppointmentSearchResponse,
    summary="Search appointments",
    description="Search appointments by patient name, email, or phone.",
    responses={
        400: {"description": "At least one search parameter is required."},
        422: {"description": "Invalid query parameter values."},
        500: {"description": "Unexpected server error."},
    },
)
def search_appointments(
    name: str | None = Query(default=None, description="Partial patient name match."),
    email: str | None = Query(default=None, description="Exact patient email match."),
    phone: str | None = Query(default=None, description="Exact patient phone match."),
    session: Session = Depends(get_db),
) -> AppointmentSearchResponse:
    if not any(
        isinstance(value, str) and value.strip()
        for value in (name, email, phone)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one search parameter is required.",
        )

    try:
        request = AppointmentSearchRequest.model_validate(
            {
                "name": name,
                "email": email,
                "phone": phone,
            }
        )
    except ValidationError as exc:
        raise RequestValidationError(
            [
                {
                    **error,
                    "loc": ("query", *error["loc"]),
                }
                for error in exc.errors()
            ]
        ) from exc

    return search_appointment_records(session, request)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentDetailsResponse,
    summary="Get appointment details",
    description="Fetch the appointment record along with doctor and patient details.",
    responses={
        404: {"description": "Appointment not found."},
        500: {"description": "Unexpected server error."},
    },
)
def read_appointment(
    appointment_id: int,
    session: Session = Depends(get_db),
) -> AppointmentDetailsResponse:
    return get_appointment_details(session, appointment_id)
