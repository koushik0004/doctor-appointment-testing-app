from __future__ import annotations

from typing import Protocol

from app.llm.models import (
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMProviderDescriptor,
)


class LLMProvider(Protocol):
    """Provider-neutral contract for future provider adapters."""

    def describe(self) -> LLMProviderDescriptor:
        ...

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        ...


class LLMProviderRegistry(Protocol):
    """Lookup boundary for future provider registration and resolution."""

    def list_providers(self) -> list[LLMProviderDescriptor]:
        ...

    def get_provider(self, provider_name: str) -> LLMProvider | None:
        ...
