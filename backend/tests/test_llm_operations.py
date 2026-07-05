from datetime import datetime

import pytest

from app.llm import (
    AIExecutionMode,
    AIExecutionOwner,
    LLMAuditTrailRecord,
    LLMAuditVisibility,
    LLMCostAggregationWindow,
    LLMCostBreakdown,
    LLMCostRollup,
    LLMConfigurationSettings,
    LLMObservabilityRecord,
    LLMOperationalHealthStatus,
    LLMOperationalReadinessEvaluator,
    LLMOperationalReadinessService,
    LLMProviderName,
    LLMRetryBackoffStrategy,
    LLMRetryPolicy,
    LLMRolloutPolicy,
    LLMRolloutStage,
    LLMTimingBreakdown,
    LLMTimeoutPolicy,
    LLMTokenAccounting,
    LLMTraceContext,
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
        "timeout_seconds": 45.0,
        "max_retries": 2,
        "retry_backoff_seconds": 0.5,
        "openai": {
            "enabled": True,
            "default_model_name": "gpt-4.1-mini",
            "api_key": "openai-key",
            "timeout_seconds": 20.0,
            "max_retries": 3,
            "retry_backoff_seconds": 1.0,
        },
        "claude": {
            "enabled": False,
        },
    }
    payload.update(overrides)
    return LLMConfigurationSettings(**payload)


def test_observability_record_serializes_canonically():
    record = LLMObservabilityRecord(
        event_name="provider_invocation_completed",
        trace=LLMTraceContext(
            request_id="req-1",
            execution_id="exec-1",
            correlation_id="corr-1",
        ),
        timing=LLMTimingBreakdown(
            total_duration_ms=220.5,
            provider_latency_ms=180.0,
            orchestration_duration_ms=20.0,
            prompt_builder_duration_ms=12.0,
            execution_policy_duration_ms=8.5,
        ),
        metadata={"provider": "openai", "shadow": False},
    )

    payload = record.model_dump(mode="json")

    assert payload["trace"]["request_id"] == "req-1"
    assert payload["timing"]["provider_latency_ms"] == 180.0
    assert payload["metadata"]["provider"] == "openai"


def test_token_accounting_computes_total_tokens():
    usage = LLMTokenAccounting(
        provider_name="openai",
        model_name="gpt-4.1-mini",
        prompt_tokens=120,
        completion_tokens=30,
        cached_tokens=10,
        reasoning_tokens=5,
    )

    assert usage.total_tokens == 165
    assert usage.model_dump(mode="json")["total_tokens"] == 165


def test_cost_models_compute_and_roll_up_request_cost():
    request_cost = LLMCostBreakdown(
        provider_name="openai",
        model_name="gpt-4.1-mini",
        prompt_cost_micros=1200,
        completion_cost_micros=800,
        cached_cost_micros=100,
        reasoning_cost_micros=50,
    )
    rollup = LLMCostRollup(
        window=LLMCostAggregationWindow.DAILY,
        request_count=4,
        total_cost_micros=request_cost.request_cost_micros * 4,
        provider_name="openai",
    )

    assert request_cost.request_cost_micros == 2150
    assert rollup.model_dump(mode="json")["window"] == "DAILY"
    assert rollup.total_cost_micros == 8600


def test_retry_policy_validation_rejects_disabled_multi_attempt_policy():
    with pytest.raises(ValueError):
        LLMRetryPolicy(
            enabled=False,
            max_attempts=2,
            backoff_strategy=LLMRetryBackoffStrategy.EXPONENTIAL,
            initial_backoff_seconds=0.5,
        )


def test_timeout_policy_validation_rejects_provider_timeout_above_global():
    with pytest.raises(ValueError):
        LLMTimeoutPolicy(
            global_timeout_seconds=20.0,
            provider_timeout_seconds={"openai": 25.0},
        )


def test_audit_trail_model_preserves_execution_metadata():
    record = LLMAuditTrailRecord(
        request_id="req-10",
        execution_id="exec-10",
        correlation_id="corr-10",
        provider_name="openai",
        model_name="gpt-4.1-mini",
        execution_mode=AIExecutionMode.SHADOW,
        routing_owner=AIExecutionOwner.DETERMINISTIC,
        generation_profile_name="BALANCED",
        visibility=LLMAuditVisibility.REDACTED_CONTENT,
        requested_at=datetime(2026, 7, 5, 10, 0, 0),
        completed_at=datetime(2026, 7, 5, 10, 0, 2),
    )

    payload = record.model_dump(mode="json")

    assert payload["execution_mode"] == "SHADOW"
    assert payload["routing_owner"] == "DETERMINISTIC"
    assert payload["visibility"] == "REDACTED_CONTENT"


def test_rollout_policy_validation_rejects_disabled_percentage_rollout():
    with pytest.raises(ValueError):
        LLMRolloutPolicy(
            stage=LLMRolloutStage.DISABLED,
            enabled=False,
            percentage=20,
        )


def test_operational_readiness_evaluator_reports_healthy_runtime():
    composition = LLMRuntimeCompositionRoot(
        prompt_builder=PromptBuilderService(),
        configuration_settings=_base_settings(),
        transport_factory=StaticTransportFactory(["openai"]),
    ).compose()

    profile = LLMOperationalReadinessEvaluator().evaluate(
        configuration=composition.configuration,
        activation_status=composition.activation_status,
        rollout_policy=LLMRolloutPolicy(
            stage=LLMRolloutStage.SHADOW,
            enabled=True,
            percentage=0,
            shadow_enabled=True,
        ),
    )

    assert profile.health.overall_status == LLMOperationalHealthStatus.HEALTHY
    assert profile.retry_policy.max_attempts == 4
    assert profile.timeout_policy.provider_timeout_seconds["openai"] == 20.0
    assert profile.rollout_policy.stage == LLMRolloutStage.SHADOW


def test_operational_readiness_service_fails_safely_for_invalid_configuration():
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

    result = LLMOperationalReadinessService(composition_root=root).evaluate()

    assert result.composition is None
    assert result.profile.health.overall_status == LLMOperationalHealthStatus.CONFIGURATION_ERROR
    assert result.profile.health.diagnostics[0].code == "configuration_invalid"
