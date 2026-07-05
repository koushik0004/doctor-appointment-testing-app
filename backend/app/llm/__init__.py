"""Provider-neutral LLM integration boundary.

This package is intentionally inactive in Phase 6.4. It defines only
implementation-ready contracts for a future LLM adapter layer and an inactive
generation orchestrator, and is not wired into the current chat runtime,
workflow engine, retrieval layer, or prompt builder.
"""

from app.llm.adapters import BaseLLMProviderAdapter
from app.llm.config import (
    LLMConfiguration,
    LLMConfigurationLoader,
    LLMConfigurationSettings,
    LLMProviderConfiguration,
    LLMProviderEnvironmentSettings,
    LLMProviderFeatureFlags,
    LLMProviderName,
    get_llm_configuration,
)
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
from app.llm.orchestrator import (
    LLMGenerationOrchestrationRequest,
    LLMGenerationOrchestrationResult,
    LLMGenerationOrchestrator,
)
from app.llm.registry import InMemoryLLMProviderRegistry
from app.llm.service import LLMIntegrationService, LLMIntegrationStatus

__all__ = [
    "BaseLLMProviderAdapter",
    "LLMConfiguration",
    "LLMConfigurationLoader",
    "LLMConfigurationSettings",
    "LLMCitation",
    "LLMFinishReason",
    "LLMGenerationConstraints",
    "LLMGenerationOrchestrationRequest",
    "LLMGenerationOrchestrationResult",
    "LLMGenerationOrchestrator",
    "LLMGenerationRequest",
    "LLMGenerationResponse",
    "LLMIntegrationService",
    "LLMIntegrationStatus",
    "LLMMessage",
    "LLMMessageRole",
    "LLMProvider",
    "LLMProviderConfiguration",
    "LLMProviderCapabilities",
    "LLMProviderDescriptor",
    "LLMProviderEnvironmentSettings",
    "LLMProviderFeatureFlags",
    "LLMProviderName",
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
    "get_llm_configuration",
]
