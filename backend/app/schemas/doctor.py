from enum import Enum

from pydantic import BaseModel


class AppointmentType(str, Enum):
    IN_PERSON = "IN_PERSON"
    TELEMEDICINE = "TELEMEDICINE"


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str
    rating: float
    review_count: int
    clinic_name: str
    location: str
    consultation_fee_min: int
    consultation_fee_max: int
    next_available_slot: str
    appointment_types: list[str]
    languages: list[str]
    description: str
    image_url: str


class DoctorListResponse(BaseModel):
    items: list[DoctorResponse]
    total: int
