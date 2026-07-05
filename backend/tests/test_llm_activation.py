from app.llm import (
    LLMConfigurationLoader,
    LLMConfigurationSettings,
    LLMProviderName,
    LLMRuntimeActivationEvaluator,
    LLMRuntimeActivationService,
    LLMRuntimeCompositionRoot,
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


def _base_settings(**overrides) -> LLMConfigurationSettings:
    payload = {
        "provider": LLMProviderName.OPENAI,
        "enabled": True,
        "allow_generation": True,
        "allow_streaming": True,
        "allow_tool_calling": True,
        "allow_reasoning": True,
        "openai": {
            "enabled": True,
            "default_model_name": "gpt-4.1-mini",
            "api_key": "openai-key",
            "feature_flags": {
                "streaming": True,
                "tool_calls": True,
                "reasoning": True,
            },
        },
        "claude": {
            "enabled": False,
        },
    }
    payload.update(overrides)
    return LLMConfigurationSettings(**payload)


def test_activation_evaluator_reports_inactive_mode_when_llm_disabled():
    configuration = LLMConfigurationLoader().load(
        _base_settings(enabled=False, allow_generation=False)
    )

    status = LLMRuntimeActivationEvaluator().evaluate(
        configuration=configuration,
        adapters={},
        transports={},
    )

    assert status.llm_enabled is False
    assert status.generation_available is False
    assert status.status_reason == "LLM runtime activation is disabled by the LLM_ENABLED flag."
    assert any(diagnostic.code == "llm_disabled" for diagnostic in status.diagnostics)


def test_activation_evaluator_reports_disabled_selected_provider():
    configuration = LLMConfigurationLoader().load(
        _base_settings(
            openai={
                "enabled": False,
            },
            provider=None,
            enabled=False,
            allow_generation=False,
        )
    )
    provider = configuration.get_provider(LLMProviderName.OPENAI)

    status = LLMRuntimeActivationEvaluator().evaluate(
        configuration=configuration,
        adapters={},
        transports={},
    )

    assert provider is not None
    openai_status = next(
        candidate for candidate in status.providers if candidate.provider_name == "openai"
    )
    assert openai_status.provider_enabled is False
    assert any(diagnostic.code == "provider_disabled" for diagnostic in openai_status.diagnostics)


def test_activation_service_fails_safely_for_invalid_configuration():
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=LLMConfigurationSettings(
            provider=LLMProviderName.OPENAI,
            enabled=True,
            allow_generation=True,
            openai={
                "enabled": True,
                "default_model_name": "gpt-4.1-mini",
            },
        ),
    )

    result = LLMRuntimeActivationService(composition_root=root).evaluate()

    assert result.composition is None
    assert result.status.configuration_loaded is False
    assert result.status.configuration_valid is False
    assert result.status.generation_available is False
    assert result.status.diagnostics[0].code == "configuration_invalid"


def test_activation_evaluator_reports_missing_transport_for_enabled_provider():
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(),
    )

    composition = root.compose()

    assert composition.activation_status.selected_provider_healthy is False
    assert composition.activation_status.generation_available is False
    openai_status = next(
        candidate
        for candidate in composition.activation_status.providers
        if candidate.provider_name == "openai"
    )
    assert openai_status.transport_available is False
    assert any(
        diagnostic.code == "transport_unavailable"
        for diagnostic in openai_status.diagnostics
    )


def test_activation_evaluator_reports_successful_activation_state():
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(shadow_mode=True),
        transport_factory=StaticTransportFactory(["openai"]),
    )

    composition = root.compose()
    status = composition.activation_status

    assert status.llm_enabled is True
    assert status.shadow_mode is True
    assert status.selected_provider_name == "openai"
    assert status.selected_provider_healthy is True
    assert status.generation_allowed is True
    assert status.generation_available is True
    assert status.streaming_allowed is True
    assert status.tool_calling_allowed is True
    assert status.reasoning_allowed is True
    assert "shadow mode" in status.status_reason


def test_activation_decisions_are_deterministic_for_equal_inputs():
    settings = _base_settings()
    evaluator = LLMRuntimeActivationEvaluator()
    configuration = LLMConfigurationLoader().load(settings)
    adapters = {"openai": object()}
    transports = {"openai": StaticTransport()}

    first = evaluator.evaluate(
        configuration=configuration,
        adapters=adapters,
        transports=transports,
    )
    second = evaluator.evaluate(
        configuration=configuration,
        adapters=adapters,
        transports=transports,
    )

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
