from __future__ import annotations

import json
import logging
import re
import traceback
from copy import deepcopy
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)
_TRACE_LOGGER_NAME = "ai.runtime.trace"
_TRACE_LOG_PATH = Path(__file__).resolve().parents[3] / "logs" / "ai-runtime-trace.log"
_TRACE_LOGGER_LOCK = Lock()
_STAGE_NAMES = (
    "conversation_manager",
    "workflow_engine",
    "vectorless_rag",
    "execution_policy",
    "runtime_facade",
    "prompt_builder",
    "llm_integration",
    "provider_adapter",
    "provider_transport",
    "runtime_validator",
    "eligibility",
    "composer",
    "post_processor",
    "final_response",
)

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
_LABELLED_NAME_RE = re.compile(
    r"\b(full name|patient name|my name is|name is|i am)\b\s*[:\-]?\s*([A-Za-z][A-Za-z\s'.-]{1,60})",
    re.IGNORECASE,
)


def _get_trace_logger() -> logging.Logger:
    trace_logger = logging.getLogger(_TRACE_LOGGER_NAME)
    with _TRACE_LOGGER_LOCK:
        trace_logger.setLevel(logging.INFO)
        trace_logger.propagate = False
        if not any(getattr(handler, "_ai_runtime_trace_handler", False) for handler in trace_logger.handlers):
            _TRACE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(
                _TRACE_LOG_PATH,
                maxBytes=5 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            handler._ai_runtime_trace_handler = True  # type: ignore[attr-defined]
            handler.setFormatter(logging.Formatter("%(message)s"))
            trace_logger.addHandler(handler)
    return trace_logger


def _default_stage_payload() -> dict[str, Any]:
    return {
        "entered": False,
        "completed": False,
        "duration_ms": None,
        "status": "NOT_STARTED",
    }


class AIRuntimeTraceSession:
    def __init__(
        self,
        *,
        enabled: bool,
        request_id: str | None = None,
        conversation_id: str | None = None,
    ) -> None:
        self.enabled = enabled
        self.trace_id = str(uuid4()) if enabled else ""
        self._lock = Lock()
        self._emitted = False
        self._started_at = datetime.now(timezone.utc)
        self._payload: dict[str, Any] = {
            "trace_id": self.trace_id,
            "trace_name": "AI Runtime Trace",
            "request_id": request_id or str(uuid4()),
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": None,
            "intent": None,
            "execution_mode": None,
            "selected_provider": None,
            "provider_health": None,
            "activation_status": {},
            "llm_not_invoked": False,
            "stop_component": None,
            "stop_reason": None,
            "final_response_source": None,
            "final_response_preview": None,
            "latency_ms": None,
            "exceptions": [],
        }
        for stage_name in _STAGE_NAMES:
            self._payload[stage_name] = _default_stage_payload()

    def attach_user_message(self, message: str) -> None:
        if not self.enabled:
            return
        self.set_root("user_message", self._redact_user_message(message))

    def set_root(self, key: str, value: Any) -> None:
        if not self.enabled:
            return
        with self._lock:
            self._payload[key] = deepcopy(value)

    def set_final_response(self, *, source: str | None, preview: str | None) -> None:
        if not self.enabled:
            return
        with self._lock:
            self._payload["final_response_source"] = source
            self._payload["final_response_preview"] = preview

    def record_exception(
        self,
        component: str,
        exc: BaseException,
        *,
        converted_to_fallback: bool = False,
    ) -> None:
        if not self.enabled:
            return
        stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        exception_record = {
            "component": component,
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "stack_trace": stack_trace,
            "converted_to_fallback": converted_to_fallback,
        }
        with self._lock:
            exceptions = self._payload.setdefault("exceptions", [])
            if isinstance(exceptions, list):
                exceptions.append(exception_record)
            self._payload["exception_type"] = exception_record["exception_type"]
            self._payload["exception_message"] = exception_record["message"]
            self._payload["exception_component"] = component
            self._payload["exception_stack_trace"] = stack_trace
            if component in _STAGE_NAMES:
                stage_payload = self._payload.setdefault(component, _default_stage_payload())
                if isinstance(stage_payload, dict):
                    stage_payload["entered"] = True
                    stage_payload["completed"] = False
                    stage_payload["status"] = "FAILED"

    def update_stage(self, stage: str, values: dict[str, Any]) -> None:
        if not self.enabled:
            return
        with self._lock:
            current = self._payload.setdefault(
                stage,
                _default_stage_payload() if stage in _STAGE_NAMES else {},
            )
            if isinstance(current, dict):
                current.update(deepcopy(values))
                if stage in _STAGE_NAMES:
                    self._normalize_stage_payload(current, values)
            else:
                self._payload[stage] = deepcopy(values)

    def snapshot(self) -> dict[str, Any]:
        if not self.enabled:
            return {}
        with self._lock:
            return deepcopy(self._payload)

    def mark_llm_not_invoked(self, component: str, reason: str) -> None:
        if not self.enabled:
            return
        with self._lock:
            if self._payload.get("stop_component") is not None:
                return
            self._payload["llm_not_invoked"] = True
            self._payload["stop_component"] = component
            self._payload["stop_reason"] = reason

    def emit(self) -> None:
        if not self.enabled:
            return
        with self._lock:
            if self._emitted:
                return
            self._finalize_payload(self._payload)
            self._payload["latency_ms"] = round(
                (datetime.now(timezone.utc) - self._started_at).total_seconds() * 1000,
                3,
            )
            payload = deepcopy(self._payload)
            self._emitted = True
        serialized = json.dumps(payload, sort_keys=True, default=str)
        trace_logger = _get_trace_logger()
        try:
            record = trace_logger.makeRecord(
                trace_logger.name,
                logging.INFO,
                __file__,
                0,
                serialized,
                args=(),
                exc_info=None,
                func=None,
                extra=None,
            )
            trace_logger.handle(record)
            for handler in trace_logger.handlers:
                handler.flush()
        except Exception:
            logger.exception("Failed to write AI runtime trace.")

    def _finalize_payload(self, payload: dict[str, Any]) -> None:
        activation_status = payload.get("activation_status")
        if payload.get("provider_health") is None:
            if isinstance(activation_status, dict):
                payload["provider_health"] = activation_status.get("selected_provider_healthy")
            if payload.get("provider_health") is None:
                execution_policy = payload.get("execution_policy")
                if isinstance(execution_policy, dict):
                    payload["provider_health"] = execution_policy.get("provider_healthy")

        for stage_name in _STAGE_NAMES:
            stage_payload = payload.setdefault(stage_name, _default_stage_payload())
            if isinstance(stage_payload, dict):
                self._normalize_stage_payload(stage_payload, {})
                if stage_payload.get("status") == "IN_PROGRESS":
                    stage_payload["completed"] = True
                    stage_payload["status"] = "SUCCEEDED"

    def _normalize_stage_payload(
        self,
        stage_payload: dict[str, Any],
        updates: dict[str, Any],
    ) -> None:
        explicit_entered = "entered" in updates
        explicit_completed = "completed" in updates
        explicit_status = "status" in updates
        stage_payload.setdefault("entered", False)
        stage_payload.setdefault("completed", False)
        stage_payload.setdefault("duration_ms", None)

        observed = any(
            key not in {"entered", "completed", "duration_ms", "status"}
            for key in stage_payload
        )
        if observed and not explicit_entered and not stage_payload.get("entered"):
            stage_payload["entered"] = True

        if stage_payload.get("skipped") is True or updates.get("executed") is False:
            if not explicit_completed:
                stage_payload["completed"] = True
            if not explicit_status:
                stage_payload["status"] = "SKIPPED"
            return

        if stage_payload.get("status") == "FAILED" and not explicit_status:
            return

        if explicit_status and isinstance(stage_payload.get("status"), str):
            stage_payload["status"] = stage_payload["status"].upper()
            return

        if stage_payload.get("completed") is True:
            stage_payload["status"] = "SUCCEEDED"
            return

        if stage_payload.get("entered") is True:
            stage_payload["status"] = "IN_PROGRESS"
            return

        stage_payload["status"] = "NOT_STARTED"

    def _redact_user_message(self, message: str) -> str:
        sanitized = _EMAIL_RE.sub("[REDACTED_EMAIL]", message)
        sanitized = _PHONE_RE.sub("[REDACTED_PHONE]", sanitized)
        sanitized = _LABELLED_NAME_RE.sub(r"\1 [REDACTED_NAME]", sanitized)
        sanitized = re.sub(r"(\[REDACTED_NAME\])(?=\[REDACTED_EMAIL\])", r"\1 and my email is ", sanitized)
        sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()
        return sanitized


class AIRuntimeTraceRegistry:
    _sessions: dict[str, AIRuntimeTraceSession] = {}
    _lock = Lock()

    @classmethod
    def register(cls, session: AIRuntimeTraceSession) -> None:
        if not session.enabled:
            return
        with cls._lock:
            cls._sessions[session.trace_id] = session

    @classmethod
    def unregister(cls, trace_id: str | None) -> None:
        if not trace_id:
            return
        with cls._lock:
            cls._sessions.pop(trace_id, None)

    @classmethod
    def get(cls, trace_id: str | None) -> AIRuntimeTraceSession | None:
        if not trace_id:
            return None
        with cls._lock:
            return cls._sessions.get(trace_id)


def get_runtime_trace_from_metadata(metadata: dict[str, Any] | None) -> AIRuntimeTraceSession | None:
    if not isinstance(metadata, dict):
        return None
    return AIRuntimeTraceRegistry.get(metadata.get("ai_runtime_trace_id"))
