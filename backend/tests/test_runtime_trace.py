from __future__ import annotations

import json
import logging

from app.llm import runtime_trace as runtime_trace_module
from app.llm.runtime_trace import AIRuntimeTraceSession


def test_runtime_trace_emit_creates_dedicated_log_file_and_writes_one_json_object(runtime_trace_log):
    session = AIRuntimeTraceSession(
        enabled=True,
        request_id="req-runtime-trace",
        conversation_id="conv-runtime-trace",
    )
    session.attach_user_message("Hello")
    session.update_stage(
        "final_response",
        {
            "response_source": "deterministic_engine",
        },
    )

    session.emit()
    session.emit()

    assert runtime_trace_log.parent.exists()
    assert runtime_trace_log.exists()

    lines = runtime_trace_log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    trace_logger = logging.getLogger(runtime_trace_module._TRACE_LOGGER_NAME)

    assert trace_logger.name == "ai.runtime.trace"
    assert trace_logger.propagate is False
    assert payload["request_id"] == "req-runtime-trace"
    assert payload["conversation_id"] == "conv-runtime-trace"
    assert payload["user_message"] == "Hello"
    assert payload["final_response"]["status"] == "SUCCEEDED"
    assert payload["latency_ms"] is not None


def test_runtime_trace_preserves_failed_stage_details(runtime_trace_log):
    session = AIRuntimeTraceSession(enabled=True)
    session.update_stage(
        "provider_transport",
        {
            "transport_selected": "ClaudeTransport",
            "http_request_started": True,
        },
    )
    session.record_exception("provider_transport", RuntimeError("transport failure"))
    session.update_stage(
        "provider_transport",
        {
            "http_response_received": False,
            "duration_ms": 12.5,
        },
    )
    session.mark_llm_not_invoked("provider_transport", "transport failure")

    session.emit()

    payload = json.loads(runtime_trace_log.read_text(encoding="utf-8").splitlines()[0])
    assert payload["stop_component"] == "provider_transport"
    assert payload["stop_reason"] == "transport failure"
    assert payload["provider_transport"]["status"] == "FAILED"
    assert payload["provider_transport"]["duration_ms"] == 12.5
    assert payload["exception_component"] == "provider_transport"
    assert payload["exception_type"] == "RuntimeError"
