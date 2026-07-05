from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.llm.activation import LLMRuntimeActivationStatus

if TYPE_CHECKING:
    from app.llm.composition import LLMRuntimeCompositionRoot


class AIExecutionMode(str, Enum):
    WORKFLOW_ONLY = "WORKFLOW_ONLY"
    DETERMINISTIC_ONLY = "DETERMINISTIC_ONLY"
    KNOWLEDGE_ONLY = "KNOWLEDGE_ONLY"
    LLM_ONLY = "LLM_ONLY"
    HYBRID = "HYBRID"
    SHADOW = "SHADOW"


class AIExecutionOwner(str, Enum):
    WORKFLOW = "WORKFLOW"
    KNOWLEDGE = "KNOWLEDGE"
    DETERMINISTIC = "DETERMINISTIC"
    LLM = "LLM"


class AIExecutionFallbackStrategy(str, Enum):
    NONE = "NONE"
    USE_WORKFLOW = "USE_WORKFLOW"
    USE_KNOWLEDGE = "USE_KNOWLEDGE"
    USE_DETERMINISTIC = "USE_DETERMINISTIC"


class AIExecutionDiagnosticSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AIExecutionDiagnostic(BaseModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: AIExecutionDiagnosticSeverity = AIExecutionDiagnosticSeverity.INFO
    blocking: bool = False
    metadata: dict[str, str | bool] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class AIExecutionActivationSnapshot(BaseModel):
    llm_enabled: bool = False
    shadow_mode: bool = False
    generation_allowed: bool = False
    generation_available: bool = False
    provider_readiness: bool = False
    selected_provider_name: str | None = None
    selected_provider_enabled: bool = False
    selected_provider_healthy: bool = False
    status_reason: str = ""

    model_config = ConfigDict(str_strip_whitespace=True)


class AIExecutionPolicyRequest(BaseModel):
    preferred_mode: AIExecutionMode = AIExecutionMode.DETERMINISTIC_ONLY
    intent_name: str | None = None
    has_active_workflow: bool = False
    knowledge_eligible: bool = False
    knowledge_match_available: bool = False
    deterministic_available: bool = True

    model_config = ConfigDict(str_strip_whitespace=True)


class AIExecutionDecision(BaseModel):
    requested_mode: AIExecutionMode
    execution_mode: AIExecutionMode
    primary_owner: AIExecutionOwner
    official_response_owner: AIExecutionOwner
    selected_provider_name: str | None = None
    activation: AIExecutionActivationSnapshot
    fallback_strategy: AIExecutionFallbackStrategy = AIExecutionFallbackStrategy.NONE
    fallback_owner: AIExecutionOwner | None = None
    should_execute_workflow: bool = False
    should_execute_knowledge: bool = False
    should_execute_deterministic: bool = False
    should_execute_llm: bool = False
    should_execute_shadow: bool = False
    routing_reason: str = Field(min_length=1)
    fallback_reason: str | None = None
    diagnostics: list[AIExecutionDiagnostic] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


@dataclass(frozen=True)
class AIExecutionPolicyResult:
    decision: AIExecutionDecision


class AIExecutionPolicyEvaluator:
    """Deterministic provider-neutral execution policy for future runtime routing."""

    _WORKFLOW_INTENTS = frozenset(
        {
            "BOOK_APPOINTMENT",
            "CANCEL_APPOINTMENT",
            "APPOINTMENT_CONFIRMATION",
        }
    )

    def evaluate(
        self,
        *,
        request: AIExecutionPolicyRequest,
        activation_status: LLMRuntimeActivationStatus,
    ) -> AIExecutionDecision:
        activation = self._build_activation_snapshot(activation_status)

        if self._workflow_owns_request(request):
            return AIExecutionDecision(
                requested_mode=request.preferred_mode,
                execution_mode=AIExecutionMode.WORKFLOW_ONLY,
                primary_owner=AIExecutionOwner.WORKFLOW,
                official_response_owner=AIExecutionOwner.WORKFLOW,
                activation=activation,
                fallback_strategy=AIExecutionFallbackStrategy.USE_WORKFLOW,
                fallback_owner=AIExecutionOwner.WORKFLOW,
                should_execute_workflow=True,
                routing_reason=(
                    "Workflow ownership is mandatory for booking, cancellation, "
                    "appointment confirmation, and active workflow continuation."
                ),
                diagnostics=[
                    AIExecutionDiagnostic(
                        code="workflow_owned_request",
                        message=(
                            "Execution policy preserved workflow ownership and skipped "
                            "knowledge, deterministic, and LLM routing."
                        ),
                    )
                ],
            )

        baseline_owner = self._resolve_baseline_owner(request)
        baseline_mode = (
            AIExecutionMode.KNOWLEDGE_ONLY
            if baseline_owner == AIExecutionOwner.KNOWLEDGE
            else AIExecutionMode.DETERMINISTIC_ONLY
        )
        fallback_strategy = (
            AIExecutionFallbackStrategy.USE_KNOWLEDGE
            if baseline_owner == AIExecutionOwner.KNOWLEDGE
            else AIExecutionFallbackStrategy.USE_DETERMINISTIC
        )

        if request.preferred_mode == AIExecutionMode.LLM_ONLY:
            if activation.generation_available:
                return self._decision_for_llm_only(request, activation)
            return self._fallback_decision(
                request=request,
                activation=activation,
                baseline_owner=baseline_owner,
                baseline_mode=baseline_mode,
                fallback_strategy=fallback_strategy,
                fallback_reason=(
                    "LLM-only execution is unavailable because runtime activation is not "
                    "generation-ready."
                ),
                diagnostic_code="llm_only_unavailable",
            )

        if request.preferred_mode == AIExecutionMode.HYBRID:
            if activation.generation_available:
                return self._decision_for_hybrid(
                    request=request,
                    activation=activation,
                    baseline_owner=baseline_owner,
                )
            return self._fallback_decision(
                request=request,
                activation=activation,
                baseline_owner=baseline_owner,
                baseline_mode=baseline_mode,
                fallback_strategy=fallback_strategy,
                fallback_reason=(
                    "Hybrid execution fell back because runtime activation is not "
                    "generation-ready."
                ),
                diagnostic_code="hybrid_unavailable",
            )

        if request.preferred_mode == AIExecutionMode.SHADOW:
            if activation.shadow_mode and activation.generation_available:
                return self._decision_for_shadow(
                    request=request,
                    activation=activation,
                    baseline_owner=baseline_owner,
                )
            return self._fallback_decision(
                request=request,
                activation=activation,
                baseline_owner=baseline_owner,
                baseline_mode=baseline_mode,
                fallback_strategy=fallback_strategy,
                fallback_reason=(
                    "Shadow execution fell back because shadow mode or runtime generation "
                    "availability is not enabled."
                ),
                diagnostic_code="shadow_unavailable",
            )

        return self._baseline_decision(
            request=request,
            activation=activation,
            baseline_owner=baseline_owner,
            baseline_mode=baseline_mode,
        )

    def _workflow_owns_request(self, request: AIExecutionPolicyRequest) -> bool:
        return request.has_active_workflow or request.intent_name in self._WORKFLOW_INTENTS

    def _resolve_baseline_owner(
        self,
        request: AIExecutionPolicyRequest,
    ) -> AIExecutionOwner:
        if request.knowledge_eligible and request.knowledge_match_available:
            return AIExecutionOwner.KNOWLEDGE
        return AIExecutionOwner.DETERMINISTIC

    def _baseline_decision(
        self,
        *,
        request: AIExecutionPolicyRequest,
        activation: AIExecutionActivationSnapshot,
        baseline_owner: AIExecutionOwner,
        baseline_mode: AIExecutionMode,
    ) -> AIExecutionDecision:
        return AIExecutionDecision(
            requested_mode=request.preferred_mode,
            execution_mode=baseline_mode,
            primary_owner=baseline_owner,
            official_response_owner=baseline_owner,
            selected_provider_name=activation.selected_provider_name,
            activation=activation,
            should_execute_knowledge=baseline_owner == AIExecutionOwner.KNOWLEDGE,
            should_execute_deterministic=baseline_owner == AIExecutionOwner.DETERMINISTIC,
            routing_reason=self._baseline_reason(baseline_owner),
            diagnostics=self._baseline_diagnostics(baseline_owner, activation),
        )

    def _decision_for_llm_only(
        self,
        request: AIExecutionPolicyRequest,
        activation: AIExecutionActivationSnapshot,
    ) -> AIExecutionDecision:
        return AIExecutionDecision(
            requested_mode=request.preferred_mode,
            execution_mode=AIExecutionMode.LLM_ONLY,
            primary_owner=AIExecutionOwner.LLM,
            official_response_owner=AIExecutionOwner.LLM,
            selected_provider_name=activation.selected_provider_name,
            activation=activation,
            should_execute_llm=True,
            routing_reason=(
                "LLM-only execution was selected because the caller explicitly requested "
                "LLM participation and runtime activation is generation-ready."
            ),
            diagnostics=[
                AIExecutionDiagnostic(
                    code="llm_execution_selected",
                    message=(
                        "Execution policy selected LLM-only routing without changing "
                        "workflow or knowledge ownership rules."
                    ),
                )
            ],
        )

    def _decision_for_hybrid(
        self,
        *,
        request: AIExecutionPolicyRequest,
        activation: AIExecutionActivationSnapshot,
        baseline_owner: AIExecutionOwner,
    ) -> AIExecutionDecision:
        return AIExecutionDecision(
            requested_mode=request.preferred_mode,
            execution_mode=AIExecutionMode.HYBRID,
            primary_owner=baseline_owner,
            official_response_owner=baseline_owner,
            selected_provider_name=activation.selected_provider_name,
            activation=activation,
            should_execute_knowledge=baseline_owner == AIExecutionOwner.KNOWLEDGE,
            should_execute_deterministic=baseline_owner == AIExecutionOwner.DETERMINISTIC,
            should_execute_llm=True,
            routing_reason=(
                "Hybrid execution preserved the baseline deterministic owner while allowing "
                "optional LLM participation."
            ),
            diagnostics=[
                AIExecutionDiagnostic(
                    code="hybrid_execution_selected",
                    message=(
                        "Execution policy kept the existing deterministic owner as the "
                        "official response path and allowed LLM participation."
                    ),
                )
            ],
        )

    def _decision_for_shadow(
        self,
        *,
        request: AIExecutionPolicyRequest,
        activation: AIExecutionActivationSnapshot,
        baseline_owner: AIExecutionOwner,
    ) -> AIExecutionDecision:
        return AIExecutionDecision(
            requested_mode=request.preferred_mode,
            execution_mode=AIExecutionMode.SHADOW,
            primary_owner=baseline_owner,
            official_response_owner=baseline_owner,
            selected_provider_name=activation.selected_provider_name,
            activation=activation,
            should_execute_knowledge=baseline_owner == AIExecutionOwner.KNOWLEDGE,
            should_execute_deterministic=baseline_owner == AIExecutionOwner.DETERMINISTIC,
            should_execute_llm=True,
            should_execute_shadow=True,
            routing_reason=(
                "Shadow execution preserved the official deterministic owner and allowed "
                "independent hidden LLM execution."
            ),
            diagnostics=[
                AIExecutionDiagnostic(
                    code="shadow_execution_selected",
                    message=(
                        "Execution policy enabled hidden LLM shadow execution while keeping "
                        "the official response unchanged."
                    ),
                )
            ],
        )

    def _fallback_decision(
        self,
        *,
        request: AIExecutionPolicyRequest,
        activation: AIExecutionActivationSnapshot,
        baseline_owner: AIExecutionOwner,
        baseline_mode: AIExecutionMode,
        fallback_strategy: AIExecutionFallbackStrategy,
        fallback_reason: str,
        diagnostic_code: str,
    ) -> AIExecutionDecision:
        return AIExecutionDecision(
            requested_mode=request.preferred_mode,
            execution_mode=baseline_mode,
            primary_owner=baseline_owner,
            official_response_owner=baseline_owner,
            selected_provider_name=activation.selected_provider_name,
            activation=activation,
            fallback_strategy=fallback_strategy,
            fallback_owner=baseline_owner,
            should_execute_knowledge=baseline_owner == AIExecutionOwner.KNOWLEDGE,
            should_execute_deterministic=baseline_owner == AIExecutionOwner.DETERMINISTIC,
            routing_reason=self._baseline_reason(baseline_owner),
            fallback_reason=fallback_reason,
            diagnostics=[
                AIExecutionDiagnostic(
                    code=diagnostic_code,
                    message=fallback_reason,
                    severity=AIExecutionDiagnosticSeverity.WARNING,
                    blocking=True,
                    metadata={
                        "requested_mode": request.preferred_mode.value,
                        "selected_provider_name": activation.selected_provider_name or "",
                    },
                )
            ],
        )

    def _baseline_reason(self, baseline_owner: AIExecutionOwner) -> str:
        if baseline_owner == AIExecutionOwner.KNOWLEDGE:
            return (
                "Vector-less RAG retained ownership because a deterministic knowledge "
                "match was available and no workflow owned the request."
            )
        return (
            "Deterministic chat remained the default production execution path because "
            "no workflow owned the request and no knowledge route overrode it."
        )

    def _baseline_diagnostics(
        self,
        baseline_owner: AIExecutionOwner,
        activation: AIExecutionActivationSnapshot,
    ) -> list[AIExecutionDiagnostic]:
        if baseline_owner == AIExecutionOwner.KNOWLEDGE:
            return [
                AIExecutionDiagnostic(
                    code="knowledge_execution_selected",
                    message=(
                        "Execution policy selected deterministic knowledge routing before "
                        "deterministic fallback."
                    ),
                )
            ]
        if activation.generation_available:
            return [
                AIExecutionDiagnostic(
                    code="deterministic_default_selected",
                    message=(
                        "Execution policy kept deterministic chat as the official default "
                        "even though LLM activation is available."
                    ),
                )
            ]
        return [
            AIExecutionDiagnostic(
                code="deterministic_fallback_selected",
                message=(
                    "Execution policy kept deterministic chat as the safe default because "
                    "LLM participation is unavailable or not requested."
                ),
            )
        ]

    def _build_activation_snapshot(
        self,
        activation_status: LLMRuntimeActivationStatus,
    ) -> AIExecutionActivationSnapshot:
        return AIExecutionActivationSnapshot(
            llm_enabled=activation_status.llm_enabled,
            shadow_mode=activation_status.shadow_mode,
            generation_allowed=activation_status.generation_allowed,
            generation_available=activation_status.generation_available,
            provider_readiness=activation_status.provider_readiness,
            selected_provider_name=activation_status.selected_provider_name,
            selected_provider_enabled=activation_status.selected_provider_enabled,
            selected_provider_healthy=activation_status.selected_provider_healthy,
            status_reason=activation_status.status_reason,
        )


class AIExecutionPolicyService:
    """Convenience wrapper that evaluates execution policy from composed runtime state."""

    def __init__(
        self,
        *,
        composition_root: LLMRuntimeCompositionRoot,
        evaluator: AIExecutionPolicyEvaluator | None = None,
    ) -> None:
        self._composition_root = composition_root
        self._evaluator = evaluator if evaluator is not None else AIExecutionPolicyEvaluator()

    def evaluate(
        self,
        request: AIExecutionPolicyRequest,
    ) -> AIExecutionPolicyResult:
        composition = self._composition_root.compose()
        decision = self._evaluator.evaluate(
            request=request,
            activation_status=composition.activation_status,
        )
        return AIExecutionPolicyResult(decision=decision)
