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


class LLMMessage(BaseModel):
    role: LLMMessageRole
    content: str = Field(min_length=1)
    name: str | None = None
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
    constraints: LLMGenerationConstraints = Field(
        default_factory=LLMGenerationConstraints
    )
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
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMProviderCapabilities(BaseModel):
    supports_system_prompt: bool = True
    supports_message_history: bool = True
    supports_streaming: bool = False
    supports_json_output: bool = False
    supports_tool_calls: bool = False
    supports_images: bool = False


class LLMProviderDescriptor(BaseModel):
    provider_name: str = Field(min_length=1)
    default_model_name: str | None = None
    capabilities: LLMProviderCapabilities = Field(
        default_factory=LLMProviderCapabilities
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)
