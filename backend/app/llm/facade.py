from __future__ import annotations

from collections import deque
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime, timezone
from enum import Enum
from threading import Lock, Thread
from time import perf_counter
from typing import Any, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.knowledge import KnowledgeDocument
from app.llm.activation import LLMRuntimeActivationStatus
from app.llm.composition import LLMRuntimeComposition, LLMRuntimeCompositionRoot
from app.llm.composer import (
    LLMRuntimeResponse,
    LLMRuntimeResponseComposer,
    LLMRuntimeResponseComposerRequest,
    LLMRuntimeResponseComposerResult,
)
from app.llm.execution_policy import (
    AIExecutionDecision,
    AIExecutionMode,
    AIExecutionOwner,
    AIExecutionPolicyRequest,
)
from app.llm.eligibility import (
    LLMRuntimeResponseEligibilityEvaluator,
    LLMRuntimeResponseEligibilityRequest,
    LLMRuntimeResponseEligibilityResult,
)
from app.llm.operations import (
    LLMAuditTrailRecord,
    LLMObservabilityRecord,
    LLMTokenAccounting,
    LLMTimingBreakdown,
    LLMTraceContext,
)
from app.llm.orchestrator import (
    LLMGenerationOrchestrationRequest,
    LLMGenerationOrchestrationResult,
)
from app.llm.service import LLMIntegrationStatus
from app.llm.validation import (
    LLMRuntimeResponseValidationRequest,
    LLMRuntimeResponseValidationResult,
    LLMRuntimeResponseValidator,
)


class LLMRuntimeFacadeSnapshot(BaseModel):
    """Deterministic save-ready view of the inactive LLM runtime boundary."""

    configuration_loaded: bool = True
    composition_cached: bool = True
    connected_provider_names: list[str] = Field(default_factory=list)
    default_provider_name: str | None = None
    selected_provider_name: str | None = None
    activation_status: LLMRuntimeActivationStatus
    integration_status: LLMIntegrationStatus
    prompt_builder_attached: bool = True
    orchestrator_attached: bool = True
    shadow_execution_count: int = 0
    last_shadow_status: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMShadowModeStatus(str, Enum):
    SKIPPED = "SKIPPED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class LLMShadowModeRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()), min_length=1)
    correlation_id: str | None = None
    parent_execution_id: str | None = None
    user_message: str = Field(min_length=1)
    official_response_owner: AIExecutionOwner
    official_intent_name: str | None = None
    has_active_workflow: bool = False
    knowledge_eligible: bool = False
    knowledge_match_available: bool = False
    conversation_state: dict[str, Any] = Field(default_factory=dict)
    documents: list[KnowledgeDocument] = Field(default_factory=list)
    provider_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMShadowModeDiagnostic(BaseModel):
    request_id: str = Field(min_length=1)
    correlation_id: str | None = None
    execution_id: str = Field(min_length=1)
    status: LLMShadowModeStatus
    decision: AIExecutionDecision
    observability: LLMObservabilityRecord
    audit_record: LLMAuditTrailRecord
    token_accounting: LLMTokenAccounting | None = None
    provider_name: str | None = None
    model_name: str | None = None
    error_message: str | None = None
    error_type: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMShadowModeDispatchResult(BaseModel):
    decision: AIExecutionDecision
    scheduled: bool = False
    diagnostic: LLMShadowModeDiagnostic | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMControlledGenerationStatus(str, Enum):
    SKIPPED = "SKIPPED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class LLMControlledGenerationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()), min_length=1)
    correlation_id: str | None = None
    parent_execution_id: str | None = None
    policy_request: AIExecutionPolicyRequest = Field(
        default_factory=AIExecutionPolicyRequest
    )
    deterministic_response: LLMRuntimeResponse | None = None
    orchestration_request: LLMGenerationOrchestrationRequest

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMControlledGenerationResult(BaseModel):
    request_id: str
    correlation_id: str | None = None
    decision: AIExecutionDecision
    status: LLMControlledGenerationStatus
    generated_result: LLMGenerationOrchestrationResult | None = None
    validation_result: LLMRuntimeResponseValidationResult | None = None
    eligibility_result: LLMRuntimeResponseEligibilityResult | None = None
    composition_result: LLMRuntimeResponseComposerResult | None = None
    final_response: LLMRuntimeResponse | None = None
    fallback_reason: str | None = None
    error_message: str | None = None
    error_type: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMShadowExecutionRunner(Protocol):
    def submit(self, task: Callable[[], None]) -> None:
        ...


