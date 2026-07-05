from copy import deepcopy

from app.llm import (
    AIExecutionMode,
    AIExecutionPolicyRequest,
    InactiveLLMProviderTransportFactory,
    LLMConfiguration,
    LLMConfigurationLoader,
    LLMConfigurationSettings,
    LLMGenerationOrchestrationRequest,
    LLMGenerationRequest,
    LLMMessage,
    LLMMessageRole,
    LLMProviderName,
    LLMRuntimeCompositionRoot,
)
from app.services.prompt_builder import PromptBuilderService


class CountingConfigurationLoader(LLMConfigurationLoader):
    def __init__(self) -> None:
        self.load_calls = 0

    def load(
        self,
        settings: LLMConfigurationSettings | None = None,
    ) -> LLMConfiguration:
        self.load_calls += 1
        return super().load(settings)


class RecordingTransport:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def invoke(self, request: dict[str, object]) -> dict[str, object]:
        self.calls.append(deepcopy(request))
        return deepcopy(self.response)


class StaticTransportFactory:
    def __init__(self, transports: dict[str, RecordingTransport]) -> None:
        self.transports = transports
        self.calls = 0

    def create_transports(self, configuration) -> dict[str, RecordingTransport]:
        self.calls += 1
        del configuration
        return dict(self.transports)


def _make_settings() -> LLMConfigurationSettings:
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
            "enabled": True,
            "default_model_name": "claude-sonnet",
            "api_key": "claude-key",
        },
        gemini={
            "enabled": False,
        },
    )


def test_composition_root_loads_configuration_once_and_caches_graph():
    loader = CountingConfigurationLoader()
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_loader=loader,
        configuration_settings=_make_settings(),
    )

    first = root.compose()
    second = root.compose()

    assert loader.load_calls == 1
    assert first is second


def test_composition_root_registers_only_enabled_providers_and_preserves_default():
    composition = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_make_settings(),
    ).compose()

    assert composition.default_provider_name == "openai"
    assert list(composition.adapters.keys()) == ["openai", "claude"]
    assert composition.activation_status.selected_provider_name == "openai"
    assert [provider.provider_name for provider in composition.provider_registry.list_providers()] == [
        "openai",
        "claude",
    ]
    assert composition.provider_registry.get_provider("gemini") is None
    assert composition.llm_integration_service.get_status().default_provider_name == "openai"
    assert composition.execution_policy is not None
    assert composition.operational_readiness is not None


def test_composition_root_injects_transports_into_created_adapters():
    openai_transport = RecordingTransport(
        {
            "content": "Echo: hello",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 2,
                "total_tokens": 12,
            },
        }
    )
    transport_factory = StaticTransportFactory({"openai": openai_transport})
    composition = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_make_settings(),
        transport_factory=transport_factory,
    ).compose()

    response = composition.adapters["openai"].generate(
        LLMGenerationRequest(
            messages=[LLMMessage(role=LLMMessageRole.USER, content="hello")]
        )
    )

    assert transport_factory.calls == 1
    assert len(openai_transport.calls) == 1
    assert openai_transport.calls[0]["model"] == "gpt-4.1-mini"
    assert composition.activation_status.generation_available is True
    assert response.provider_name == "openai"
    assert response.message.content == "Echo: hello"


def test_composition_root_keeps_enabled_providers_inactive_without_transports():
    composition = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_make_settings(),
        transport_factory=InactiveLLMProviderTransportFactory(),
    ).compose()

    try:
        composition.llm_integration_service.generate(
            LLMGenerationRequest(
                messages=[LLMMessage(role=LLMMessageRole.USER, content="Hello")]
            )
        )
    except RuntimeError as exc:
        assert "inactive" in str(exc)
    else:
        raise AssertionError("Expected composed service to remain inactive without transports.")


def test_composition_root_composes_orchestrator_with_explicit_dependencies():
    composition = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=LLMConfigurationSettings(),
    ).compose()

    assert composition.orchestrator._prompt_builder is composition.prompt_builder
    assert composition.orchestrator._llm_integration_service is composition.llm_integration_service
    assert composition.llm_integration_service.get_status().connected_provider_names == []
    assert (
        composition.execution_policy_service.evaluate(
            AIExecutionPolicyRequest(preferred_mode=AIExecutionMode.DETERMINISTIC_ONLY)
        ).decision.execution_mode
        == AIExecutionMode.DETERMINISTIC_ONLY
    )
    assert (
        composition.operational_readiness_service.evaluate().profile.health.overall_status
        == "UNAVAILABLE"
    )

    try:
        composition.orchestrator.generate(
            LLMGenerationOrchestrationRequest(user_message="Hello")
        )
    except RuntimeError as exc:
        assert "inactive" in str(exc)
    else:
        raise AssertionError("Expected composed orchestrator to remain inactive.")
