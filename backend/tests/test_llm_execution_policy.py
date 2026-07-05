from app.llm import (
    AIExecutionFallbackStrategy,
    AIExecutionMode,
    AIExecutionOwner,
    AIExecutionPolicyEvaluator,
    AIExecutionPolicyRequest,
    LLMConfigurationSettings,
    LLMProviderName,
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
        "shadow_mode": False,
        "openai": {
            "enabled": True,
            "default_model_name": "gpt-4.1-mini",
            "api_key": "openai-key",
        },
        "claude": {
            "enabled": False,
        },
    }
    payload.update(overrides)
    return LLMConfigurationSettings(**payload)


def _activation_status(
    *,
    enabled: bool = True,
    shadow_mode: bool = False,
    selected_provider: LLMProviderName | None = LLMProviderName.OPENAI,
    provider_enabled: bool = True,
    transport_available: bool = True,
):
    root = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(
            provider=selected_provider,
            enabled=enabled,
            allow_generation=enabled,
            shadow_mode=shadow_mode,
            openai={
                "enabled": provider_enabled,
                "default_model_name": "gpt-4.1-mini",
                "api_key": "openai-key" if provider_enabled else None,
            },
        ),
        transport_factory=(
            StaticTransportFactory(["openai"]) if transport_available else StaticTransportFactory([])
        ),
    )
    return root.compose().activation_status


def test_execution_policy_preserves_workflow_ownership():
    decision = AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(
            preferred_mode=AIExecutionMode.SHADOW,
            intent_name="BOOK_APPOINTMENT",
        ),
        activation_status=_activation_status(enabled=True, shadow_mode=True),
    )

    assert decision.execution_mode == AIExecutionMode.WORKFLOW_ONLY
    assert decision.primary_owner == AIExecutionOwner.WORKFLOW
    assert decision.should_execute_workflow is True
    assert decision.should_execute_llm is False


def test_execution_policy_selects_knowledge_before_deterministic_fallback():
    decision = AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(
            preferred_mode=AIExecutionMode.DETERMINISTIC_ONLY,
            knowledge_eligible=True,
            knowledge_match_available=True,
        ),
        activation_status=_activation_status(enabled=False, transport_available=False),
    )

    assert decision.execution_mode == AIExecutionMode.KNOWLEDGE_ONLY
    assert decision.primary_owner == AIExecutionOwner.KNOWLEDGE
    assert decision.should_execute_knowledge is True
    assert decision.should_execute_deterministic is False


def test_execution_policy_keeps_deterministic_as_default_when_llm_is_available():
    decision = AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(),
        activation_status=_activation_status(enabled=True, transport_available=True),
    )

    assert decision.execution_mode == AIExecutionMode.DETERMINISTIC_ONLY
    assert decision.primary_owner == AIExecutionOwner.DETERMINISTIC
    assert decision.should_execute_deterministic is True
    assert decision.should_execute_llm is False


def test_execution_policy_enables_shadow_mode_without_changing_official_owner():
    decision = AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(preferred_mode=AIExecutionMode.SHADOW),
        activation_status=_activation_status(enabled=True, shadow_mode=True),
    )

    assert decision.execution_mode == AIExecutionMode.SHADOW
    assert decision.primary_owner == AIExecutionOwner.DETERMINISTIC
    assert decision.official_response_owner == AIExecutionOwner.DETERMINISTIC
    assert decision.should_execute_shadow is True
    assert decision.should_execute_llm is True


def test_execution_policy_falls_back_when_no_routable_provider_is_available():
    decision = AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(preferred_mode=AIExecutionMode.LLM_ONLY),
        activation_status=_activation_status(
            enabled=True,
            selected_provider=None,
            provider_enabled=False,
            transport_available=False,
        ),
    )

    assert decision.execution_mode == AIExecutionMode.DETERMINISTIC_ONLY
    assert decision.fallback_strategy == AIExecutionFallbackStrategy.USE_DETERMINISTIC
    assert decision.fallback_owner == AIExecutionOwner.DETERMINISTIC
    assert decision.should_execute_llm is False


def test_execution_policy_falls_back_from_hybrid_to_knowledge_when_activation_is_unavailable():
    decision = AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(
            preferred_mode=AIExecutionMode.HYBRID,
            knowledge_eligible=True,
            knowledge_match_available=True,
        ),
        activation_status=_activation_status(enabled=False, transport_available=False),
    )

    assert decision.execution_mode == AIExecutionMode.KNOWLEDGE_ONLY
    assert decision.fallback_strategy == AIExecutionFallbackStrategy.USE_KNOWLEDGE
    assert decision.fallback_owner == AIExecutionOwner.KNOWLEDGE


def test_execution_decision_serializes_canonically():
    decision = AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(preferred_mode=AIExecutionMode.LLM_ONLY),
        activation_status=_activation_status(enabled=True, transport_available=True),
    )

    payload = decision.model_dump(mode="json")

    assert payload["execution_mode"] == "LLM_ONLY"
    assert payload["primary_owner"] == "LLM"
    assert payload["activation"]["selected_provider_name"] == "openai"


def test_execution_policy_is_deterministic_for_equal_inputs():
    evaluator = AIExecutionPolicyEvaluator()
    request = AIExecutionPolicyRequest(
        preferred_mode=AIExecutionMode.SHADOW,
        knowledge_eligible=True,
        knowledge_match_available=True,
    )
    activation_status = _activation_status(enabled=True, shadow_mode=True)

    first = evaluator.evaluate(request=request, activation_status=activation_status)
    second = evaluator.evaluate(request=request, activation_status=activation_status)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_composed_execution_policy_service_uses_runtime_activation_status():
    composition = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(enabled=True, shadow_mode=True),
        transport_factory=StaticTransportFactory(["openai"]),
    ).compose()

    result = composition.execution_policy_service.evaluate(
        AIExecutionPolicyRequest(preferred_mode=AIExecutionMode.SHADOW)
    )

    assert composition.execution_policy is not None
    assert result.decision.execution_mode == AIExecutionMode.SHADOW
    assert result.decision.activation.shadow_mode is True
