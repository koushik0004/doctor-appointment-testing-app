from __future__ import annotations

from enum import Enum
from datetime import date as Date
from typing import Literal

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


class ChatRoutingTarget(str, Enum):
    DETERMINISTIC_ENGINE = "DETERMINISTIC_ENGINE"
    WORKFLOW_ENGINE = "WORKFLOW_ENGINE"
    FUTURE_AI_LAYER = "FUTURE_AI_LAYER"


class ChatConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"


class ChatConversationHistoryMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    text: str = Field(min_length=1, max_length=2000)
    intent: ChatIntent | None = None
    search_filters: ChatSearchFilters | None = None
    selected_doctor_id: int | None = None
    selected_doctor_name: str | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class ChatConversationContext(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=100)
    status: ChatConversationStatus = ChatConversationStatus.ACTIVE
    turn_count: int = Field(default=0, ge=0)
    last_intent: ChatIntent | None = None
    active_filters: ChatSearchFilters | None = None
    selected_doctor_id: int | None = None
    selected_doctor_name: str | None = None
    last_user_message: str | None = None
    last_assistant_message: str | None = None
    routed_to: ChatRoutingTarget = ChatRoutingTarget.DETERMINISTIC_ENGINE


class ChatConversationRequest(BaseModel):
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)
    context: ChatConversationContext | None = None
    history: list[ChatConversationHistoryMessage] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    conversation: ChatConversationRequest | None = None

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
    conversation: ChatConversationContext | None = None

    @model_validator(mode="after")
    def _sync_legacy_response(self) -> "ChatResponse":
        if not self.response:
            self.response = self.message
        return self
