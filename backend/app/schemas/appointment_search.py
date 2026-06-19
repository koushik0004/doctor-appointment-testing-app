from datetime import date
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.doctor import AppointmentType


class AppointmentSearchStatus(str, Enum):
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppointmentSearchRequest(BaseModel):
    name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    phone: str | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def trim_and_normalize_query_params(cls, values: object) -> object:
        if not isinstance(values, dict):
            return values

        normalized = dict(values)

        for field_name in ("name", "email", "phone"):
            raw_value = normalized.get(field_name)
            if isinstance(raw_value, str):
                raw_value = raw_value.strip()
                normalized[field_name] = raw_value or None

        return normalized

    @model_validator(mode="after")
    def validate_at_least_one_search_param(self) -> "AppointmentSearchRequest":
        if not any((self.name, self.email, self.phone)):
            raise ValueError("At least one search parameter is required.")
        return self


class AppointmentSearchResult(BaseModel):
    appointment_id: int
    patient_name: str
    patient_email: EmailStr
    patient_phone: str | None = None
    doctor_name: str
    doctor_specialty: str
    appointment_date: date
    appointment_time: str
    appointment_type: AppointmentType
    status: AppointmentSearchStatus


class AppointmentSearchResponse(BaseModel):
    count: int
    appointments: list[AppointmentSearchResult]
