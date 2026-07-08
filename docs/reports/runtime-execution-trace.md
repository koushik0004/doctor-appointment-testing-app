# Runtime Execution Trace

## Purpose

This report captures the routing change that makes controlled generation reachable from the live chat path and the follow-up observability work that guarantees a durable structured trace when controlled generation does not succeed.

It is both an implementation report and a runtime trace summary for the same request class:

`"My wife has been suffering from migraine for 3 weeks. Which specialist should we consult first?"`

## Files Modified

- `backend/app/llm/runtime_trace.py`
- `backend/app/llm/facade.py`
- `backend/app/llm/service.py`
- `backend/app/llm/orchestrator.py`
- `backend/app/llm/adapters.py`
- `backend/app/llm/transport.py`
- `backend/app/services/conversation_manager.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/knowledge/retrieval.py`
- `backend/tests/test_llm_facade.py`
- `backend/tests/test_conversation_manager.py`
- `backend/tests/test_llm_orchestrator.py`
- `backend/tests/test_llm_transport.py`

## What Changed

Before this change, `ConversationManager` always finished the visible response and then attempted hidden shadow execution. That shadow path stopped early in `LLMRuntimeFacade.run_shadow_mode()` whenever `should_execute_shadow` was false, so Prompt Builder, Orchestrator, Provider Registry, Claude Adapter, Claude Transport, Validator, Eligibility, Composer, and Post Processor were never reached.

After this change, `ConversationManager` routes eligible low-risk chat requests into `LLMRuntimeFacade.run_controlled_generation()` instead of shadow mode. Workflow-owned requests still stay deterministic, doctor search and availability remain deterministic, and active workflows still block LLM participation. The visible response is replaced only when controlled generation succeeds.

The follow-up observability change keeps that routing intact and adds a final controlled-generation summary to the runtime trace whenever the facade returns `SKIPPED` or `FAILED`, while also wiring the broader request path into a single rotating JSON trace file. The new summary is additive and does not change chat behavior, fallback behavior, or response shapes.

## Routing Changes

- Workflow requests still win first.
- Active workflows still block controlled generation.
- Booking, cancellation, confirmation, doctor search, availability lookup, and doctor-detail routes remain deterministic.
- Low-risk conversational requests now enter controlled generation when the intent is `UNKNOWN`, `APPOINTMENT_HELP`, or `CANCEL_APPOINTMENT_HELP`.
- Knowledge-backed low-risk requests use `HYBRID` mode so the deterministic knowledge document and Claude guidance can be composed together.
- Knowledge-free low-risk requests use `LLM_ONLY` mode.

## Before / After

| Area | Before | After |
|---|---|---|
| Visible chat owner | Deterministic or Vector-less RAG only | Deterministic, Vector-less RAG, or controlled generation |
| General AI questions | Fell back to deterministic text | Reach Prompt Builder, Claude, and post-processing |
| Knowledge-backed low-risk questions | Knowledge reply only | Hybrid controlled generation with knowledge context |
| Workflow requests | Deterministic workflow only | Deterministic workflow only |
| Shadow mode | Only diagnostic, and often skipped early | Still available as a facade capability, but no longer the live chat trigger |

## Why Controlled Generation Was Previously Unreachable

The controlled-generation pipeline already existed in `LLMRuntimeFacade.run_controlled_generation()`, but `ConversationManager.handle()` never called it. The chat path always invoked `_run_shadow_mode()`, which asked the execution policy for `SHADOW` mode and returned as soon as `should_execute_shadow` was false.

That meant the live request never reached:

- Prompt Builder
- LLM Orchestrator
- LLM Integration Service
- Provider Registry
- Claude Adapter
- Claude Transport
- Runtime Validator
- Runtime Eligibility
- Runtime Composer
- Runtime Post Processor

## How It Is Activated Now

`ConversationManager` now evaluates the request after the workflow and knowledge layers:

1. Workflow ownership still short-circuits the request.
2. If no workflow owns the request and the intent is low risk, the manager builds a controlled-generation request.
3. If a knowledge document was found, the request is sent in `HYBRID` mode with the document included in the orchestration input.
4. If no knowledge document exists, the request is sent in `LLM_ONLY` mode.
5. The facade then runs the existing validated path:
   - Prompt Builder
   - Orchestrator
   - Integration Service
   - Provider Adapter
   - Claude Transport
   - Runtime Validator
   - Runtime Eligibility
   - Runtime Composer
   - Runtime Post Processor

