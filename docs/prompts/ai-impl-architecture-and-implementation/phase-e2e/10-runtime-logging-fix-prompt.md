Doctor Appointment AI Assistant

This is NOT a new feature.

This is NOT an architecture redesign.

This is a production debugging task.

The application architecture is complete.

Do NOT redesign or refactor existing architecture.

Do NOT modify business logic.

Do NOT modify routing.

Do NOT modify Vector-less RAG.

Do NOT modify Prompt Builder.

Do NOT modify ConversationManager logic except where required for guaranteed trace emission.

The only objective is to make runtime tracing production-grade and deterministic.

=========================================================
BACKGROUND
=========================================================

The runtime already contains:

- AIRuntimeTraceSession
- runtime_trace.update_stage(...)
- runtime_trace.mark_llm_not_invoked(...)
- Runtime Facade
- Prompt Builder
- LLM Integration
- Provider Adapter
- Claude Transport

Transport tracing is already implemented.

Console proves transport execution because every request logs

    llm_transport_failure

Therefore execution definitely reaches ClaudeTransport.

The problem is observability.

Current implementation of AIRuntimeTraceSession.emit() only performs

    logger.info(...)

No dedicated logger exists.

No FileHandler exists.

No RotatingFileHandler exists.

No runtime trace file is ever created.

There is no guarantee emit() is executed on every exit path.

=========================================================
OBJECTIVE
=========================================================

Implement a production-grade runtime tracing system.

This is NOT application logging.

This is dedicated runtime execution tracing.

The implementation must allow us to determine the exact component where execution stopped.

=========================================================
REQUIREMENTS
=========================================================

1.

Create a completely independent runtime trace logger.

DO NOT depend on the root logger.

DO NOT depend on uvicorn logging.

DO NOT depend on logger.info() reaching a configured FileHandler.

Configure a dedicated logger inside runtime_trace.py.

Requirements:

- logger name = "ai.runtime.trace"
- propagate = False
- level = INFO
- RotatingFileHandler
- automatically create logs/
- automatically create

    logs/ai-runtime-trace.log

- UTF-8 encoding
- maxBytes
- backupCount

Configure this logger exactly once.

Avoid duplicate handlers.

=========================================================

2.

AIRuntimeTraceSession.emit()

must

- always serialize JSON
- write one JSON object per request
- flush immediately
- never silently fail

If writing fails

log the exception using the application logger.

=========================================================

3.

ConversationManager

must guarantee

runtime_trace.emit()

is executed exactly once.

Use

finally

Do NOT emit from multiple places.

Every request

successful

fallback

exception

must emit exactly one trace.

=========================================================

4.

Every runtime stage must record

entered

completed

duration_ms

status

=========================================================

Stages

conversation_manager

workflow_engine

vectorless_rag

execution_policy

runtime_facade

prompt_builder

llm_integration

provider_adapter

provider_transport

runtime_validator

eligibility

composer

post_processor

final_response

=========================================================

5.

If execution stops

record

stop_component

stop_reason

llm_not_invoked

=========================================================

6.

If any exception occurs

record

exception type

exception message

stack trace

component

before fallback occurs.

=========================================================

7.

Provider transport tracing already exists.

Do NOT duplicate transport instrumentation.

Only connect existing transport updates into the runtime trace.

=========================================================

8.

At the end of every request include

trace_id

conversation_id

request_id

user_message

intent

selected_provider

execution_mode

generation_available

provider_health

final_response_source

final_response_preview

latency_ms

stop_component

stop_reason

=========================================================

9.

After implementation verify the following scenario.

User sends

    Hello

Expected

- logs directory created automatically
- ai-runtime-trace.log created automatically
- exactly one JSON trace written

User sends

    My wife has been suffering from migraine for 3 weeks.
    Which specialist should we consult first?

Expected

- Prompt Builder recorded
- LLM Integration recorded
- Provider Adapter recorded
- Claude Transport recorded
- If transport fails

stop_component

must equal

provider_transport

instead of silently falling back.

=========================================================

10.

Do NOT redesign architecture.

Do NOT change dependency injection.

Do NOT change providers.

Do NOT change activation.

Do NOT change routing.

Only improve runtime observability.

=========================================================

DELIVERABLE

Generate production-ready code modifications only.

Modify the minimum number of files required.

Maintain backward compatibility.

The implementation should be suitable for long-term production debugging.