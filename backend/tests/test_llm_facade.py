from app.llm import (
    AIExecutionOwner,
    InlineLLMShadowExecutionRunner,
    LLMConfigurationSettings,
    LLMProviderName,
    LLMRuntimeCompositionRoot,
    LLMRuntimeFacade,
    LLMRuntimeFacadeSnapshot,
    LLMShadowModeRequest,
    LLMShadowModeStatus,
)
from app.services.prompt_builder import PromptBuilderService


class StaticTransport:
    def __init__(self, response: dict[str, object]) -> None:
        self._response = dict(response)
        self.calls: list[dict[str, object]] = []

    def invoke(self, request: dict[str, object]) -> dict[str, object]:
        self.calls.append(request)
        return dict(self._response)


class FailingTransport:
    def invoke(self, request: dict[str, object]) -> dict[str, object]:
        del request
        raise RuntimeError("transport failure")


class StaticTransportFactory:
    def __init__(self, provider_transports: dict[str, object]) -> None:
        self._provider_transports = dict(provider_transports)

    def create_transports(self, configuration) -> dict[str, object]:
        del configuration
        return dict(self._provider_transports)


def _base_settings(*, shadow_mode: bool = False) -> LLMConfigurationSettings:
    return LLMConfigurationSettings(
        provider=LLMProviderName.OPENAI,
        enabled=True,
        allow_generation=True,
        shadow_mode=shadow_mode,
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
        transport_factory=StaticTransportFactory(
            {
                "openai": StaticTransport(
                    {
                        "content": "shadow",
                        "finish_reason": "stop",
                        "model": "gpt-4.1-mini",
                    }
                )
            }
        ),
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
    assert snapshot.shadow_execution_count == 0
    assert snapshot.last_shadow_status is None


def test_runtime_facade_snapshot_serializes_deterministically():
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(),
            transport_factory=StaticTransportFactory(
                {
                    "openai": StaticTransport(
                        {
                            "content": "shadow",
                            "finish_reason": "stop",
                            "model": "gpt-4.1-mini",
                        }
                    )
                }
            ),
        )
    )

    first = facade.snapshot().model_dump(mode="json")
    second = facade.save_integration_boundary().model_dump(mode="json")

    assert first == second


def test_runtime_facade_executes_shadow_mode_and_captures_diagnostics():
    transport = StaticTransport(
        {
            "content": "Hidden LLM answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
            "usage": {
                "prompt_tokens": 14,
                "completion_tokens": 6,
                "total_tokens": 20,
            },
        }
    )
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(shadow_mode=True),
            transport_factory=StaticTransportFactory({"openai": transport}),
        ),
        shadow_execution_runner=InlineLLMShadowExecutionRunner(),
    )

    dispatch = facade.run_shadow_mode(
        LLMShadowModeRequest(
            correlation_id="conv-1",
            user_message="What payment methods do you accept?",
            official_response_owner=AIExecutionOwner.DETERMINISTIC,
            official_intent_name="UNKNOWN",
            knowledge_eligible=True,
            knowledge_match_available=False,
            conversation_state={
                "conversation_id": "conv-1",
                "history": [{"role": "user", "text": "What payment methods do you accept?"}],
            },
        ),
        asynchronous=False,
    )

    assert dispatch.decision.should_execute_shadow is True
    assert dispatch.diagnostic is not None
    assert dispatch.diagnostic.status is LLMShadowModeStatus.SUCCEEDED
    assert dispatch.diagnostic.provider_name == "openai"
    assert dispatch.diagnostic.model_name == "gpt-4.1-mini"
    assert dispatch.diagnostic.token_accounting is not None
    assert dispatch.diagnostic.token_accounting.total_tokens == 20
    assert dispatch.diagnostic.observability.metadata["shadow_mode"] is True
    assert dispatch.diagnostic.audit_record.correlation_id == "conv-1"
    assert len(transport.calls) == 1
    assert facade.snapshot().shadow_execution_count == 1
    assert facade.snapshot().last_shadow_status == "SUCCEEDED"


def test_runtime_facade_skips_shadow_execution_when_shadow_mode_is_disabled():
    transport = StaticTransport(
        {
            "content": "Hidden LLM answer",
            "finish_reason": "stop",
            "model": "gpt-4.1-mini",
        }
    )
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(shadow_mode=False),
            transport_factory=StaticTransportFactory({"openai": transport}),
        ),
        shadow_execution_runner=InlineLLMShadowExecutionRunner(),
    )

    dispatch = facade.run_shadow_mode(
        LLMShadowModeRequest(
            correlation_id="conv-2",
            user_message="Hello",
            official_response_owner=AIExecutionOwner.DETERMINISTIC,
            official_intent_name="UNKNOWN",
        ),
        asynchronous=False,
    )

    assert dispatch.decision.should_execute_shadow is False
    assert dispatch.diagnostic is not None
    assert dispatch.diagnostic.status is LLMShadowModeStatus.SKIPPED
    assert transport.calls == []


def test_runtime_facade_records_shadow_failures_without_raising():
    facade = LLMRuntimeFacade(
        composition_root=LLMRuntimeCompositionRoot(
            prompt_builder=PromptBuilderService(),
            configuration_settings=_base_settings(shadow_mode=True),
            transport_factory=StaticTransportFactory({"openai": FailingTransport()}),
        ),
        shadow_execution_runner=InlineLLMShadowExecutionRunner(),
    )

    dispatch = facade.run_shadow_mode(
        LLMShadowModeRequest(
            correlation_id="conv-3",
            user_message="Hello",
            official_response_owner=AIExecutionOwner.DETERMINISTIC,
            official_intent_name="UNKNOWN",
        ),
        asynchronous=False,
    )

    assert dispatch.decision.should_execute_shadow is True
    assert dispatch.diagnostic is not None
    assert dispatch.diagnostic.status is LLMShadowModeStatus.FAILED
    assert dispatch.diagnostic.error_message is not None
    assert facade.get_last_shadow_diagnostic() is not None
    assert facade.get_last_shadow_diagnostic().status is LLMShadowModeStatus.FAILED
