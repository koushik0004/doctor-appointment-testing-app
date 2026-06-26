from __future__ import annotations

from enum import Enum
from datetime import date as Date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChatIntent(str, Enum):
    SHOW_DOCTORS_BY_SPECIALIZATION = "SHOW_DOCTORS_BY_SPECIALIZATION"
    SHOW_AVAILABLE_DOCTORS = "SHOW_AVAILABLE_DOCTORS"
    SHOW_DOCTOR_DETAILS = "SHOW_DOCTOR_DETAILS"
    APPOINTMENT_HELP = "APPOINTMENT_HELP"
    CANCEL_APPOINTMENT_HELP = "CANCEL_APPOINTMENT_HELP"
    UNKNOWN = "UNKNOWN"


class ChatSearchFilters(BaseModel):
    specialization: str | None = None
    gender: str | None = None
    minimum_fee: int | None = None
    maximum_fee: int | None = None
    date: Date | None = None
    time_preference: str | None = None
    clinic_location: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class ChatDoctorCard(BaseModel):
    doctor_id: int
    doctor_name: str
    specialty: str
    gender: str
    consultation_fee_min: int
    consultation_fee_max: int
    next_available_slot: str
    clinic_name: str
    location: str


class ChatAvailabilityCard(BaseModel):
    doctor_id: int
    doctor_name: str
    specialty: str
    available_date: Date
    available_time: str


class ChatResponse(BaseModel):
    intent: ChatIntent
    message: str
    data: list[ChatDoctorCard | ChatAvailabilityCard] = Field(default_factory=list)
    search_filters: ChatSearchFilters | None = None
    help_steps: list[str] = Field(default_factory=list)
    response: str = ""

    @model_validator(mode="after")
    def _sync_legacy_response(self) -> "ChatResponse":
        if not self.response:
            self.response = self.message
        return self
