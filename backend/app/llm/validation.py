from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.llm.models import LLMFinishReason, LLMMessageRole
from app.llm.orchestrator import (
    LLMGenerationOrchestrationRequest,
    LLMGenerationOrchestrationResult,
)


class LLMRuntimeResponseValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


class LLMRuntimeResponseValidationIssue(BaseModel):
    code: str = Field(min_length=1)
    path: str = Field(min_length=1)
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseValidationRequest(BaseModel):
    request_id: str = Field(min_length=1)
    correlation_id: str | None = None
    orchestration_request: LLMGenerationOrchestrationRequest
    orchestration_result: LLMGenerationOrchestrationResult
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseValidationResult(BaseModel):
    request_id: str
    correlation_id: str | None = None
    status: LLMRuntimeResponseValidationStatus
    is_valid: bool
    issues: list[LLMRuntimeResponseValidationIssue] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponseValidator:
    """Provider-neutral validator for canonical runtime generation results."""

    def validate(
        self,
        request: LLMRuntimeResponseValidationRequest,
    ) -> LLMRuntimeResponseValidationResult:
        issues: list[LLMRuntimeResponseValidationIssue] = []
        result = request.orchestration_result
        response_message = getattr(result, "response_message", None)
        structured_output_requested = request.orchestration_request.structured_output is not None
        structured_output = getattr(result, "structured_output", None)
        finish_reason = getattr(result, "finish_reason", None)

        self._validate_required_result_fields(result=result, issues=issues)
        self._validate_response_message(
            response_message=response_message,
            issues=issues,
        )
        self._validate_finish_reason(finish_reason=finish_reason, issues=issues)
        self._validate_structured_output(
            structured_output_requested=structured_output_requested,
            structured_output=structured_output,
            issues=issues,
        )
        self._validate_metadata(result=result, issues=issues)

        diagnostics = {
            "response_message_role": (
                response_message.role.value
                if hasattr(response_message, "role") and isinstance(response_message.role, LLMMessageRole)
                else getattr(response_message, "role", None)
            ),
            "response_content_length": (
                len(str(response_message.content).strip())
                if hasattr(response_message, "content") and response_message.content is not None
                else None
            ),
            "structured_output_requested": structured_output_requested,
            "structured_output_present": isinstance(structured_output, dict),
            "finish_reason": (
                finish_reason.value
                if isinstance(finish_reason, LLMFinishReason)
                else finish_reason
            ),
            "provider_name": getattr(result, "provider_name", None),
            "model_name": getattr(result, "model_name", None),
            "issue_count": len(issues),
        }

        return LLMRuntimeResponseValidationResult(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            status=(
                LLMRuntimeResponseValidationStatus.VALID
                if not issues
                else LLMRuntimeResponseValidationStatus.INVALID
            ),
            is_valid=not issues,
            issues=issues,
            diagnostics=diagnostics,
        )

    def _validate_required_result_fields(
        self,
        *,
        result: LLMGenerationOrchestrationResult,
        issues: list[LLMRuntimeResponseValidationIssue],
    ) -> None:
        prompt = getattr(result, "prompt", None)
        if not isinstance(prompt, str) or not prompt.strip():
            self._add_issue(
                issues,
                code="missing_required_canonical_field",
                path="prompt",
                message="The canonical runtime result must include a non-empty rendered prompt.",
            )

        response_message = getattr(result, "response_message", None)
        if response_message is None:
            self._add_issue(
                issues,
                code="missing_required_canonical_field",
                path="response_message",
                message="The canonical runtime result must include a response message.",
            )

        finish_reason = getattr(result, "finish_reason", None)
        if finish_reason is None:
            self._add_issue(
                issues,
                code="missing_required_canonical_field",
                path="finish_reason",
                message="The canonical runtime result must include a finish reason.",
            )

    def _validate_response_message(
        self,
        *,
        response_message: Any,
        issues: list[LLMRuntimeResponseValidationIssue],
    ) -> None:
        if response_message is None:
            return

        role = getattr(response_message, "role", None)
        if not isinstance(role, LLMMessageRole):
            self._add_issue(
                issues,
                code="invalid_canonical_metadata",
                path="response_message.role",
                message="The response message role must be a canonical LLM message role.",
            )
        elif role is not LLMMessageRole.ASSISTANT:
            self._add_issue(
                issues,
                code="invalid_response_message_role",
                path="response_message.role",
                message="The runtime response must be an assistant message.",
            )

        content = getattr(response_message, "content", None)
        if not isinstance(content, str):
            self._add_issue(
                issues,
                code="missing_required_canonical_field",
                path="response_message.content",
                message="The response message content must be a string.",
            )
            return

        if content == "":
            self._add_issue(
                issues,
                code="empty_runtime_response",
                path="response_message.content",
                message="The runtime response content must not be empty.",
            )
        elif not content.strip():
            self._add_issue(
                issues,
                code="whitespace_runtime_response",
                path="response_message.content",
                message="The runtime response content must not be whitespace only.",
            )

    def _validate_finish_reason(
        self,
        *,
        finish_reason: Any,
        issues: list[LLMRuntimeResponseValidationIssue],
    ) -> None:
        if isinstance(finish_reason, LLMFinishReason):
            return

        self._add_issue(
            issues,
            code="invalid_finish_reason",
            path="finish_reason",
            message="The runtime response finish reason must be canonical and recognized.",
        )

    def _validate_structured_output(
        self,
        *,
        structured_output_requested: bool,
        structured_output: Any,
        issues: list[LLMRuntimeResponseValidationIssue],
    ) -> None:
        if structured_output is None:
            if structured_output_requested:
                self._add_issue(
                    issues,
                    code="missing_structured_output",
                    path="structured_output",
                    message="The requested structured output is missing from the runtime response.",
                )
            return

        if not isinstance(structured_output, Mapping):
            self._add_issue(
                issues,
                code="malformed_structured_output",
                path="structured_output",
                message="The structured output must be a canonical mapping when present.",
            )
            return

        if structured_output_requested and not dict(structured_output):
            self._add_issue(
                issues,
                code="malformed_structured_output",
                path="structured_output",
                message="The structured output must contain canonical content when requested.",
            )

    def _validate_metadata(
        self,
        *,
        result: LLMGenerationOrchestrationResult,
        issues: list[LLMRuntimeResponseValidationIssue],
    ) -> None:
        self._validate_mapping(
            value=getattr(result, "provider_metadata", None),
            path="provider_metadata",
            issues=issues,
        )
        self._validate_mapping(
            value=getattr(result, "model_metadata", None),
            path="model_metadata",
            issues=issues,
        )
        self._validate_mapping(
            value=getattr(result, "metadata", None),
            path="metadata",
            issues=issues,
        )

        response_message = getattr(result, "response_message", None)
        if response_message is not None:
            self._validate_mapping(
                value=getattr(response_message, "metadata", None),
                path="response_message.metadata",
                issues=issues,
            )

        reasoning = getattr(result, "reasoning", None)
        if reasoning is not None:
            self._validate_mapping(
                value=getattr(reasoning, "metadata", None),
                path="reasoning.metadata",
                issues=issues,
            )

        streaming = getattr(result, "streaming", None)
        if streaming is not None:
            self._validate_mapping(
                value=getattr(streaming, "metadata", None),
                path="streaming.metadata",
                issues=issues,
            )

        citations = getattr(result, "citations", None)
        if isinstance(citations, list):
            for index, citation in enumerate(citations):
                self._validate_mapping(
                    value=getattr(citation, "metadata", None),
                    path=f"citations[{index}].metadata",
                    issues=issues,
                )

    def _validate_mapping(
        self,
        *,
        value: Any,
        path: str,
        issues: list[LLMRuntimeResponseValidationIssue],
    ) -> None:
        if value is None:
            return
        if not isinstance(value, Mapping):
            self._add_issue(
                issues,
                code="invalid_canonical_metadata",
                path=path,
                message="The runtime response metadata must be a canonical mapping.",
            )

    def _add_issue(
        self,
        issues: list[LLMRuntimeResponseValidationIssue],
        *,
        code: str,
        path: str,
        message: str,
    ) -> None:
        issues.append(
            LLMRuntimeResponseValidationIssue(
                code=code,
                path=path,
                message=message,
            )
        )
