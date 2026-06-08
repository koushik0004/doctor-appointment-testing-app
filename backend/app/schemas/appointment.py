from datetime import date
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.models.appointment import AppointmentStatus
from app.schemas.doctor import AppointmentType


TimeString = Annotated[str, Field(pattern=r"^\d{2}:\d{2}$")]


class PatientInput(BaseModel):
    full_name: Annotated[str, Field(min_length=2)]
    email: EmailStr
    phone: str | None = None


class AppointmentCreateRequest(BaseModel):
    doctor_id: Annotated[int, Field(gt=0)]
    availability_id: Annotated[int, Field(gt=0)]
    appointment_date: date
    start_time: TimeString
    appointment_type: AppointmentType
    patient: PatientInput
    health_description: str | None = Field(default=None, max_length=500)


class AppointmentCreateResponse(BaseModel):
    id: int
    confirmation_code: str
    status: AppointmentStatus
    doctor_id: int
    patient_id: int
    appointment_date: date
    start_time: str
    end_time: str


class AppointmentDoctorSummary(BaseModel):
    name: str
    specialty: str
    clinic_name: str
    location: str


class AppointmentPatientSummary(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None


class AppointmentConfirmationResponse(BaseModel):
    id: int
    confirmation_code: str
    status: AppointmentStatus
    doctor: AppointmentDoctorSummary
    patient: AppointmentPatientSummary
    appointment_date: date
    start_time: str
    end_time: str
    appointment_type: AppointmentType
    health_description: str | None = None
