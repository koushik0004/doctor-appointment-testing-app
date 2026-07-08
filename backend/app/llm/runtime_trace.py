from __future__ import annotations

import json
import logging
import re
from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
_LABELLED_NAME_RE = re.compile(
    r"\b(full name|patient name|my name is|name is|i am)\b\s*[:\-]?\s*([A-Za-z][A-Za-z\s'.-]{1,60})",
    re.IGNORECASE,
)


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
        self._payload: dict[str, Any] = {
            "trace_name": "AI Runtime Trace",
            "request_id": request_id or str(uuid4()),
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": None,
            "conversation_manager": {},
            "workflow_engine": {},
            "vectorless_rag": {},
            "execution_policy": {},
            "runtime_facade": {},
            "prompt_builder": {},
            "llm_integration": {},
            "provider_adapter": {},
            "provider_transport": {},
            "runtime_validator": {},
            "eligibility": {},
            "composer": {},
            "post_processor": {},
            "final_response": {},
            "llm_not_invoked": False,
            "stop_component": None,
            "stop_reason": None,
        }

    def attach_user_message(self, message: str) -> None:
        if not self.enabled:
            return
        self.set_root("user_message", self._redact_user_message(message))

    def set_root(self, key: str, value: Any) -> None:
        if not self.enabled:
            return
        with self._lock:
            self._payload[key] = deepcopy(value)

    def update_stage(self, stage: str, values: dict[str, Any]) -> None:
        if not self.enabled:
            return
        with self._lock:
            current = self._payload.setdefault(stage, {})
            if isinstance(current, dict):
                current.update(deepcopy(values))
            else:
                self._payload[stage] = deepcopy(values)

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
            payload = deepcopy(self._payload)
            self._emitted = True
        logger.info("ai_runtime_trace %s", json.dumps(payload, sort_keys=True, default=str))

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