## Runtime Trace Coverage

The trace now records:

- `controlled_generation`
- `runtime_facade`
- `execution_policy`
- `prompt_builder`
- `llm_integration`
- `provider_adapter`
- `provider_transport`
- `runtime_validator`
- `eligibility`
- `composer`
- `post_processor`
- `final_response`

The visible trace now also records a final controlled-generation summary with:

- execution mode
- generation availability
- provider readiness
- selected provider
- orchestration started
- prompt builder executed
- provider adapter executed
- transport invoked
- HTTP request sent
- HTTP response received
- validation result
- eligibility result
- composition result
- post processor result
- stop stage
- fallback reason
- exception type
- exception message

The visible trace still emits `llm_not_invoked` when the facade is missing, policy blocks the request, or controlled generation fails safely before provider execution.

## Observability Layer

- `AIRuntimeTraceSession.emit()` now writes one raw JSON object per request to `logs/ai-runtime-trace.log` through a dedicated rotating file handler, and falls back to the application logger if the file write fails.
- `ConversationManager.handle()` now emits only inside its `finally` block so the trace includes final response ownership, preview, stop reason, and any recorded exception context.
- `WorkflowEngine`, Vector-less RAG retrieval, LLM integration, provider adapters, and provider transport now stamp enter/completed/duration fields, plus exception component/type/message/stack-trace records when a failure is converted into fallback or re-raised.
- The runtime trace payload now captures `trace_id`, `timestamp`, `conversation_id`, `request_id`, `intent`, `selected_provider`, `activation_status`, `stop_component`, `stop_reason`, `llm_not_invoked`, `final_response_source`, `final_response_preview`, and `latency_ms` in addition to the existing per-stage dictionaries.

## Stabilization Summary

- Issue: non-success controlled-generation runs could finish without a single final diagnostic record that explained where execution stopped.
- Root Cause: the facade already tracked stage progress, but the end-of-call summary was only implicit and some skip/failure branches returned before a structured diagnostic was emitted.
- Implementation: added a dedicated rotating runtime-trace logger, request-scoped exception recording, `AIRuntimeTraceSession.snapshot()`, and a final controlled-generation diagnostic summary so every `SKIPPED` or `FAILED` result logs the stage summary, fallback reason, and exception details before completion.
- Files Changed: `backend/app/llm/runtime_trace.py`, `backend/app/llm/facade.py`, `backend/app/llm/service.py`, `backend/app/llm/orchestrator.py`, `backend/app/llm/adapters.py`, `backend/app/llm/transport.py`, `backend/app/services/conversation_manager.py`, `backend/app/services/workflow_engine.py`, `backend/app/knowledge/retrieval.py`, `backend/tests/test_llm_facade.py`, `backend/tests/test_conversation_manager.py`, `backend/tests/test_llm_orchestrator.py`, `backend/tests/test_llm_transport.py`
- Backward Compatibility: routing and fallback behavior are unchanged; the new diagnostic and trace file are additive and only appear when `AI_RUNTIME_TRACE` is enabled.

## Manual Validation

Validated with targeted backend tests:

```bash
./backend/.venv/bin/python -m pytest backend/tests/test_llm_*.py backend/tests/test_conversation_manager.py backend/tests/test_knowledge_repository.py -q
```

Result:

- `133 passed, 1 skipped`

Additional direct verification covered the intended behavior classes:

- general low-risk text now reaches controlled generation
- workflow-owned requests stay deterministic and do not call the facade
- non-success controlled-generation runs now emit a final structured diagnostic before the trace is logged
- every request emits exactly one raw JSON trace in `logs/ai-runtime-trace.log`

## Practical Interpretation

- General AI questions such as `What is quantization?` and `What is diabetes?` can now reach Claude through the controlled-generation path.
- Knowledge-backed low-risk questions can combine Vector-less RAG and Claude guidance through the existing composer.
- Booking and other business-owned flows remain on deterministic APIs and do not lose ownership to the LLM path.
