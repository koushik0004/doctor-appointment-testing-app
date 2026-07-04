"""Provider-neutral LLM integration boundary.

This package is intentionally inactive in Phase 6.2. It defines only
implementation-ready contracts for a future LLM adapter layer, including
canonical translation boundaries and an explicit inactive registry, and is not
wired into the current chat runtime, workflow engine, retrieval layer, or
prompt builder.
"""

from app.llm.adapters import BaseLLMProviderAdapter
from app.llm.interfaces import (
    LLMProvider,
    LLMProviderRegistry,
    LLMRequestTranslator,
    LLMResponseTranslator,
)
from app.llm.models import (
    LLMCitation,
    LLMFinishReason,
    LLMGenerationConstraints,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMMessage,
    LLMMessageRole,
    LLMProviderCapabilities,
    LLMProviderDescriptor,
    LLMReasoningConfig,
    LLMReasoningEffort,
    LLMReasoningResult,
    LLMRequestedModality,
    LLMStreamingMetadata,
    LLMStreamingOptions,
    LLMStructuredOutputMode,
    LLMStructuredOutputSchema,
    LLMTokenUsage,
    LLMToolCall,
    LLMToolChoice,
    LLMToolChoiceMode,
    LLMToolDefinition,
)
from app.llm.registry import InMemoryLLMProviderRegistry
from app.llm.service import LLMIntegrationService, LLMIntegrationStatus

__all__ = [
    "BaseLLMProviderAdapter",
    "LLMCitation",
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
    "LLMReasoningConfig",
    "LLMReasoningEffort",
    "LLMReasoningResult",
    "LLMRequestTranslator",
    "LLMRequestedModality",
    "LLMResponseTranslator",
    "LLMStreamingMetadata",
    "LLMStreamingOptions",
    "LLMStructuredOutputMode",
    "LLMStructuredOutputSchema",
    "LLMTokenUsage",
    "LLMToolCall",
    "LLMToolChoice",
    "LLMToolChoiceMode",
    "LLMToolDefinition",
    "InMemoryLLMProviderRegistry",
]
