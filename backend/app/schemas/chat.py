from __future__ import annotations

from enum import Enum
from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.knowledge.documents import (
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
)


class ChatIntent(str, Enum):
    SHOW_DOCTORS_BY_SPECIALIZATION = "SHOW_DOCTORS_BY_SPECIALIZATION"
    SHOW_AVAILABLE_DOCTORS = "SHOW_AVAILABLE_DOCTORS"
    SHOW_DOCTOR_DETAILS = "SHOW_DOCTOR_DETAILS"
    APPOINTMENT_HELP = "APPOINTMENT_HELP"
    CANCEL_APPOINTMENT_HELP = "CANCEL_APPOINTMENT_HELP"
    BOOK_APPOINTMENT = "BOOK_APPOINTMENT"
    CANCEL_APPOINTMENT = "CANCEL_APPOINTMENT"
    APPOINTMENT_CONFIRMATION = "APPOINTMENT_CONFIRMATION"
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


class ChatWorkflowType(str, Enum):
    BOOK_APPOINTMENT = "BOOK_APPOINTMENT"
    CANCEL_APPOINTMENT = "CANCEL_APPOINTMENT"
    APPOINTMENT_CONFIRMATION = "APPOINTMENT_CONFIRMATION"


class ChatWorkflowStatus(str, Enum):
    INPUT_REQUIRED = "INPUT_REQUIRED"
    READY = "READY"
    COMPLETED = "COMPLETED"


class ChatWorkflowDraft(BaseModel):
    doctor_id: int | None = None
    doctor_name: str | None = None
    appointment_date: Date | None = None
    start_time: str | None = None
    appointment_type: str | None = None
    patient_full_name: str | None = None
    patient_email: str | None = None
    patient_phone: str | None = None
    health_description: str | None = None
    appointment_id: int | None = None
    confirmation_code: str | None = None


class ChatWorkflowAppointmentSummary(BaseModel):
    appointment_id: int
    confirmation_code: str
    status: str
    doctor_name: str
    appointment_date: Date
    start_time: str
    end_time: str
    appointment_type: str
    patient_name: str


class ChatWorkflowState(BaseModel):
    workflow_type: ChatWorkflowType
    status: ChatWorkflowStatus
    missing_fields: list[str] = Field(default_factory=list)
    draft: ChatWorkflowDraft = Field(default_factory=ChatWorkflowDraft)


class ChatWorkflowResult(BaseModel):
    workflow_type: ChatWorkflowType
    status: ChatWorkflowStatus
    missing_fields: list[str] = Field(default_factory=list)
    draft: ChatWorkflowDraft = Field(default_factory=ChatWorkflowDraft)
    appointment: ChatWorkflowAppointmentSummary | None = None


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
    current_workflow: ChatWorkflowState | None = None


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


class ChatKnowledgeSource(BaseModel):
    document_id: str
    title: str
    source_type: KnowledgeDocumentSourceType
    source_path: str
    domain: KnowledgeDocumentDomain
    audience: KnowledgeDocumentAudience
    status: KnowledgeDocumentStatus
    matched_terms: list[str] = Field(default_factory=list)
    score: int | None = None


class ChatResponse(BaseModel):
    intent: ChatIntent
    message: str
    data: list[ChatDoctorCard | ChatAvailabilityCard] = Field(default_factory=list)
    search_filters: ChatSearchFilters | None = None
    help_steps: list[str] = Field(default_factory=list)
    knowledge_source: ChatKnowledgeSource | None = None
    response: str = ""
    conversation: ChatConversationContext | None = None
    workflow: ChatWorkflowResult | None = None

    @model_validator(mode="after")
    def _sync_legacy_response(self) -> "ChatResponse":
        if not self.response:
            self.response = self.message
        return self
