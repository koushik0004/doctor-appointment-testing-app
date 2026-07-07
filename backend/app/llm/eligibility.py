from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.llm.execution_policy import AIExecutionDecision, AIExecutionMode
from app.llm.orchestrator import LLMGenerationOrchestrationRequest
from app.llm.validation import LLMRuntimeResponseValidationResult


class LLMRuntimeResponseEligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


class LLMRuntimeResponseEligibilityIssue(BaseModel):
    code: str = Field(min_length=1)
    path: str = Field(min_length=1)
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseEligibilityRequest(BaseModel):
    request_id: str = Field(min_length=1)
    correlation_id: str | None = None
    policy_decision: AIExecutionDecision
    validation_result: LLMRuntimeResponseValidationResult
    orchestration_request: LLMGenerationOrchestrationRequest
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseEligibilityResult(BaseModel):
    request_id: str
    correlation_id: str | None = None
    status: LLMRuntimeResponseEligibilityStatus
    is_eligible: bool
    eligibility_reason: str
    fallback_reason: str | None = None
    issues: list[LLMRuntimeResponseEligibilityIssue] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseEligibilityEvaluator:
    """Deterministic provider-neutral user-visibility gate for validated runtime responses."""

    _LOW_RISK_VISIBLE_INTENTS = frozenset(
        {
            "UNKNOWN",
            "APPOINTMENT_HELP",
            "CANCEL_APPOINTMENT_HELP",
        }
    )
    _VISIBLE_EXECUTION_MODES = frozenset(
        {
            AIExecutionMode.LLM_ONLY,
            AIExecutionMode.HYBRID,
        }
    )

    def evaluate(
        self,
        request: LLMRuntimeResponseEligibilityRequest,
    ) -> LLMRuntimeResponseEligibilityResult:
        issues: list[LLMRuntimeResponseEligibilityIssue] = []
        policy_decision = request.policy_decision
        validation_result = request.validation_result
        active_intent = request.orchestration_request.active_intent

        if not validation_result.is_valid:
            self._add_issue(
                issues,
                code="invalid_runtime_response",
                path="validation_result",
                message=(
                    "Only validated runtime responses may be evaluated for user "
                    "visibility."
                ),
            )

        if (
            not policy_decision.should_execute_llm
            or policy_decision.execution_mode not in self._VISIBLE_EXECUTION_MODES
        ):
            self._add_issue(
                issues,
                code="policy_not_approved_for_visibility",
                path="policy_decision",
                message=(
                    "Execution policy did not approve the response for user "
                    "visibility."
                ),
            )

        if not self._is_low_risk_intent(active_intent):
            self._add_issue(
                issues,
                code="non_eligible_intent",
                path="orchestration_request.active_intent",
                message=(
                    "The runtime response is reserved for low-risk conversational "
                    "scenarios."
                ),
            )

        eligible = not issues
        diagnostics = {
            "policy_execution_mode": policy_decision.execution_mode.value,
            "policy_primary_owner": policy_decision.primary_owner.value,
            "policy_official_response_owner": policy_decision.official_response_owner.value,
            "policy_should_execute_llm": policy_decision.should_execute_llm,
            "policy_selected_provider_name": policy_decision.selected_provider_name,
            "validation_status": validation_result.status.value,
            "validation_is_valid": validation_result.is_valid,
            "active_intent": active_intent,
            "low_risk_intent": self._is_low_risk_intent(active_intent),
            "issue_count": len(issues),
        }

        return LLMRuntimeResponseEligibilityResult(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            status=(
                LLMRuntimeResponseEligibilityStatus.ELIGIBLE
                if eligible
                else LLMRuntimeResponseEligibilityStatus.INELIGIBLE
            ),
            is_eligible=eligible,
            eligibility_reason=(
                "The validated runtime response is approved for user visibility."
                if eligible
                else (
                    "The validated runtime response is not approved for user "
                    "visibility."
                )
            ),
            fallback_reason=(
                None
                if eligible
                else (
                    "Runtime response eligibility preserved the deterministic "
                    "reply because the request is not an approved low-risk "
                    "conversational scenario."
                )
            ),
            issues=issues,
            diagnostics=diagnostics,
        )

    def _is_low_risk_intent(self, intent_name: str | None) -> bool:
        return intent_name is None or intent_name in self._LOW_RISK_VISIBLE_INTENTS

    def _add_issue(
        self,
        issues: list[LLMRuntimeResponseEligibilityIssue],
        *,
        code: str,
        path: str,
        message: str,
    ) -> None:
        issues.append(
            LLMRuntimeResponseEligibilityIssue(
                code=code,
                path=path,
                message=message,
            )
        )
