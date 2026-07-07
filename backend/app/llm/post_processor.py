from __future__ import annotations

import re
from collections.abc import Mapping
from copy import deepcopy
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.llm.composer import LLMRuntimeResponse, LLMRuntimeResponseComposerResult


class LLMRuntimeResponsePostProcessingStatus(str, Enum):
    PROCESSED = "PROCESSED"
    FALLBACK = "FALLBACK"


class LLMRuntimeResponsePostProcessingIssue(BaseModel):
    code: str = Field(min_length=1)
    path: str = Field(min_length=1)
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponsePostProcessingRequest(BaseModel):
    request_id: str = Field(min_length=1)
    correlation_id: str | None = None
    final_response: LLMRuntimeResponse | None = None
    composition_result: LLMRuntimeResponseComposerResult | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponsePostProcessingResult(BaseModel):
    request_id: str
    correlation_id: str | None = None
    status: LLMRuntimeResponsePostProcessingStatus
    final_response: LLMRuntimeResponse
    original_response: LLMRuntimeResponse | None = None
    message_changed: bool = False
    metadata_changed: bool = False
    removed_metadata_keys: list[str] = Field(default_factory=list)
    sanitized_presentation_metadata: dict[str, Any] = Field(default_factory=dict)
    issues: list[LLMRuntimeResponsePostProcessingIssue] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMRuntimeResponsePostProcessor:
    """Deterministic provider-neutral runtime response post processor."""

    _PRESENTATION_METADATA_KEYS = frozenset(
        {
            "display_metadata",
            "presentation",
            "presentation_metadata",
            "rendering_metadata",
            "ui_metadata",
        }
    )

    def process(
        self,
        request: LLMRuntimeResponsePostProcessingRequest,
    ) -> LLMRuntimeResponsePostProcessingResult:
        issues: list[LLMRuntimeResponsePostProcessingIssue] = []
        original_response = (
            request.final_response.model_copy(deep=True)
            if request.final_response is not None
            else None
        )
        status = LLMRuntimeResponsePostProcessingStatus.PROCESSED
        if original_response is None:
            issues.append(
                LLMRuntimeResponsePostProcessingIssue(
                    code="missing_final_response",
                    path="final_response",
                    message=(
                        "Runtime response post-processing requires a final "
                        "response envelope."
                    ),
                )
            )
            status = LLMRuntimeResponsePostProcessingStatus.FALLBACK
        response = original_response or LLMRuntimeResponse()

        normalized_message, message_diagnostics = self._normalize_message(
            response.message
        )
        sanitized_metadata, sanitized_presentation_metadata, removed_metadata_keys = (
            self._sanitize_metadata(response.metadata)
        )
        final_response = LLMRuntimeResponse(
            message=normalized_message,
            data=deepcopy(response.data),
            metadata=sanitized_metadata,
        )

        metadata_changed = sanitized_metadata != response.metadata
        message_changed = normalized_message != response.message
        diagnostics = {
            "request_id": request.request_id,
            "correlation_id": request.correlation_id,
            "original_message_length": len(response.message),
            "normalized_message_length": len(normalized_message),
            "message_changed": message_changed,
            "metadata_changed": metadata_changed,
            "removed_metadata_keys": list(removed_metadata_keys),
            "presentation_metadata_removed": bool(sanitized_presentation_metadata),
            "composition_mode": (
                request.composition_result.composition_mode.value
                if request.composition_result is not None
                else None
            ),
            "composition_status": (
                request.composition_result.status.value
                if request.composition_result is not None
                else None
            ),
            "composition_augmentation_applied": (
                request.composition_result.augmentation_applied
                if request.composition_result is not None
                else None
            ),
            **message_diagnostics,
            "issue_count": len(issues),
        }

        final_response = self._annotate_final_response(
            response=final_response,
            request=request,
            original_response=original_response,
            removed_metadata_keys=removed_metadata_keys,
            sanitized_presentation_metadata=sanitized_presentation_metadata,
            diagnostics=diagnostics,
            message_changed=message_changed,
            metadata_changed=metadata_changed,
        )

        return LLMRuntimeResponsePostProcessingResult(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            status=status,
            final_response=final_response,
            original_response=original_response,
            message_changed=message_changed,
            metadata_changed=metadata_changed,
            removed_metadata_keys=list(removed_metadata_keys),
            sanitized_presentation_metadata=deepcopy(
                sanitized_presentation_metadata
            ),
            issues=issues,
            diagnostics=diagnostics,
        )

    def _normalize_message(self, message: str) -> tuple[str, dict[str, Any]]:
        normalized = message.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")

        trailing_spaces_removed = sum(len(line) - len(line.rstrip()) for line in lines)
        normalized = "\n".join(line.rstrip() for line in lines)

        heading_changes = 0

        def _normalize_heading(match: re.Match[str]) -> str:
            nonlocal heading_changes
            heading_changes += 1
            return f"{match.group(1)} {match.group(2)}"

        normalized = re.sub(
            r"(?m)^(#{1,6})(\S)",
            _normalize_heading,
            normalized,
        )

        bullet_changes = 0

        def _normalize_bullet(match: re.Match[str]) -> str:
            nonlocal bullet_changes
            bullet_changes += 1
            return f"{match.group(1)} "

        normalized = re.sub(
            r"(?m)^([ \t]*[-*+])\s+",
            _normalize_bullet,
            normalized,
        )

        ordered_list_changes = 0

        def _normalize_ordered_list(match: re.Match[str]) -> str:
            nonlocal ordered_list_changes
            ordered_list_changes += 1
            return f"{match.group(1)} "

        normalized = re.sub(
            r"(?m)^([ \t]*\d+\.)\s+",
            _normalize_ordered_list,
            normalized,
        )

        blockquote_changes = 0

        def _normalize_blockquote(match: re.Match[str]) -> str:
            nonlocal blockquote_changes
            blockquote_changes += 1
            return "> "

        normalized = re.sub(
            r"(?m)^>\s*",
            _normalize_blockquote,
            normalized,
        )

        duplicate_blank_line_groups = 0
        duplicate_blank_lines_removed = 0

        def _collapse_blank_lines(match: re.Match[str]) -> str:
            nonlocal duplicate_blank_line_groups, duplicate_blank_lines_removed
            duplicate_blank_line_groups += 1
            newline_count = match.group(0).count("\n")
            duplicate_blank_lines_removed += max(0, newline_count - 2)
            return "\n\n"

        normalized = re.sub(r"\n{3,}", _collapse_blank_lines, normalized)
        normalized = normalized.strip()

        diagnostics = {
            "trailing_spaces_removed": trailing_spaces_removed,
            "heading_markdown_normalized": heading_changes > 0,
            "bullet_markdown_normalized": bullet_changes > 0,
            "ordered_list_markdown_normalized": ordered_list_changes > 0,
            "blockquote_markdown_normalized": blockquote_changes > 0,
            "duplicate_blank_line_groups": duplicate_blank_line_groups,
            "duplicate_blank_lines_removed": duplicate_blank_lines_removed,
        }
        return normalized, diagnostics

    def _sanitize_metadata(
        self,
        metadata: Mapping[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
        sanitized = deepcopy(dict(metadata))
        sanitized_presentation_metadata: dict[str, Any] = {}
        removed_keys: list[str] = []

        for key in sorted(self._PRESENTATION_METADATA_KEYS):
            if key not in sanitized:
                continue
            removed_keys.append(key)
            sanitized_presentation_metadata[key] = sanitized.pop(key)

        return sanitized, sanitized_presentation_metadata, removed_keys

    def _annotate_final_response(
        self,
        *,
        response: LLMRuntimeResponse,
        request: LLMRuntimeResponsePostProcessingRequest,
        original_response: LLMRuntimeResponse | None,
        removed_metadata_keys: list[str],
        sanitized_presentation_metadata: dict[str, Any],
        diagnostics: dict[str, Any],
        message_changed: bool,
        metadata_changed: bool,
    ) -> LLMRuntimeResponse:
        metadata = deepcopy(response.metadata)
        metadata["runtime_response_post_processing"] = {
            "request_id": request.request_id,
            "correlation_id": request.correlation_id,
            "message_changed": message_changed,
            "metadata_changed": metadata_changed,
            "removed_metadata_keys": list(removed_metadata_keys),
            "sanitized_presentation_metadata": deepcopy(
                sanitized_presentation_metadata
            ),
            "composition_mode": (
                request.composition_result.composition_mode.value
                if request.composition_result is not None
                else None
            ),
            "composition_status": (
                request.composition_result.status.value
                if request.composition_result is not None
                else None
            ),
            "original_response_present": original_response is not None,
            "metadata": deepcopy(request.metadata),
        }
        metadata["runtime_response_post_processing_diagnostics"] = deepcopy(
            diagnostics
        )
        return LLMRuntimeResponse(
            message=response.message,
            data=deepcopy(response.data),
            metadata=metadata,
        )
