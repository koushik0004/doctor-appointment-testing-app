from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.llm.execution_policy import AIExecutionMode
from app.llm.orchestrator import LLMGenerationOrchestrationResult
from app.llm.validation import LLMRuntimeResponseValidationResult
from app.llm.eligibility import LLMRuntimeResponseEligibilityResult


class LLMRuntimeResponse(BaseModel):
    """Provider-neutral final runtime response envelope."""

    message: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseCompositionStatus(str, Enum):
    COMPOSED = "COMPOSED"
    FALLBACK = "FALLBACK"
    FAILED = "FAILED"


class LLMRuntimeResponseCompositionIssue(BaseModel):
    code: str = Field(min_length=1)
    path: str = Field(min_length=1)
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseComposerRequest(BaseModel):
    request_id: str = Field(min_length=1)
    correlation_id: str | None = None
    composition_mode: AIExecutionMode
    deterministic_response: LLMRuntimeResponse | None = None
    validation_result: LLMRuntimeResponseValidationResult | None = None
    eligibility_result: LLMRuntimeResponseEligibilityResult | None = None
    orchestration_result: LLMGenerationOrchestrationResult | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseComposerResult(BaseModel):
    request_id: str
    correlation_id: str | None = None
    composition_mode: AIExecutionMode
    status: LLMRuntimeResponseCompositionStatus
    final_response: LLMRuntimeResponse
    deterministic_response: LLMRuntimeResponse | None = None
    llm_response: LLMRuntimeResponse | None = None
    augmentation_applied: bool = False
    preserved_business_fields: list[str] = Field(default_factory=list)
    fallback_reason: str | None = None
    issues: list[LLMRuntimeResponseCompositionIssue] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseComposer:
    """Deterministic provider-neutral runtime response composer."""

    _SUPPORTED_MODES = frozenset(
        {
            AIExecutionMode.DETERMINISTIC_ONLY,
            AIExecutionMode.LLM_ONLY,
            AIExecutionMode.HYBRID,
        }
    )

    def compose(
        self,
        request: LLMRuntimeResponseComposerRequest,
    ) -> LLMRuntimeResponseComposerResult:
        issues: list[LLMRuntimeResponseCompositionIssue] = []
        deterministic_response = (
            request.deterministic_response.model_copy(deep=True)
            if request.deterministic_response is not None
            else None
        )
        llm_response = self._build_llm_response(
            request.orchestration_result,
            validation_result=request.validation_result,
            eligibility_result=request.eligibility_result,
        )

        if request.composition_mode not in self._SUPPORTED_MODES:
            self._add_issue(
                issues,
                code="unsupported_composition_mode",
                path="composition_mode",
                message=(
                    "Runtime response composition only supports deterministic-only, "
                    "LLM-only, and hybrid modes."
                ),
            )

        llm_allowed = self._is_llm_usable(
            validation_result=request.validation_result,
            eligibility_result=request.eligibility_result,
            llm_response=llm_response,
        )
        fallback_reason: str | None = None
        augmentation_applied = False

        if request.composition_mode is AIExecutionMode.DETERMINISTIC_ONLY:
            final_response = self._compose_deterministic_only(
                deterministic_response=deterministic_response,
                llm_response=llm_response,
                issues=issues,
            )
            status = (
                LLMRuntimeResponseCompositionStatus.COMPOSED
                if deterministic_response is not None
                else LLMRuntimeResponseCompositionStatus.FALLBACK
            )
            if deterministic_response is None:
                fallback_reason = (
                    "Deterministic-only runtime composition had no business response "
                    "to preserve."
                )
        elif request.composition_mode is AIExecutionMode.LLM_ONLY:
            if llm_allowed and llm_response is not None:
                final_response = self._compose_llm_only(llm_response=llm_response)
                status = LLMRuntimeResponseCompositionStatus.COMPOSED
            elif deterministic_response is not None:
                final_response = self._compose_deterministic_only(
                    deterministic_response=deterministic_response,
                    llm_response=llm_response,
                    issues=issues,
                )
                status = LLMRuntimeResponseCompositionStatus.FALLBACK
                fallback_reason = (
                    "LLM-only composition fell back to the deterministic response "
                    "because validated and eligible LLM content was unavailable."
                )
            else:
                final_response = LLMRuntimeResponse()
                status = LLMRuntimeResponseCompositionStatus.FAILED
                fallback_reason = (
                    "LLM-only composition could not produce a final response."
                )
        else:
            if deterministic_response is not None and llm_allowed and llm_response is not None:
                final_response = self._compose_hybrid(
                    deterministic_response=deterministic_response,
                    llm_response=llm_response,
                )
                augmentation_applied = True
                status = LLMRuntimeResponseCompositionStatus.COMPOSED
            elif deterministic_response is not None:
                final_response = self._compose_deterministic_only(
                    deterministic_response=deterministic_response,
                    llm_response=llm_response,
                    issues=issues,
                )
                status = LLMRuntimeResponseCompositionStatus.FALLBACK
                fallback_reason = (
                    "Hybrid composition preserved the deterministic business "
                    "response because validated and eligible LLM augmentation was "
                    "unavailable."
                )
            elif llm_allowed and llm_response is not None:
                final_response = self._compose_llm_only(llm_response=llm_response)
                status = LLMRuntimeResponseCompositionStatus.FALLBACK
                fallback_reason = (
                    "Hybrid composition fell back to LLM-only because the "
                    "deterministic business response was unavailable."
                )
            else:
                final_response = LLMRuntimeResponse()
                status = LLMRuntimeResponseCompositionStatus.FAILED
                fallback_reason = (
                    "Hybrid composition could not produce a final response."
                )

        if llm_response is not None and request.composition_mode is AIExecutionMode.HYBRID:
            augmentation_applied = augmentation_applied or (
                status is LLMRuntimeResponseCompositionStatus.COMPOSED
                and deterministic_response is not None
            )

        final_response = self._annotate_final_response(
            final_response=final_response,
            request=request,
            deterministic_response=deterministic_response,
            llm_response=llm_response,
            augmentation_applied=augmentation_applied,
            fallback_reason=fallback_reason,
        )

        diagnostics = {
            "composition_mode": request.composition_mode.value,
            "validation_provided": request.validation_result is not None,
            "validation_is_valid": (
                request.validation_result.is_valid
                if request.validation_result is not None
                else None
            ),
            "eligibility_provided": request.eligibility_result is not None,
            "eligibility_is_eligible": (
                request.eligibility_result.is_eligible
                if request.eligibility_result is not None
                else None
            ),
            "deterministic_response_present": deterministic_response is not None,
            "llm_response_present": llm_response is not None,
            "augmentation_applied": augmentation_applied,
            "preserved_business_field_count": len(
                self._business_field_names(deterministic_response)
            ),
            "issue_count": len(issues),
        }

        return LLMRuntimeResponseComposerResult(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            composition_mode=request.composition_mode,
            status=status,
            final_response=final_response,
            deterministic_response=deterministic_response,
            llm_response=llm_response,
            augmentation_applied=augmentation_applied,
            preserved_business_fields=self._business_field_names(deterministic_response),
            fallback_reason=fallback_reason,
            issues=issues,
            diagnostics=diagnostics,
        )

    def _build_llm_response(
        self,
        orchestration_result: LLMGenerationOrchestrationResult | None,
        *,
        validation_result: LLMRuntimeResponseValidationResult | None,
        eligibility_result: LLMRuntimeResponseEligibilityResult | None,
    ) -> LLMRuntimeResponse | None:
        if orchestration_result is None:
            return None

        if validation_result is None or not validation_result.is_valid:
            return None

        if eligibility_result is None or not eligibility_result.is_eligible:
            return None

        return LLMRuntimeResponse(
            message=orchestration_result.response_message.content,
            data=deepcopy(orchestration_result.structured_output or {}),
            metadata={
                "provider_name": orchestration_result.provider_name,
                "model_name": orchestration_result.model_name,
                "finish_reason": orchestration_result.finish_reason.value,
                "usage": (
                    orchestration_result.usage.model_dump(mode="json")
                    if orchestration_result.usage is not None
                    else None
                ),
                "citations": [
                    citation.model_dump(mode="json")
                    for citation in orchestration_result.citations
                ],
                "tool_calls": [
                    tool_call.model_dump(mode="json")
                    for tool_call in orchestration_result.tool_calls
                ],
                "reasoning": (
                    orchestration_result.reasoning.model_dump(mode="json")
                    if orchestration_result.reasoning is not None
                    else None
                ),
                "streaming": (
                    orchestration_result.streaming.model_dump(mode="json")
                    if orchestration_result.streaming is not None
                    else None
                ),
                "provider_metadata": deepcopy(orchestration_result.provider_metadata),
                "model_metadata": deepcopy(orchestration_result.model_metadata),
                "metadata": deepcopy(orchestration_result.metadata),
            },
        )

    def _compose_deterministic_only(
        self,
        *,
        deterministic_response: LLMRuntimeResponse | None,
        llm_response: LLMRuntimeResponse | None,
        issues: list[LLMRuntimeResponseCompositionIssue],
    ) -> LLMRuntimeResponse:
        del llm_response
        if deterministic_response is None:
            self._add_issue(
                issues,
                code="missing_deterministic_response",
                path="deterministic_response",
                message=(
                    "Deterministic-only composition requires a deterministic "
                    "business response."
                ),
            )
            return LLMRuntimeResponse()

        return LLMRuntimeResponse(
            message=deterministic_response.message,
            data=deepcopy(deterministic_response.data),
            metadata=deepcopy(deterministic_response.metadata),
        )

    def _compose_llm_only(
        self,
        *,
        llm_response: LLMRuntimeResponse,
    ) -> LLMRuntimeResponse:
        return LLMRuntimeResponse(
            message=llm_response.message,
            data=deepcopy(llm_response.data),
            metadata=deepcopy(llm_response.metadata),
        )

    def _compose_hybrid(
        self,
        *,
        deterministic_response: LLMRuntimeResponse,
        llm_response: LLMRuntimeResponse,
    ) -> LLMRuntimeResponse:
        message = deterministic_response.message
        if llm_response.message.strip():
            message = (
                f"{message}\n\nAdditional guidance:\n{llm_response.message}"
                if message
                else llm_response.message
            )

        metadata = deepcopy(deterministic_response.metadata)
        metadata["runtime_response_composition"] = {
            "mode": AIExecutionMode.HYBRID.value,
            "augmentation_applied": True,
            "llm_provider_name": llm_response.metadata.get("provider_name"),
            "llm_model_name": llm_response.metadata.get("model_name"),
            "additional_guidance": llm_response.message,
        }

        return LLMRuntimeResponse(
            message=message,
            data=deepcopy(deterministic_response.data),
            metadata=metadata,
        )

    def _annotate_final_response(
        self,
        *,
        final_response: LLMRuntimeResponse,
        request: LLMRuntimeResponseComposerRequest,
        deterministic_response: LLMRuntimeResponse | None,
        llm_response: LLMRuntimeResponse | None,
        augmentation_applied: bool,
        fallback_reason: str | None,
    ) -> LLMRuntimeResponse:
        metadata = deepcopy(final_response.metadata)
        metadata["runtime_response_composition"] = {
            "request_id": request.request_id,
            "correlation_id": request.correlation_id,
            "composition_mode": request.composition_mode.value,
            "augmentation_applied": augmentation_applied,
            "fallback_reason": fallback_reason,
            "deterministic_response_present": deterministic_response is not None,
            "llm_response_present": llm_response is not None,
            "metadata": deepcopy(request.metadata),
        }
        metadata["preserved_business_fields"] = self._business_field_names(
            deterministic_response
        )
        return LLMRuntimeResponse(
            message=final_response.message,
            data=deepcopy(final_response.data),
            metadata=metadata,
        )

    def _business_field_names(
        self,
        deterministic_response: LLMRuntimeResponse | None,
    ) -> list[str]:
        if deterministic_response is None:
            return []
        return sorted(deterministic_response.data.keys())

    def _is_llm_usable(
        self,
        *,
        validation_result: LLMRuntimeResponseValidationResult | None,
        eligibility_result: LLMRuntimeResponseEligibilityResult | None,
        llm_response: LLMRuntimeResponse | None,
    ) -> bool:
        return (
            validation_result is not None
            and validation_result.is_valid
            and eligibility_result is not None
            and eligibility_result.is_eligible
            and llm_response is not None
            and bool(llm_response.message.strip())
        )

    def _add_issue(
        self,
        issues: list[LLMRuntimeResponseCompositionIssue],
        *,
        code: str,
        path: str,
        message: str,
    ) -> None:
        issues.append(
            LLMRuntimeResponseCompositionIssue(
                code=code,
                path=path,
                message=message,
            )
        )
