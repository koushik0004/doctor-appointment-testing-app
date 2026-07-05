from __future__ import annotations

from collections.abc import Iterable

from app.llm.interfaces import LLMProvider
from app.llm.models import LLMProviderDescriptor


class InMemoryLLMProviderRegistry:
    """Inactive explicit registry for future adapter resolution."""

    def __init__(
        self,
        providers: Iterable[LLMProvider] = (),
        *,
        default_provider_name: str | None = None,
    ) -> None:
        self._providers: dict[str, LLMProvider] = {}
        self._default_provider_name = default_provider_name

        for provider in providers:
            self.register(provider)

    def register(self, provider: LLMProvider) -> None:
        descriptor = provider.describe()
        provider_name = descriptor.provider_name
        if provider_name in self._providers:
            raise ValueError(f"Provider '{provider_name}' is already registered.")
        self._providers[provider_name] = provider

    def list_providers(self) -> list[LLMProviderDescriptor]:
        return [provider.describe() for provider in self._providers.values()]

    def get_provider(self, provider_name: str) -> LLMProvider | None:
        return self._providers.get(provider_name)

    def get_default_provider_name(self) -> str | None:
        return self._default_provider_name
