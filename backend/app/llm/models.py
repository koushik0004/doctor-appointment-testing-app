from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LLMMessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class LLMFinishReason(str, Enum):
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALL = "tool_call"
    CONTENT_FILTER = "content_filter"
    OTHER = "other"


class LLMRequestedModality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


class LLMStructuredOutputMode(str, Enum):
    JSON_OBJECT = "json_object"
    JSON_SCHEMA = "json_schema"


class LLMToolChoiceMode(str, Enum):
    AUTO = "auto"
    NONE = "none"
    REQUIRED = "required"
    NAMED = "named"


class LLMReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LLMStructuredOutputSchema(BaseModel):
    mode: LLMStructuredOutputMode
    name: str | None = None
    schema_definition: dict[str, Any] | None = Field(
        default=None,
        alias="schema",
        serialization_alias="schema",
    )
    strict: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)


class LLMToolDefinition(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    input_schema: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMToolChoice(BaseModel):
    mode: LLMToolChoiceMode = LLMToolChoiceMode.AUTO
    tool_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMToolCall(BaseModel):
    call_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMReasoningConfig(BaseModel):
    effort: LLMReasoningEffort | None = None
    include_summary: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMReasoningResult(BaseModel):
    effort: LLMReasoningEffort | None = None
    summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMStreamingOptions(BaseModel):
    enabled: bool = False
    include_usage: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMStreamingMetadata(BaseModel):
    enabled: bool = False
    chunk_count: int | None = Field(default=None, ge=0)
    terminated_early: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMCitation(BaseModel):
    citation_id: str | None = None
    label: str | None = None
    url: str | None = None
    excerpt: str | None = None
    start_index: int | None = Field(default=None, ge=0)
    end_index: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMMessage(BaseModel):
    role: LLMMessageRole
    content: str = Field(min_length=1)
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMGenerationConstraints(BaseModel):
    max_output_tokens: int | None = Field(default=None, gt=0)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, gt=0.0, le=1.0)
    stop_sequences: list[str] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMGenerationRequest(BaseModel):
    messages: list[LLMMessage] = Field(min_length=1)
    prompt: str | None = None
    system_prompt: str | None = None
    model_name: str | None = None
    constraints: LLMGenerationConstraints = Field(
        default_factory=LLMGenerationConstraints
    )
    requested_modalities: list[LLMRequestedModality] = Field(default_factory=list)
    structured_output: LLMStructuredOutputSchema | None = None
    tools: list[LLMToolDefinition] = Field(default_factory=list)
    tool_choice: LLMToolChoice | None = None
    reasoning: LLMReasoningConfig | None = None
    streaming: LLMStreamingOptions = Field(default_factory=LLMStreamingOptions)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMTokenUsage(BaseModel):
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class LLMGenerationResponse(BaseModel):
    message: LLMMessage
    finish_reason: LLMFinishReason = LLMFinishReason.STOP
    model_name: str | None = None
    provider_name: str | None = None
    usage: LLMTokenUsage | None = None
    structured_output: dict[str, Any] | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    reasoning: LLMReasoningResult | None = None
    streaming: LLMStreamingMetadata | None = None
    citations: list[LLMCitation] = Field(default_factory=list)
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    model_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMProviderCapabilities(BaseModel):
    supports_system_prompt: bool = True
    supports_message_history: bool = True
    supports_streaming: bool = False
    supports_json_output: bool = False
    supports_tool_calls: bool = False
    supports_images: bool = False
    supports_reasoning: bool = False
    supports_citations: bool = False
    supports_audio_input: bool = False
    supports_audio_output: bool = False


class LLMProviderDescriptor(BaseModel):
    provider_name: str = Field(min_length=1)
    default_model_name: str | None = None
    capabilities: LLMProviderCapabilities = Field(
        default_factory=LLMProviderCapabilities
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)
