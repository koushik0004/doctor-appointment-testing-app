from __future__ import annotations

from app.llm import (
    AIExecutionMode,
    AIExecutionPolicyEvaluator,
    AIExecutionPolicyRequest,
    LLMConfigurationSettings,
    LLMGenerationOrchestrationRequest,
    LLMProviderName,
    LLMRuntimeCompositionRoot,
    LLMRuntimeResponseEligibilityEvaluator,
    LLMRuntimeResponseEligibilityRequest,
    LLMRuntimeResponseEligibilityStatus,
    LLMRuntimeResponseValidationResult,
    LLMRuntimeResponseValidationStatus,
    LLMRuntimeResponseValidationIssue,
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
        return {provider_name: StaticTransport() for provider_name in self._provider_names}


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


def _policy_decision(*, intent_name: str | None = None):
    composition = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(),
        transport_factory=StaticTransportFactory(["openai"]),
    ).compose()
    return AIExecutionPolicyEvaluator().evaluate(
        request=AIExecutionPolicyRequest(
            preferred_mode=AIExecutionMode.LLM_ONLY,
            intent_name=intent_name,
        ),
        activation_status=composition.activation_status,
    )


def _validation_result(*, is_valid: bool = True) -> LLMRuntimeResponseValidationResult:
    return LLMRuntimeResponseValidationResult(
        request_id="eligibility-1",
        status=(
            LLMRuntimeResponseValidationStatus.VALID
            if is_valid
            else LLMRuntimeResponseValidationStatus.INVALID
        ),
        is_valid=is_valid,
        issues=(
            []
            if is_valid
            else [
                LLMRuntimeResponseValidationIssue(
                    code="invalid_runtime_response",
                    path="validation_result",
                    message="Invalid runtime response.",
                )
            ]
        ),
        diagnostics={"issue_count": 0 if is_valid else 1},
    )


def _orchestration_request(*, active_intent: str | None) -> LLMGenerationOrchestrationRequest:
    return LLMGenerationOrchestrationRequest(
        user_message="Hello there",
        active_intent=active_intent,
        provider_name="openai",
    )


def test_runtime_response_eligibility_accepts_low_risk_conversation():
    evaluator = LLMRuntimeResponseEligibilityEvaluator()
    result = evaluator.evaluate(
        LLMRuntimeResponseEligibilityRequest(
            request_id="eligibility-1",
            policy_decision=_policy_decision(intent_name=None),
            validation_result=_validation_result(),
            orchestration_request=_orchestration_request(active_intent="UNKNOWN"),
        )
    )

    assert result.status is LLMRuntimeResponseEligibilityStatus.ELIGIBLE
    assert result.is_eligible is True
    assert result.issues == []
    assert result.fallback_reason is None
    assert result.diagnostics["low_risk_intent"] is True


def test_runtime_response_eligibility_rejects_booking_request():
    evaluator = LLMRuntimeResponseEligibilityEvaluator()
    result = evaluator.evaluate(
        LLMRuntimeResponseEligibilityRequest(
            request_id="eligibility-2",
            policy_decision=_policy_decision(intent_name=None),
            validation_result=_validation_result(),
            orchestration_request=_orchestration_request(active_intent="BOOK_APPOINTMENT"),
        )
    )

    assert result.status is LLMRuntimeResponseEligibilityStatus.INELIGIBLE
    assert result.is_eligible is False
    assert result.fallback_reason is not None
    assert any(issue.code == "non_eligible_intent" for issue in result.issues)


def test_runtime_response_eligibility_rejects_cancellation_request():
    evaluator = LLMRuntimeResponseEligibilityEvaluator()
    result = evaluator.evaluate(
        LLMRuntimeResponseEligibilityRequest(
            request_id="eligibility-3",
            policy_decision=_policy_decision(intent_name=None),
            validation_result=_validation_result(),
            orchestration_request=_orchestration_request(active_intent="CANCEL_APPOINTMENT"),
        )
    )

    assert result.status is LLMRuntimeResponseEligibilityStatus.INELIGIBLE
    assert result.is_eligible is False
    assert result.fallback_reason is not None
    assert any(issue.code == "non_eligible_intent" for issue in result.issues)


def test_runtime_response_eligibility_rejects_invalid_validation_result():
    evaluator = LLMRuntimeResponseEligibilityEvaluator()
    result = evaluator.evaluate(
        LLMRuntimeResponseEligibilityRequest(
            request_id="eligibility-4",
            policy_decision=_policy_decision(intent_name="APPOINTMENT_HELP"),
            validation_result=_validation_result(is_valid=False),
            orchestration_request=_orchestration_request(active_intent="APPOINTMENT_HELP"),
        )
    )

    assert result.status is LLMRuntimeResponseEligibilityStatus.INELIGIBLE
    assert result.is_eligible is False
    assert result.issues[0].code == "invalid_runtime_response"
    assert result.diagnostics["validation_is_valid"] is False


def test_runtime_response_eligibility_serializes_deterministically():
    evaluator = LLMRuntimeResponseEligibilityEvaluator()
    request = LLMRuntimeResponseEligibilityRequest(
        request_id="eligibility-5",
        policy_decision=_policy_decision(intent_name="APPOINTMENT_HELP"),
        validation_result=_validation_result(),
        orchestration_request=_orchestration_request(active_intent="APPOINTMENT_HELP"),
    )

    first = evaluator.evaluate(request).model_dump(mode="json")
    second = evaluator.evaluate(request).model_dump(mode="json")

    assert first == second
