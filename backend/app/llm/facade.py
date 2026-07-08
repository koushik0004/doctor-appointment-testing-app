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
from app.llm.post_processor import (
    LLMRuntimeResponsePostProcessor,
    LLMRuntimeResponsePostProcessingRequest,
    LLMRuntimeResponsePostProcessingResult,
    LLMRuntimeResponsePostProcessingStatus,
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
from app.llm.runtime_trace import AIRuntimeTraceSession


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
    post_processing_result: LLMRuntimeResponsePostProcessingResult | None = None
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
        runtime_response_post_processor: LLMRuntimeResponsePostProcessor | None = None,
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
        self._runtime_response_post_processor = (
            runtime_response_post_processor
            if runtime_response_post_processor is not None
            else LLMRuntimeResponsePostProcessor()
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
        runtime_trace: AIRuntimeTraceSession | None = None,
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
                lambda: self._execute_shadow_mode(
                    request=request,
                    decision=decision,
                    runtime_trace=runtime_trace,
                )
            )
            return LLMShadowModeDispatchResult(
                decision=decision,
                scheduled=True,
            )

        diagnostic = self._execute_shadow_mode(
            request=request,
            decision=decision,
            runtime_trace=runtime_trace,
        )
        return LLMShadowModeDispatchResult(
            decision=decision,
            scheduled=False,
            diagnostic=diagnostic,
        )

    def run_controlled_generation(
        self,
        request: LLMControlledGenerationRequest,
        *,
        runtime_trace: AIRuntimeTraceSession | None = None,
    ) -> LLMControlledGenerationResult:
        decision = self._evaluate_controlled_generation_decision(request.policy_request)
        pipeline_stage = "orchestration"
        if runtime_trace is not None:
            runtime_trace.update_stage(
                "controlled_generation",
                {
                    "entered": True,
                    "execution_mode": decision.execution_mode.value,
                    "execution_owner": decision.official_response_owner.value,
                    "shadow_mode": False,
                    "reason": decision.fallback_reason or decision.routing_reason,
                },
            )
            runtime_trace.update_stage(
                "runtime_facade",
                {
                    "entered": True,
                    "mode": "CONTROLLED_GENERATION",
                    "execution_mode": decision.execution_mode.value,
                    "execution_owner": decision.official_response_owner.value,
                    "reason": decision.fallback_reason or decision.routing_reason,
                },
            )
            runtime_trace.update_stage(
                "execution_policy",
                {
                    "llm_enabled": decision.activation.llm_enabled,
                    "selected_provider": decision.selected_provider_name,
                    "provider_healthy": decision.activation.selected_provider_healthy,
                    "generation_allowed": decision.activation.generation_allowed,
                    "generation_available": decision.activation.generation_available,
                    "execution_owner": decision.official_response_owner.value,
                    "decision": decision.execution_mode.value,
                    "reason": decision.fallback_reason or decision.routing_reason,
                },
            )
        if decision.execution_mode is AIExecutionMode.DETERMINISTIC_ONLY:
            if request.deterministic_response is None:
                result = LLMControlledGenerationResult(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    decision=decision,
                    status=LLMControlledGenerationStatus.SKIPPED,
                    fallback_reason=(
                        "Deterministic-only controlled generation had no business "
                        "response to preserve."
                    ),
                )
                if runtime_trace is not None:
                    self._emit_controlled_generation_diagnostic(
                        runtime_trace=runtime_trace,
                        result=result,
                        stop_stage="deterministic_response",
                    )
                return result

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
            post_processing_result = self._post_process_runtime_response(
                request=request,
                composition_result=composition_result,
            )
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "runtime_validator",
                    {"executed": False, "reason": "Deterministic-only controlled generation bypassed validation."},
                )
                runtime_trace.update_stage(
                    "eligibility",
                    {"executed": False, "reason": "Deterministic-only controlled generation bypassed eligibility."},
                )
                runtime_trace.update_stage(
                    "composer",
                    {
                        "executed": True,
                        "composition_mode": AIExecutionMode.DETERMINISTIC_ONLY.value,
                        "reason": "Deterministic-only controlled generation preserved the business response.",
                    },
                )
                runtime_trace.update_stage(
                    "post_processor",
                    {
                        "executed": True,
                        "status": post_processing_result.status.value,
                    },
                )
                runtime_trace.update_stage(
                    "controlled_generation",
                    {
                        "entered": True,
                        "status": LLMControlledGenerationStatus.SUCCEEDED.value,
                        "reason": "Deterministic-only controlled generation preserved the business response.",
                    },
                )
            return LLMControlledGenerationResult(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                decision=decision,
                status=LLMControlledGenerationStatus.SUCCEEDED,
                composition_result=composition_result,
                post_processing_result=post_processing_result,
                final_response=post_processing_result.final_response,
            )

        if not self._can_execute_controlled_generation(decision):
            result = LLMControlledGenerationResult(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                decision=decision,
                status=LLMControlledGenerationStatus.SKIPPED,
                fallback_reason=decision.fallback_reason or decision.routing_reason,
            )
            if runtime_trace is not None:
                self._emit_controlled_generation_diagnostic(
                    runtime_trace=runtime_trace,
                    result=result,
                    stop_stage="execution_policy",
                )
            return result

        eligibility_result: LLMRuntimeResponseEligibilityResult | None = None
        post_processing_result: LLMRuntimeResponsePostProcessingResult | None = None
        try:
            pipeline_stage = "orchestration"
            generated_result = self.compose().orchestrator.generate(
                request.orchestration_request,
                runtime_trace=runtime_trace,
            )
            pipeline_stage = "validation"
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
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "runtime_validator",
                    {
                        "executed": True,
                        "passed": validation_result.is_valid,
                        "issue_count": len(validation_result.issues),
                    },
                )
            if not validation_result.is_valid:
                if runtime_trace is not None:
                    runtime_trace.update_stage(
                        "eligibility",
                        {
                            "executed": False,
                            "reason": "Validation failed before eligibility evaluation.",
                        },
                    )
                    runtime_trace.update_stage(
                        "composer",
                        {
                            "executed": False,
                            "reason": "Validation failed before response composition.",
                        },
                    )
                    runtime_trace.update_stage(
                        "post_processor",
                        {
                            "executed": False,
                            "reason": "Validation failed before response post processing.",
                        },
                    )
                    runtime_trace.update_stage(
                        "controlled_generation",
                        {
                            "entered": True,
                            "status": LLMControlledGenerationStatus.FAILED.value,
                            "reason": (
                                "Controlled runtime generation failed validation and "
                                "preserved the existing deterministic response."
                            ),
                        },
                    )
                result = LLMControlledGenerationResult(
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
                if runtime_trace is not None:
                    self._emit_controlled_generation_diagnostic(
                        runtime_trace=runtime_trace,
                        result=result,
                        stop_stage="validation",
                    )
                return result
            pipeline_stage = "eligibility"
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
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "eligibility",
                    {
                        "executed": True,
                        "passed": eligibility_result.is_eligible,
                        "issue_count": len(eligibility_result.issues),
                    },
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
                    post_processing_result = self._post_process_runtime_response(
                        request=request,
                        composition_result=composition_result,
                    )
                    final_response = post_processing_result.final_response
                    if runtime_trace is not None:
                        runtime_trace.update_stage(
                            "composer",
                            {
                                "executed": True,
                                "composition_mode": AIExecutionMode.DETERMINISTIC_ONLY.value,
                                "reason": eligibility_result.fallback_reason,
                            },
                        )
                        runtime_trace.update_stage(
                            "post_processor",
                            {
                                "executed": True,
                                "status": post_processing_result.status.value,
                            },
                        )
                result = LLMControlledGenerationResult(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    decision=decision,
                    status=LLMControlledGenerationStatus.SKIPPED,
                    validation_result=validation_result,
                    eligibility_result=eligibility_result,
                    composition_result=composition_result,
                    post_processing_result=post_processing_result,
                    final_response=final_response,
                    fallback_reason=eligibility_result.fallback_reason,
                )
                if runtime_trace is not None:
                    self._emit_controlled_generation_diagnostic(
                        runtime_trace=runtime_trace,
                        result=result,
                        stop_stage="eligibility",
                    )
                return result
            pipeline_stage = "composition"
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
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "composer",
                    {
                        "executed": True,
                        "composition_mode": decision.execution_mode.value,
                        "augmentation_applied": composition_result.augmentation_applied,
                    },
                )
            post_processing_result = self._post_process_runtime_response(
                request=request,
                composition_result=composition_result,
            )
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "post_processor",
                    {
                        "executed": True,
                        "status": post_processing_result.status.value,
                    },
                )
        except Exception as exc:
            result = LLMControlledGenerationResult(
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
            if runtime_trace is not None:
                self._emit_controlled_generation_diagnostic(
                    runtime_trace=runtime_trace,
                    result=result,
                    stop_stage=pipeline_stage,
                )
            return result

        result = LLMControlledGenerationResult(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            decision=decision,
            status=LLMControlledGenerationStatus.SUCCEEDED,
            generated_result=generated_result,
            validation_result=validation_result,
            eligibility_result=eligibility_result,
            composition_result=composition_result,
            post_processing_result=post_processing_result,
            final_response=post_processing_result.final_response,
        )
        if runtime_trace is not None:
            runtime_trace.update_stage(
                "controlled_generation",
                {
                    "entered": True,
                    "status": LLMControlledGenerationStatus.SUCCEEDED.value,
                    "reason": "Controlled runtime generation completed successfully.",
                },
            )
        return result

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

    def _emit_controlled_generation_diagnostic(
        self,
        *,
        runtime_trace: AIRuntimeTraceSession,
        result: LLMControlledGenerationResult,
        stop_stage: str,
    ) -> None:
        snapshot = runtime_trace.snapshot()
        provider_transport = snapshot.get("provider_transport") or {}
        provider_adapter = snapshot.get("provider_adapter") or {}
        prompt_builder = snapshot.get("prompt_builder") or {}
        llm_integration = snapshot.get("llm_integration") or {}
        runtime_validator = snapshot.get("runtime_validator") or {}
        eligibility = snapshot.get("eligibility") or {}
        composer = snapshot.get("composer") or {}
        post_processor = snapshot.get("post_processor") or {}

        transport_invoked = bool(provider_transport.get("http_request_started"))
        stage_name = self._infer_controlled_generation_stop_stage(
            stop_stage=stop_stage,
            prompt_builder=prompt_builder,
            llm_integration=llm_integration,
            provider_adapter=provider_adapter,
            provider_transport=provider_transport,
        )
        diagnostic_reason = result.fallback_reason or result.decision.fallback_reason or result.decision.routing_reason
        runtime_trace.update_stage(
            "controlled_generation",
            {
                "entered": True,
                "status": result.status.value,
                "execution_mode": result.decision.execution_mode.value,
                "execution_owner": result.decision.official_response_owner.value,
                "generation_available": result.decision.activation.generation_available,
                "provider_readiness": result.decision.activation.provider_readiness,
                "provider_selected": result.decision.selected_provider_name,
                "orchestration_started": bool(
                    prompt_builder or llm_integration or provider_adapter or provider_transport
                ),
                "prompt_builder_executed": bool(prompt_builder.get("executed")),
                "provider_adapter_executed": bool(provider_adapter.get("request_translated")),
                "transport_invoked": transport_invoked,
                "http_request_sent": provider_transport.get("http_request_started", False),
                "http_response_received": provider_transport.get("http_response_received", False),
                "validation_result": {
                    "executed": runtime_validator.get("executed", False),
                    "passed": runtime_validator.get("passed"),
                    "issue_count": runtime_validator.get("issue_count"),
                    "status": (
                        result.validation_result.status.value
                        if result.validation_result is not None
                        else None
                    ),
                    "issue_codes": (
                        [issue.code for issue in result.validation_result.issues]
                        if result.validation_result is not None
                        else []
                    ),
                },
                "eligibility_result": {
                    "executed": eligibility.get("executed", False),
                    "passed": eligibility.get("passed"),
                    "issue_count": eligibility.get("issue_count"),
                    "status": (
                        result.eligibility_result.status.value
                        if result.eligibility_result is not None
                        else None
                    ),
                    "issue_codes": (
                        [issue.code for issue in result.eligibility_result.issues]
                        if result.eligibility_result is not None
                        else []
                    ),
                },
                "composition_result": {
                    "executed": composer.get("executed", False),
                    "composition_mode": composer.get("composition_mode"),
                    "augmentation_applied": composer.get("augmentation_applied"),
                    "status": (
                        result.composition_result.status.value
                        if result.composition_result is not None
                        else None
                    ),
                    "fallback_reason": (
                        result.composition_result.fallback_reason
                        if result.composition_result is not None
                        else None
                    ),
                },
                "post_processor_result": {
                    "executed": post_processor.get("executed", False),
                    "status": (
                        result.post_processing_result.status.value
                        if result.post_processing_result is not None
                        else post_processor.get("status")
                    ),
                    "message_changed": (
                        result.post_processing_result.message_changed
                        if result.post_processing_result is not None
                        else None
                    ),
                    "metadata_changed": (
                        result.post_processing_result.metadata_changed
                        if result.post_processing_result is not None
                        else None
                    ),
                },
                "stop_stage": stage_name,
                "fallback_reason": diagnostic_reason,
                "exception_type": result.error_type,
                "exception_message": result.error_message,
            },
        )
        if not transport_invoked:
            runtime_trace.mark_llm_not_invoked("controlled_generation", diagnostic_reason)
        runtime_trace.emit()

    def _infer_controlled_generation_stop_stage(
        self,
        *,
        stop_stage: str,
        prompt_builder: dict[str, Any],
        llm_integration: dict[str, Any],
        provider_adapter: dict[str, Any],
        provider_transport: dict[str, Any],
    ) -> str:
        if stop_stage != "orchestration":
            return stop_stage

        if (
            not prompt_builder.get("executed")
            and not llm_integration
            and not provider_adapter
            and not provider_transport
        ):
            return "prompt_builder"
        if provider_transport.get("http_response_received") is False and provider_transport.get("http_request_started"):
            return "provider_transport"
        if provider_adapter.get("request_translated") is False and provider_adapter.get("adapter_selected"):
            return "provider_adapter"
        if prompt_builder.get("executed") and not llm_integration:
            return "prompt_builder"
        if llm_integration:
            return "llm_integration"
        return stop_stage

    def _post_process_runtime_response(
        self,
        *,
        request: LLMControlledGenerationRequest,
        composition_result: LLMRuntimeResponseComposerResult,
    ) -> LLMRuntimeResponsePostProcessingResult:
        try:
            return self._runtime_response_post_processor.process(
                LLMRuntimeResponsePostProcessingRequest(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    final_response=composition_result.final_response,
                    composition_result=composition_result,
                    metadata={
                        "parent_execution_id": request.parent_execution_id,
                        **deepcopy(request.orchestration_request.metadata),
                    },
                )
            )
        except Exception as exc:
            return LLMRuntimeResponsePostProcessingResult(
                request_id=request.request_id,
                correlation_id=request.correlation_id,
                status=LLMRuntimeResponsePostProcessingStatus.FALLBACK,
                final_response=composition_result.final_response,
                original_response=composition_result.final_response,
                message_changed=False,
                metadata_changed=False,
                removed_metadata_keys=[],
                sanitized_presentation_metadata={},
                issues=[],
                diagnostics={
                    "post_processing_failed": True,
                    "error_message": str(exc),
                    "error_type": type(exc).__name__,
                },
            )

    def _execute_shadow_mode(
        self,
        *,
        request: LLMShadowModeRequest,
        decision: AIExecutionDecision,
        runtime_trace: AIRuntimeTraceSession | None = None,
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
            orchestration_result = composition.orchestrator.generate(
                orchestration_request,
                runtime_trace=runtime_trace,
            )
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
            if runtime_trace is not None:
                runtime_trace.mark_llm_not_invoked(
                    "runtime_facade",
                    f"Shadow execution stopped with {type(exc).__name__}: {exc}",
                )
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
