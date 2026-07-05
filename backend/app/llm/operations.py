from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.llm.activation import LLMActivationDiagnostic, LLMRuntimeActivationStatus
from app.llm.config import LLMConfiguration
from app.llm.execution_policy import AIExecutionMode, AIExecutionOwner

if TYPE_CHECKING:
    from app.llm.composition import LLMRuntimeComposition, LLMRuntimeCompositionRoot


class LLMOperationalHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"


class LLMRetryBackoffStrategy(str, Enum):
    NONE = "NONE"
    EXPONENTIAL = "EXPONENTIAL"


class LLMAuditVisibility(str, Enum):
    NONE = "NONE"
    METADATA_ONLY = "METADATA_ONLY"
    REDACTED_CONTENT = "REDACTED_CONTENT"
    FULL_CONTENT = "FULL_CONTENT"


class LLMRolloutStage(str, Enum):
    DISABLED = "DISABLED"
    SHADOW = "SHADOW"
    LIMITED = "LIMITED"
    PROVIDER_TARGETED = "PROVIDER_TARGETED"
    GRADUAL = "GRADUAL"
    GENERAL_AVAILABILITY = "GENERAL_AVAILABILITY"


class LLMCostAggregationWindow(str, Enum):
    REQUEST = "REQUEST"
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"


