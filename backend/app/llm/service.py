from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.llm.interfaces import LLMProviderRegistry
from app.llm.models import (
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMProviderDescriptor,
)
from app.llm.runtime_trace import AIRuntimeTraceSession


class LLMIntegrationStatus(BaseModel):
    enabled: bool = False
    connected_provider_names: list[str] = Field(default_factory=list)
    default_provider_name: str | None = None
    reason: str = Field(
        default="LLM integration is not connected to the runtime in this phase."
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMIntegrationService:
    """Inactive architectural boundary for future provider-neutral LLM calls."""

    def __init__(
        self,
        *,
        provider_registry: LLMProviderRegistry,
        default_provider_name: str | None = None,
    ) -> None:
        self._provider_registry = provider_registry
        self._default_provider_name = default_provider_name

    def get_status(self) -> LLMIntegrationStatus:
        default_provider_name = self._default_provider_name
        if default_provider_name is None:
            default_provider_name = self._provider_registry.get_default_provider_name()

        providers = self._provider_registry.list_providers()
        return LLMIntegrationStatus(
            enabled=False,
            connected_provider_names=[
                provider.provider_name for provider in providers
            ],
            default_provider_name=default_provider_name,
        )

    def list_registered_providers(self) -> list[LLMProviderDescriptor]:
        return list(self._provider_registry.list_providers())

    def generate(
        self,
        request: LLMGenerationRequest,
        *,
        provider_name: str | None = None,
        runtime_trace: AIRuntimeTraceSession | None = None,
    ) -> LLMGenerationResponse:
        resolved_provider_name = (
            provider_name
            or self._default_provider_name
            or self._provider_registry.get_default_provider_name()
        )
        if not resolved_provider_name:
            if runtime_trace is not None:
                runtime_trace.mark_llm_not_invoked(
                    "llm_integration",
                    "No provider name was resolved for generation.",
                )
            raise RuntimeError(
                "LLM integration is inactive: no provider name was resolved."
            )

        provider = self._provider_registry.get_provider(resolved_provider_name)
        if provider is None:
            if runtime_trace is not None:
                runtime_trace.mark_llm_not_invoked(
                    "llm_integration",
                    f"Provider '{resolved_provider_name}' is not registered.",
                )
            raise RuntimeError(
                f"LLM integration is inactive: provider '{resolved_provider_name}' is not registered."
            )

        request.metadata.setdefault("ai_runtime_trace_id", runtime_trace.trace_id if runtime_trace is not None else "")
        return provider.generate(request)
