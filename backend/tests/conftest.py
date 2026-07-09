from __future__ import annotations

import logging
from pathlib import Path

import pytest

from app.llm import runtime_trace as runtime_trace_module


@pytest.fixture
def runtime_trace_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    trace_log_path = tmp_path / "logs" / "ai-runtime-trace.log"
    monkeypatch.setattr(runtime_trace_module, "_TRACE_LOG_PATH", trace_log_path)

    trace_logger = logging.getLogger(runtime_trace_module._TRACE_LOGGER_NAME)
    for handler in list(trace_logger.handlers):
        trace_logger.removeHandler(handler)
        handler.close()

    yield trace_log_path

    for handler in list(trace_logger.handlers):
        trace_logger.removeHandler(handler)
        handler.close()
