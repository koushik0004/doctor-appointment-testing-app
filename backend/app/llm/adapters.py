from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic

from app.llm.interfaces import ProviderRequestT, ProviderResponseT
from app.llm.models import LLMGenerationRequest, LLMGenerationResponse


class BaseLLMProviderAdapter(ABC, Generic[ProviderRequestT, ProviderResponseT]):
    """Shared translation pipeline for future provider-specific adapters."""

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        provider_request = self.translate_request(request)
        provider_response = self.invoke_provider(provider_request)
        canonical_response = self.translate_response(
            provider_response,
            request=request,
        )

        descriptor = self.describe()
        if canonical_response.provider_name is None:
            canonical_response.provider_name = descriptor.provider_name
        if canonical_response.model_name is None:
            canonical_response.model_name = descriptor.default_model_name

        return canonical_response

    @abstractmethod
    def describe(self):
        ...

    @abstractmethod
    def translate_request(self, request: LLMGenerationRequest) -> ProviderRequestT:
        ...

    @abstractmethod
    def invoke_provider(self, request: ProviderRequestT) -> ProviderResponseT:
        ...

    @abstractmethod
    def translate_response(
        self,
        response: ProviderResponseT,
        *,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        ...
