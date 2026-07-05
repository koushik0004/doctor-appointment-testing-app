from app.llm import (
    LLMConfigurationSettings,
    LLMProviderName,
    LLMRuntimeCompositionRoot,
    LLMRuntimeFacade,
    LLMRuntimeFacadeSnapshot,
)
from app.services.prompt_builder import PromptBuilderService


class StaticTransport:
    def invoke(self, request: dict[str, object]) -> dict[str, object]:
        return dict(request)


class StaticTransportFactory:
    def __init__(self, provider_names: list[str]) -> None:
        self._provider_names = list(provider_names)

    def create_transports(self, configuration) -> dict[str, StaticTransport]:
        del configuration
        return {
            provider_name: StaticTransport() for provider_name in self._provider_names
        }


def _base_settings() -> LLMConfigurationSettings:
    return LLMConfigurationSettings(
        provider=LLMProviderName.OPENAI,
        enabled=True,
        allow_generation=True,
        openai={
            "enabled": True,
            "default_model_name": "gpt-4.1-mini",
            "api_key": "openai-key",
        },
        claude={
            "enabled": False,
        },
    )


def test_runtime_facade_caches_composition_and_exposes_a_save_ready_snapshot():
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(),
        transport_factory=StaticTransportFactory(["openai"]),
    )
    facade = LLMRuntimeFacade(composition_root=root)

    first = facade.compose()
    second = facade.get_composition()
    snapshot = facade.save_integration_boundary()

    assert first is second
    assert isinstance(snapshot, LLMRuntimeFacadeSnapshot)
    assert snapshot.configuration_loaded is True
    assert snapshot.composition_cached is True
    assert snapshot.connected_provider_names == ["openai"]
    assert snapshot.default_provider_name == "openai"
    assert snapshot.selected_provider_name == "openai"
    assert snapshot.activation_status.generation_available is True
    assert snapshot.integration_status.enabled is False


def test_runtime_facade_snapshot_serializes_deterministically():
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(),
            transport_factory=StaticTransportFactory(["openai"]),
        )
    )

    first = facade.snapshot().model_dump(mode="json")
    second = facade.save_integration_boundary().model_dump(mode="json")

    assert first == second