class LLMTraceContext(BaseModel):
    request_id: str = Field(min_length=1)
    execution_id: str = Field(min_length=1)
    correlation_id: str | None = None
    trace_id: str | None = None
    parent_execution_id: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMTimingBreakdown(BaseModel):
    total_duration_ms: float = Field(default=0.0, ge=0)
    provider_latency_ms: float = Field(default=0.0, ge=0)
    orchestration_duration_ms: float = Field(default=0.0, ge=0)
    prompt_builder_duration_ms: float = Field(default=0.0, ge=0)
    execution_policy_duration_ms: float = Field(default=0.0, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMObservabilityRecord(BaseModel):
    event_name: str = Field(min_length=1)
    trace: LLMTraceContext
    timing: LLMTimingBreakdown = Field(default_factory=LLMTimingBreakdown)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMObservabilityPolicy(BaseModel):
    structured_logging: bool = True
    request_tracing: bool = True
    execution_tracing: bool = True
    correlation_ids: bool = True
    provider_latency: bool = True
    orchestration_timing: bool = True
    prompt_builder_timing: bool = True
    execution_policy_timing: bool = True

    model_config = ConfigDict(frozen=True)


class LLMTokenAccounting(BaseModel):
    provider_name: str | None = None
    model_name: str | None = None
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    cached_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_total_tokens(self) -> LLMTokenAccounting:
        computed_total = (
            self.prompt_tokens
            + self.completion_tokens
            + self.cached_tokens
            + self.reasoning_tokens
        )
        if self.total_tokens is None:
            self.total_tokens = computed_total
            return self
        if self.total_tokens != computed_total:
            raise ValueError(
                "total_tokens must equal the sum of prompt, completion, cached, and reasoning tokens."
            )
        return self


class LLMCostBreakdown(BaseModel):
    provider_name: str | None = None
    model_name: str | None = None
    currency: str = Field(default="USD", min_length=1)
    prompt_cost_micros: int = Field(default=0, ge=0)
    completion_cost_micros: int = Field(default=0, ge=0)
    cached_cost_micros: int = Field(default=0, ge=0)
    reasoning_cost_micros: int = Field(default=0, ge=0)
    request_cost_micros: int | None = Field(default=None, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_request_cost(self) -> LLMCostBreakdown:
        computed_total = (
            self.prompt_cost_micros
            + self.completion_cost_micros
            + self.cached_cost_micros
            + self.reasoning_cost_micros
        )
        if self.request_cost_micros is None:
            self.request_cost_micros = computed_total
            return self
        if self.request_cost_micros != computed_total:
            raise ValueError(
                "request_cost_micros must equal the sum of prompt, completion, cached, and reasoning cost micros."
            )
        return self


class LLMCostRollup(BaseModel):
    window: LLMCostAggregationWindow
    currency: str = Field(default="USD", min_length=1)
    request_count: int = Field(default=0, ge=0)
    total_cost_micros: int = Field(default=0, ge=0)
    provider_name: str | None = None
    model_name: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMHealthDiagnostic(BaseModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    status: LLMOperationalHealthStatus
    provider_name: str | None = None
    blocking: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMProviderHealthReport(BaseModel):
    provider_name: str
    selected: bool = False
    status: LLMOperationalHealthStatus
    generation_available: bool = False
    reason: str = Field(min_length=1)
    diagnostics: list[LLMHealthDiagnostic] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMOperationalHealthReport(BaseModel):
    overall_status: LLMOperationalHealthStatus
    selected_provider_name: str | None = None
    overall_reason: str = Field(min_length=1)
    providers: list[LLMProviderHealthReport] = Field(default_factory=list)
    diagnostics: list[LLMHealthDiagnostic] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMProviderRetryPolicy(BaseModel):
    provider_name: str = Field(min_length=1)
    enabled: bool = False
    max_attempts: int = Field(default=1, ge=1)
    backoff_strategy: LLMRetryBackoffStrategy = LLMRetryBackoffStrategy.NONE
    initial_backoff_seconds: float = Field(default=0.0, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRetryPolicy(BaseModel):
    enabled: bool = False
    max_attempts: int = Field(default=1, ge=1)
    backoff_strategy: LLMRetryBackoffStrategy = LLMRetryBackoffStrategy.NONE
    initial_backoff_seconds: float = Field(default=0.0, ge=0)
    max_backoff_seconds: float | None = Field(default=None, gt=0)
    jitter_enabled: bool = False
    retryable_error_codes: list[str] = Field(default_factory=list)
    provider_policies: list[LLMProviderRetryPolicy] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_retry_policy(self) -> LLMRetryPolicy:
        if not self.enabled and self.max_attempts != 1:
            raise ValueError("Retry policy cannot disable retries while max_attempts is greater than 1.")
        if self.max_attempts == 1:
            if self.backoff_strategy is not LLMRetryBackoffStrategy.NONE:
                raise ValueError("Retry policy with one attempt must use NONE backoff.")
            if self.initial_backoff_seconds != 0:
                raise ValueError("Retry policy with one attempt must not define backoff.")
        if self.enabled and self.max_attempts < 2:
            raise ValueError("Enabled retry policy must allow at least two attempts.")
        if self.enabled and self.backoff_strategy is LLMRetryBackoffStrategy.NONE:
            raise ValueError("Enabled retry policy must define a backoff strategy.")
        if self.max_backoff_seconds is not None and self.max_backoff_seconds < self.initial_backoff_seconds:
            raise ValueError("max_backoff_seconds must be greater than or equal to initial_backoff_seconds.")
        return self


class LLMTimeoutPolicy(BaseModel):
    global_timeout_seconds: float = Field(gt=0)
    generation_timeout_seconds: float | None = Field(default=None, gt=0)
    transport_timeout_seconds: float | None = Field(default=None, gt=0)
    provider_timeout_seconds: dict[str, float] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_timeout_policy(self) -> LLMTimeoutPolicy:
        if self.generation_timeout_seconds is not None and self.generation_timeout_seconds > self.global_timeout_seconds:
            raise ValueError("generation_timeout_seconds cannot exceed global_timeout_seconds.")
        if self.transport_timeout_seconds is not None and self.transport_timeout_seconds > self.global_timeout_seconds:
            raise ValueError("transport_timeout_seconds cannot exceed global_timeout_seconds.")
        for provider_name, timeout_seconds in self.provider_timeout_seconds.items():
            if timeout_seconds <= 0:
                raise ValueError(f"Provider timeout for '{provider_name}' must be greater than zero.")
            if timeout_seconds > self.global_timeout_seconds:
                raise ValueError(
                    f"Provider timeout for '{provider_name}' cannot exceed global_timeout_seconds."
                )
        return self


class LLMSecurityPrivacyPolicy(BaseModel):
    redact_prompts: bool = True
    redact_responses: bool = True
    pii_safe_logging: bool = True
    audit_visibility: LLMAuditVisibility = LLMAuditVisibility.METADATA_ONLY

    model_config = ConfigDict(frozen=True)


class LLMAuditTrailRecord(BaseModel):
    request_id: str = Field(min_length=1)
    execution_id: str = Field(min_length=1)
    correlation_id: str | None = None
    provider_name: str | None = None
    model_name: str | None = None
    execution_mode: AIExecutionMode | None = None
    routing_owner: AIExecutionOwner | None = None
    generation_profile_name: str | None = None
    visibility: LLMAuditVisibility = LLMAuditVisibility.METADATA_ONLY
    requested_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_timestamp_order(self) -> LLMAuditTrailRecord:
        if (
            self.requested_at is not None
            and self.completed_at is not None
            and self.completed_at < self.requested_at
        ):
            raise ValueError("completed_at cannot be earlier than requested_at.")
        return self


class LLMRolloutPolicy(BaseModel):
    stage: LLMRolloutStage = LLMRolloutStage.DISABLED
    enabled: bool = False
    percentage: int = Field(default=0, ge=0, le=100)
    provider_allowlist: list[str] = Field(default_factory=list)
    model_allowlist: list[str] = Field(default_factory=list)
    shadow_enabled: bool = False
    gradual_step_percentage: int | None = Field(default=None, ge=1, le=100)

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def validate_rollout_policy(self) -> LLMRolloutPolicy:
        if not self.enabled and self.percentage != 0:
            raise ValueError("Disabled rollout policy must use percentage=0.")
        if not self.enabled and self.stage is not LLMRolloutStage.DISABLED:
            raise ValueError("Disabled rollout policy must use the DISABLED stage.")
        if self.enabled and self.stage is LLMRolloutStage.DISABLED:
            raise ValueError("Enabled rollout policy cannot use the DISABLED stage.")
        if self.stage is LLMRolloutStage.SHADOW and not self.shadow_enabled:
            raise ValueError("SHADOW rollout stage requires shadow_enabled=True.")
        if self.shadow_enabled and self.stage is not LLMRolloutStage.SHADOW:
            raise ValueError("shadow_enabled=True requires the SHADOW rollout stage.")
        if self.stage is LLMRolloutStage.GENERAL_AVAILABILITY and self.percentage != 100:
            raise ValueError("GENERAL_AVAILABILITY rollout requires percentage=100.")
        if self.gradual_step_percentage is not None and self.stage is not LLMRolloutStage.GRADUAL:
            raise ValueError("gradual_step_percentage requires the GRADUAL rollout stage.")
        return self


class LLMPerformanceMetrics(BaseModel):
    request_count: int = Field(default=0, ge=0)
    throughput_requests_per_minute: float = Field(default=0.0, ge=0)
    token_throughput_per_second: float = Field(default=0.0, ge=0)
    provider_latency_ms: float = Field(default=0.0, ge=0)
    end_to_end_latency_ms: float = Field(default=0.0, ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMOperationalReadinessProfile(BaseModel):
    observability: LLMObservabilityPolicy
    health: LLMOperationalHealthReport
    retry_policy: LLMRetryPolicy
    timeout_policy: LLMTimeoutPolicy
    security_privacy: LLMSecurityPrivacyPolicy
    rollout_policy: LLMRolloutPolicy
    performance: LLMPerformanceMetrics

    model_config = ConfigDict(str_strip_whitespace=True)


@dataclass(frozen=True)
class LLMOperationalReadinessResult:
    profile: LLMOperationalReadinessProfile
    composition: LLMRuntimeComposition | None = None


class LLMOperationalReadinessEvaluator:
    """Deterministic production-readiness evaluator for the inactive LLM seam."""

    def evaluate(
        self,
        *,
        configuration: LLMConfiguration,
        activation_status: LLMRuntimeActivationStatus,
        rollout_policy: LLMRolloutPolicy | None = None,
    ) -> LLMOperationalReadinessProfile:
        return LLMOperationalReadinessProfile(
            observability=LLMObservabilityPolicy(),
            health=self._build_health_report(
                configuration=configuration,
                activation_status=activation_status,
            ),
            retry_policy=self._build_retry_policy(configuration),
            timeout_policy=self._build_timeout_policy(configuration),
            security_privacy=LLMSecurityPrivacyPolicy(),
            rollout_policy=(
                rollout_policy if rollout_policy is not None else LLMRolloutPolicy()
            ),
            performance=LLMPerformanceMetrics(),
        )

    def _build_health_report(
        self,
        *,
        configuration: LLMConfiguration,
        activation_status: LLMRuntimeActivationStatus,
    ) -> LLMOperationalHealthReport:
        providers: list[LLMProviderHealthReport] = []
        diagnostics: list[LLMHealthDiagnostic] = []

        for provider_status in activation_status.providers:
            provider_health_status = self._map_provider_status(provider_status.diagnostics)
            providers.append(
                LLMProviderHealthReport(
                    provider_name=provider_status.provider_name,
                    selected=provider_status.selected,
                    status=(
                        LLMOperationalHealthStatus.HEALTHY
                        if provider_status.healthy
                        else provider_health_status
                    ),
                    generation_available=provider_status.generation_available,
                    reason=(
                        f"Provider '{provider_status.provider_name}' is ready for generation."
                        if provider_status.healthy
                        else f"Provider '{provider_status.provider_name}' is not ready for generation."
                    ),
                    diagnostics=[
                        self._map_activation_diagnostic(diagnostic)
                        for diagnostic in provider_status.diagnostics
                    ],
                )
            )

        diagnostics.extend(
            self._map_activation_diagnostic(diagnostic)
            for diagnostic in activation_status.diagnostics
        )

        selected_provider_name = (
            configuration.selected_provider_name.value
            if configuration.selected_provider_name is not None
            else None
        )
        overall_status = self._resolve_overall_status(
            activation_status=activation_status,
            diagnostics=diagnostics,
        )

        return LLMOperationalHealthReport(
            overall_status=overall_status,
            selected_provider_name=selected_provider_name,
            overall_reason=activation_status.status_reason,
            providers=providers,
            diagnostics=diagnostics,
        )

    def _build_retry_policy(
        self,
        configuration: LLMConfiguration,
    ) -> LLMRetryPolicy:
        provider_policies = [
            LLMProviderRetryPolicy(
                provider_name=provider.provider_name.value,
                enabled=provider.max_retries > 0,
                max_attempts=provider.max_retries + 1,
                backoff_strategy=(
                    LLMRetryBackoffStrategy.EXPONENTIAL
                    if provider.max_retries > 0
                    else LLMRetryBackoffStrategy.NONE
                ),
                initial_backoff_seconds=(
                    provider.retry_backoff_seconds if provider.max_retries > 0 else 0.0
                ),
            )
            for provider in configuration.providers
        ]

        selected_provider = (
            configuration.get_provider(configuration.selected_provider_name)
            if configuration.selected_provider_name is not None
            else None
        )
        if selected_provider is None:
            return LLMRetryPolicy(provider_policies=provider_policies)

        return LLMRetryPolicy(
            enabled=selected_provider.max_retries > 0,
            max_attempts=selected_provider.max_retries + 1,
            backoff_strategy=(
                LLMRetryBackoffStrategy.EXPONENTIAL
                if selected_provider.max_retries > 0
                else LLMRetryBackoffStrategy.NONE
            ),
            initial_backoff_seconds=(
                selected_provider.retry_backoff_seconds
                if selected_provider.max_retries > 0
                else 0.0
            ),
            max_backoff_seconds=(
                selected_provider.retry_backoff_seconds
                * (2 ** max(selected_provider.max_retries - 1, 0))
                if selected_provider.max_retries > 0
                else None
            ),
            retryable_error_codes=[
                "transport_timeout",
                "provider_unavailable",
                "rate_limited",
            ],
            provider_policies=provider_policies,
        )

    def _build_timeout_policy(
        self,
        configuration: LLMConfiguration,
    ) -> LLMTimeoutPolicy:
        provider_timeout_seconds = {
            provider.provider_name.value: provider.timeout_seconds
            for provider in configuration.providers
        }
        selected_provider = (
            configuration.get_provider(configuration.selected_provider_name)
            if configuration.selected_provider_name is not None
            else None
        )
        global_timeout_seconds = max(provider_timeout_seconds.values(), default=30.0)
        return LLMTimeoutPolicy(
            global_timeout_seconds=global_timeout_seconds,
            generation_timeout_seconds=(
                selected_provider.timeout_seconds
                if selected_provider is not None
                else global_timeout_seconds
            ),
            transport_timeout_seconds=(
                selected_provider.timeout_seconds
                if selected_provider is not None
                else global_timeout_seconds
            ),
            provider_timeout_seconds=provider_timeout_seconds,
        )

    def _resolve_overall_status(
        self,
        *,
        activation_status: LLMRuntimeActivationStatus,
        diagnostics: list[LLMHealthDiagnostic],
    ) -> LLMOperationalHealthStatus:
        if any(
            diagnostic.status is LLMOperationalHealthStatus.CONFIGURATION_ERROR
            for diagnostic in diagnostics
        ):
            return LLMOperationalHealthStatus.CONFIGURATION_ERROR
        if any(
            diagnostic.status is LLMOperationalHealthStatus.AUTHENTICATION_ERROR
            for diagnostic in diagnostics
        ):
            return LLMOperationalHealthStatus.AUTHENTICATION_ERROR
        if activation_status.generation_available:
            return LLMOperationalHealthStatus.HEALTHY
        if activation_status.llm_enabled or activation_status.selected_provider_enabled:
            return LLMOperationalHealthStatus.DEGRADED
        return LLMOperationalHealthStatus.UNAVAILABLE

    def _map_provider_status(
        self,
        diagnostics: list[LLMActivationDiagnostic],
    ) -> LLMOperationalHealthStatus:
        if any(diagnostic.code == "authentication_missing" for diagnostic in diagnostics):
            return LLMOperationalHealthStatus.AUTHENTICATION_ERROR
        if any(
            diagnostic.code in {"generation_budget_unresolved", "selected_provider_unconfigured"}
            for diagnostic in diagnostics
        ):
            return LLMOperationalHealthStatus.CONFIGURATION_ERROR
        if diagnostics:
            return LLMOperationalHealthStatus.DEGRADED
        return LLMOperationalHealthStatus.UNAVAILABLE

    def _map_activation_diagnostic(
        self,
        diagnostic: LLMActivationDiagnostic,
    ) -> LLMHealthDiagnostic:
        return LLMHealthDiagnostic(
            code=diagnostic.code,
            message=diagnostic.message,
            status=self._map_activation_status_code(diagnostic.code),
            provider_name=diagnostic.provider_name,
            blocking=diagnostic.blocking,
            metadata=dict(diagnostic.metadata),
        )

    def _map_activation_status_code(
        self,
        code: str,
    ) -> LLMOperationalHealthStatus:
        if code in {
            "configuration_invalid",
            "selected_provider_unconfigured",
            "generation_budget_unresolved",
        }:
            return LLMOperationalHealthStatus.CONFIGURATION_ERROR
        if code == "authentication_missing":
            return LLMOperationalHealthStatus.AUTHENTICATION_ERROR
        if code in {"llm_disabled", "generation_disallowed", "selected_provider_missing"}:
            return LLMOperationalHealthStatus.UNAVAILABLE
        return LLMOperationalHealthStatus.DEGRADED


class LLMOperationalReadinessService:
    """Safe wrapper that describes production-readiness from composed runtime state."""

    def __init__(
        self,
        *,
        composition_root: LLMRuntimeCompositionRoot,
        evaluator: LLMOperationalReadinessEvaluator | None = None,
    ) -> None:
        self._composition_root = composition_root
        self._evaluator = (
            evaluator if evaluator is not None else LLMOperationalReadinessEvaluator()
        )

    def evaluate(
        self,
        rollout_policy: LLMRolloutPolicy | None = None,
    ) -> LLMOperationalReadinessResult:
        try:
            composition = self._composition_root.compose()
        except Exception as exc:
            return LLMOperationalReadinessResult(
                profile=LLMOperationalReadinessProfile(
                    observability=LLMObservabilityPolicy(),
                    health=LLMOperationalHealthReport(
                        overall_status=LLMOperationalHealthStatus.CONFIGURATION_ERROR,
                        overall_reason=(
                            "Operational readiness evaluation failed because the composed "
                            f"LLM runtime could not be assembled: {exc}"
                        ),
                        diagnostics=[
                            LLMHealthDiagnostic(
                                code="configuration_invalid",
                                message=str(exc),
                                status=LLMOperationalHealthStatus.CONFIGURATION_ERROR,
                                blocking=True,
                            )
                        ],
                    ),
                    retry_policy=LLMRetryPolicy(),
                    timeout_policy=LLMTimeoutPolicy(global_timeout_seconds=30.0),
                    security_privacy=LLMSecurityPrivacyPolicy(),
                    rollout_policy=(
                        rollout_policy if rollout_policy is not None else LLMRolloutPolicy()
                    ),
                    performance=LLMPerformanceMetrics(),
                ),
                composition=None,
            )

        profile = self._evaluator.evaluate(
            configuration=composition.configuration,
            activation_status=composition.activation_status,
            rollout_policy=rollout_policy,
        )
        return LLMOperationalReadinessResult(
            profile=profile,
            composition=composition,
        )