class ThreadedLLMShadowExecutionRunner:
    """Runs shadow work in a background daemon thread."""

    def submit(self, task: Callable[[], None]) -> None:
        thread = Thread(target=task, daemon=True)
        thread.start()


class InlineLLMShadowExecutionRunner:
    """Runs shadow work inline for tests and deterministic callers."""

    def submit(self, task: Callable[[], None]) -> None:
        task()


class LLMRuntimeFacade:
    """Public runtime facade for safe shadow execution over the composed LLM subsystem."""

    def __init__(
        self,
        *,
        composition_root: LLMRuntimeCompositionRoot,
        shadow_execution_runner: LLMShadowExecutionRunner | None = None,
        runtime_response_validator: LLMRuntimeResponseValidator | None = None,
        runtime_response_eligibility_evaluator: LLMRuntimeResponseEligibilityEvaluator | None = None,
        runtime_response_composer: LLMRuntimeResponseComposer | None = None,
        shadow_history_limit: int = 100,
    ) -> None:
        self._composition_root = composition_root
        self._shadow_execution_runner = (
            shadow_execution_runner
            if shadow_execution_runner is not None
            else ThreadedLLMShadowExecutionRunner()
        )
        self._runtime_response_validator = (
            runtime_response_validator
            if runtime_response_validator is not None
            else LLMRuntimeResponseValidator()
        )
        self._runtime_response_eligibility_evaluator = (
            runtime_response_eligibility_evaluator
            if runtime_response_eligibility_evaluator is not None
            else LLMRuntimeResponseEligibilityEvaluator()
        )
        self._runtime_response_composer = (
            runtime_response_composer
            if runtime_response_composer is not None
            else LLMRuntimeResponseComposer()
        )
        self._shadow_history: deque[LLMShadowModeDiagnostic] = deque(
            maxlen=shadow_history_limit
        )
        self._shadow_history_lock = Lock()

    def compose(self) -> LLMRuntimeComposition:
        return self._composition_root.compose()

    def get_composition(self) -> LLMRuntimeComposition:
        return self.compose()

    def snapshot(self) -> LLMRuntimeFacadeSnapshot:
        composition = self.compose()
        integration_status = composition.llm_integration_service.get_status()
        last_shadow = self.get_last_shadow_diagnostic()
        return LLMRuntimeFacadeSnapshot(
            connected_provider_names=list(integration_status.connected_provider_names),
            default_provider_name=integration_status.default_provider_name,
            selected_provider_name=composition.activation_status.selected_provider_name,
            activation_status=composition.activation_status,
            integration_status=integration_status,
            shadow_execution_count=len(self.list_shadow_diagnostics()),
            last_shadow_status=last_shadow.status.value if last_shadow is not None else None,
        )

    def save_integration_boundary(self) -> LLMRuntimeFacadeSnapshot:
        """Alias for callers that want an explicit boundary-capture verb."""

        return self.snapshot()

    def run_shadow_mode(
        self,
        request: LLMShadowModeRequest,
        *,
        asynchronous: bool = True,
    ) -> LLMShadowModeDispatchResult:
        decision = self._evaluate_shadow_decision(request)
        if not decision.should_execute_shadow:
            diagnostic = self._build_skipped_diagnostic(request=request, decision=decision)
            self._store_shadow_diagnostic(diagnostic)
            return LLMShadowModeDispatchResult(
                decision=decision,
                scheduled=False,
                diagnostic=diagnostic,
            )

        if asynchronous:
            self._shadow_execution_runner.submit(
                lambda: self._execute_shadow_mode(request=request, decision=decision)
            )
            return LLMShadowModeDispatchResult(
                decision=decision,
                scheduled=True,
            )

        diagnostic = self._execute_shadow_mode(request=request, decision=decision)
        return LLMShadowModeDispatchResult(
            decision=decision,
            scheduled=False,
            diagnostic=diagnostic,
        )

    def run_controlled_generation(
        self,
        request: LLMControlledGenerationRequest,
    ) -> LLMControlledGenerationResult:
        decision = self._evaluate_controlled_generation_decision(request.policy_request)
        if decision.execution_mode is AIExecutionMode.DETERMINISTIC_ONLY:
            if request.deterministic_response is None:
                return LLMControlledGenerationResult(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    decision=decision,
                    status=LLMControlledGenerationStatus.SKIPPED,
                    fallback_reason=(
                        "Deterministic-only controlled generation had no business "
                        "response to preserve."
                    ),
                )

            composition_result = self._runtime_response_composer.compose(
                LLMRuntimeResponseComposerRequest(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    composition_mode=AIExecutionMode.DETERMINISTIC_ONLY,
                    deterministic_response=request.deterministic_response,
                    metadata={
                        "parent_execution_id": request.parent_execution_id,
                        **deepcopy(request.orchestration_request.metadata),
                    },
                )
            )
            return LLMControlledGenerationResult(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                decision=decision,
                status=LLMControlledGenerationStatus.SUCCEEDED,
                composition_result=composition_result,
                final_response=composition_result.final_response,
            )

        if not self._can_execute_controlled_generation(decision):
            return LLMControlledGenerationResult(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                decision=decision,
                status=LLMControlledGenerationStatus.SKIPPED,
                fallback_reason=decision.fallback_reason or decision.routing_reason,
            )

        eligibility_result: LLMRuntimeResponseEligibilityResult | None = None
        try:
            generated_result = self.compose().orchestrator.generate(
                request.orchestration_request
            )
            validation_result = self._runtime_response_validator.validate(
                LLMRuntimeResponseValidationRequest(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    orchestration_request=request.orchestration_request,
                    orchestration_result=generated_result,
                    metadata={
                        "parent_execution_id": request.parent_execution_id,
                        **deepcopy(request.orchestration_request.metadata),
                    },
                )
            )
            if not validation_result.is_valid:
                return LLMControlledGenerationResult(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    decision=decision,
                    status=LLMControlledGenerationStatus.FAILED,
                    validation_result=validation_result,
                    fallback_reason=(
                        "Controlled runtime generation failed validation and "
                        "preserved the existing deterministic response."
                    ),
                )
            eligibility_result = self._runtime_response_eligibility_evaluator.evaluate(
                LLMRuntimeResponseEligibilityRequest(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    policy_decision=decision,
                    validation_result=validation_result,
                    orchestration_request=request.orchestration_request,
                    metadata={
                        "parent_execution_id": request.parent_execution_id,
                        **deepcopy(request.orchestration_request.metadata),
                    },
                )
            )
            if not eligibility_result.is_eligible:
                composition_result = None
                final_response = None
                if request.deterministic_response is not None:
                    composition_result = self._runtime_response_composer.compose(
                        LLMRuntimeResponseComposerRequest(
                            request_id=request.request_id,
                            correlation_id=request.correlation_id,
                            composition_mode=AIExecutionMode.DETERMINISTIC_ONLY,
                            deterministic_response=request.deterministic_response,
                            validation_result=validation_result,
                            eligibility_result=eligibility_result,
                            metadata={
                                "parent_execution_id": request.parent_execution_id,
                                **deepcopy(request.orchestration_request.metadata),
                            },
                        )
                    )
                    final_response = composition_result.final_response
                return LLMControlledGenerationResult(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    decision=decision,
                    status=LLMControlledGenerationStatus.SKIPPED,
                    validation_result=validation_result,
                    eligibility_result=eligibility_result,
                    composition_result=composition_result,
                    final_response=final_response,
                    fallback_reason=eligibility_result.fallback_reason,
                )
            composition_result = self._runtime_response_composer.compose(
                LLMRuntimeResponseComposerRequest(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    composition_mode=decision.execution_mode,
                    deterministic_response=request.deterministic_response,
                    validation_result=validation_result,
                    eligibility_result=eligibility_result,
                    orchestration_result=generated_result,
                    metadata={
                        "parent_execution_id": request.parent_execution_id,
                        **deepcopy(request.orchestration_request.metadata),
                    },
                )
            )
        except Exception as exc:
            return LLMControlledGenerationResult(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                decision=decision,
                status=LLMControlledGenerationStatus.FAILED,
                fallback_reason=(
                    "Controlled runtime generation failed safely and preserved the "
                    "existing deterministic response."
                ),
                error_message=str(exc),
                error_type=type(exc).__name__,
            )

        return LLMControlledGenerationResult(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            decision=decision,
            status=LLMControlledGenerationStatus.SUCCEEDED,
            generated_result=generated_result,
            validation_result=validation_result,
            eligibility_result=eligibility_result,
            composition_result=composition_result,
            final_response=composition_result.final_response,
        )

    def list_shadow_diagnostics(self) -> list[LLMShadowModeDiagnostic]:
        with self._shadow_history_lock:
            return list(self._shadow_history)

    def get_last_shadow_diagnostic(self) -> LLMShadowModeDiagnostic | None:
        with self._shadow_history_lock:
            if not self._shadow_history:
                return None
            return self._shadow_history[-1]

    def _evaluate_shadow_decision(
        self,
        request: LLMShadowModeRequest,
    ) -> AIExecutionDecision:
        composition = self.compose()
        return composition.execution_policy_service.evaluate(
            AIExecutionPolicyRequest(
                preferred_mode=AIExecutionMode.SHADOW,
                intent_name=request.official_intent_name,
                has_active_workflow=request.has_active_workflow,
                knowledge_eligible=request.knowledge_eligible,
                knowledge_match_available=request.knowledge_match_available,
            )
        ).decision

    def _evaluate_controlled_generation_decision(
        self,
        request: AIExecutionPolicyRequest,
    ) -> AIExecutionDecision:
        composition = self.compose()
        return composition.execution_policy_service.evaluate(request).decision

    def _can_execute_controlled_generation(
        self,
        decision: AIExecutionDecision,
    ) -> bool:
        return decision.should_execute_llm and decision.execution_mode in {
            AIExecutionMode.LLM_ONLY,
            AIExecutionMode.HYBRID,
        }

    def _execute_shadow_mode(
        self,
        *,
        request: LLMShadowModeRequest,
        decision: AIExecutionDecision,
    ) -> LLMShadowModeDiagnostic:
        composition = self.compose()
        trace = LLMTraceContext(
            request_id=request.request_id,
            execution_id=str(uuid4()),
            correlation_id=request.correlation_id,
            parent_execution_id=request.parent_execution_id,
        )
        started_at = datetime.now(timezone.utc)
        started_perf = perf_counter()
        audit_record = LLMAuditTrailRecord(
            request_id=request.request_id,
            execution_id=trace.execution_id,
            correlation_id=request.correlation_id,
            provider_name=request.provider_name or decision.selected_provider_name,
            execution_mode=AIExecutionMode.SHADOW,
            routing_owner=request.official_response_owner,
            visibility=composition.operational_readiness_service.evaluate(
                rollout_policy=None
            ).profile.security_privacy.audit_visibility,
            requested_at=started_at,
        )

        try:
            orchestration_request = self._build_orchestration_request(
                request=request,
                provider_name=request.provider_name or decision.selected_provider_name,
            )
            orchestration_result = composition.orchestrator.generate(orchestration_request)
            completed_at = datetime.now(timezone.utc)
            duration_ms = (perf_counter() - started_perf) * 1000
            token_accounting = self._build_token_accounting(
                provider_name=orchestration_result.provider_name,
                model_name=orchestration_result.model_name,
                usage=orchestration_result.usage,
            )
            diagnostic = LLMShadowModeDiagnostic(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                execution_id=trace.execution_id,
                status=LLMShadowModeStatus.SUCCEEDED,
                decision=decision,
                observability=LLMObservabilityRecord(
                    event_name="llm_shadow_mode_execution",
                    trace=trace,
                    timing=LLMTimingBreakdown(
                        total_duration_ms=duration_ms,
                        provider_latency_ms=duration_ms,
                        orchestration_duration_ms=duration_ms,
                    ),
                    metadata=self._observability_metadata(
                        request=request,
                        decision=decision,
                        status=LLMShadowModeStatus.SUCCEEDED,
                    ),
                ),
                audit_record=audit_record.model_copy(
                    update={
                        "provider_name": orchestration_result.provider_name,
                        "model_name": orchestration_result.model_name,
                        "completed_at": completed_at,
                    }
                ),
                token_accounting=token_accounting,
                provider_name=orchestration_result.provider_name,
                model_name=orchestration_result.model_name,
            )
        except Exception as exc:
            completed_at = datetime.now(timezone.utc)
            duration_ms = (perf_counter() - started_perf) * 1000
            diagnostic = LLMShadowModeDiagnostic(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                execution_id=trace.execution_id,
                status=LLMShadowModeStatus.FAILED,
                decision=decision,
                observability=LLMObservabilityRecord(
                    event_name="llm_shadow_mode_execution",
                    trace=trace,
                    timing=LLMTimingBreakdown(
                        total_duration_ms=duration_ms,
                        provider_latency_ms=duration_ms,
                        orchestration_duration_ms=duration_ms,
                    ),
                    metadata=self._observability_metadata(
                        request=request,
                        decision=decision,
                        status=LLMShadowModeStatus.FAILED,
                        error_type=type(exc).__name__,
                    ),
                ),
                audit_record=audit_record.model_copy(
                    update={
                        "completed_at": completed_at,
                    }
                ),
                provider_name=request.provider_name or decision.selected_provider_name,
                error_message=str(exc),
                error_type=type(exc).__name__,
            )

        self._store_shadow_diagnostic(diagnostic)
        return diagnostic

    def _build_orchestration_request(
        self,
        *,
        request: LLMShadowModeRequest,
        provider_name: str | None,
    ):
        from app.llm.orchestrator import LLMGenerationOrchestrationRequest

        return LLMGenerationOrchestrationRequest(
            user_message=request.user_message,
            conversation_state=deepcopy(request.conversation_state),
            documents=list(request.documents),
            active_intent=request.official_intent_name,
            provider_name=provider_name,
            metadata={
                "shadow_mode": True,
                "request_id": request.request_id,
                "correlation_id": request.correlation_id,
                "official_response_owner": request.official_response_owner.value,
                **deepcopy(request.metadata),
            },
        )

    def _build_skipped_diagnostic(
        self,
        *,
        request: LLMShadowModeRequest,
        decision: AIExecutionDecision,
    ) -> LLMShadowModeDiagnostic:
        execution_id = str(uuid4())
        return LLMShadowModeDiagnostic(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            execution_id=execution_id,
            status=LLMShadowModeStatus.SKIPPED,
            decision=decision,
            observability=LLMObservabilityRecord(
                event_name="llm_shadow_mode_execution",
                trace=LLMTraceContext(
                    request_id=request.request_id,
                    execution_id=execution_id,
                    correlation_id=request.correlation_id,
                    parent_execution_id=request.parent_execution_id,
                ),
                metadata=self._observability_metadata(
                    request=request,
                    decision=decision,
                    status=LLMShadowModeStatus.SKIPPED,
                ),
            ),
            audit_record=LLMAuditTrailRecord(
                request_id=request.request_id,
                execution_id=execution_id,
                correlation_id=request.correlation_id,
                provider_name=request.provider_name or decision.selected_provider_name,
                execution_mode=decision.execution_mode,
                routing_owner=request.official_response_owner,
                requested_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            ),
            provider_name=request.provider_name or decision.selected_provider_name,
        )

    def _build_token_accounting(
        self,
        *,
        provider_name: str | None,
        model_name: str | None,
        usage,
    ) -> LLMTokenAccounting | None:
        if usage is None:
            return None
        return LLMTokenAccounting(
            provider_name=provider_name,
            model_name=model_name,
            prompt_tokens=usage.input_tokens or 0,
            completion_tokens=usage.output_tokens or 0,
            total_tokens=usage.total_tokens,
        )

    def _observability_metadata(
        self,
        *,
        request: LLMShadowModeRequest,
        decision: AIExecutionDecision,
        status: LLMShadowModeStatus,
        error_type: str | None = None,
    ) -> dict[str, str | int | float | bool]:
        metadata: dict[str, str | int | float | bool] = {
            "shadow_mode": True,
            "status": status.value,
            "official_response_owner": request.official_response_owner.value,
            "requested_mode": decision.requested_mode.value,
            "execution_mode": decision.execution_mode.value,
            "shadow_executed": decision.should_execute_shadow,
            "provider_name": request.provider_name or decision.selected_provider_name or "",
        }
        if request.official_intent_name:
            metadata["official_intent_name"] = request.official_intent_name
        if error_type:
            metadata["error_type"] = error_type
        return metadata

    def _store_shadow_diagnostic(self, diagnostic: LLMShadowModeDiagnostic) -> None:
        with self._shadow_history_lock:
            self._shadow_history.append(diagnostic)
