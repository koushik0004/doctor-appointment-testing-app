from __future__ import annotations

from typing import Any, Protocol, TypeVar

from app.llm.models import (
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMProviderDescriptor,
)


ProviderRequestT = TypeVar("ProviderRequestT")
ProviderResponseT = TypeVar("ProviderResponseT")


class LLMRequestTranslator(Protocol[ProviderRequestT]):
    """Maps canonical generation requests into provider-native payloads."""

    def translate_request(self, request: LLMGenerationRequest) -> ProviderRequestT:
        ...


class LLMResponseTranslator(Protocol[ProviderResponseT]):
    """Maps provider-native responses back into canonical response models."""

    def translate_response(
        self,
        response: ProviderResponseT,
        *,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        ...


class LLMProvider(
    LLMRequestTranslator[Any],
    LLMResponseTranslator[Any],
    Protocol,
):
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

    def get_default_provider_name(self) -> str | None:
        ...
