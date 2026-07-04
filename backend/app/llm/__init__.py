"""Provider-neutral LLM integration boundary.

This package is intentionally inactive in Phase 6.1. It defines only
implementation-ready contracts for a future LLM adapter layer and is not wired
into the current chat runtime, workflow engine, retrieval layer, or prompt
builder.
"""

from app.llm.interfaces import LLMProvider, LLMProviderRegistry
from app.llm.models import (
    LLMFinishReason,
    LLMGenerationConstraints,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMMessage,
    LLMMessageRole,
    LLMProviderCapabilities,
    LLMProviderDescriptor,
    LLMTokenUsage,
)
from app.llm.service import LLMIntegrationService, LLMIntegrationStatus

__all__ = [
    "LLMFinishReason",
    "LLMGenerationConstraints",
    "LLMGenerationRequest",
    "LLMGenerationResponse",
    "LLMIntegrationService",
    "LLMIntegrationStatus",
    "LLMMessage",
    "LLMMessageRole",
    "LLMProvider",
    "LLMProviderCapabilities",
    "LLMProviderDescriptor",
    "LLMProviderRegistry",
    "LLMTokenUsage",
]
