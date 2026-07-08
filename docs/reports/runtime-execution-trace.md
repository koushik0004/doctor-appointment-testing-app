# Runtime Execution Trace

## Purpose

This report captures the routing change that makes controlled generation reachable from the live chat path and the follow-up instrumentation that guarantees a structured diagnostic when controlled generation does not succeed.

It is both an implementation report and a runtime trace summary for the same request class:

`"My wife has been suffering from migraine for 3 weeks. Which specialist should we consult first?"`

## Files Modified

- `backend/app/llm/runtime_trace.py`
- `backend/app/llm/facade.py`
- `backend/app/services/conversation_manager.py`
- `backend/tests/test_llm_facade.py`
- `backend/tests/test_conversation_manager.py`

## What Changed

Before this change, `ConversationManager` always finished the visible response and then attempted hidden shadow execution. That shadow path stopped early in `LLMRuntimeFacade.run_shadow_mode()` whenever `should_execute_shadow` was false, so Prompt Builder, Orchestrator, Provider Registry, Claude Adapter, Claude Transport, Validator, Eligibility, Composer, and Post Processor were never reached.

After this change, `ConversationManager` routes eligible low-risk chat requests into `LLMRuntimeFacade.run_controlled_generation()` instead of shadow mode. Workflow-owned requests still stay deterministic, doctor search and availability remain deterministic, and active workflows still block LLM participation. The visible response is replaced only when controlled generation succeeds.

The follow-up diagnostics change keeps that routing intact and adds a final controlled-generation summary to the runtime trace whenever the facade returns `SKIPPED` or `FAILED`. The new summary is additive and does not change chat behavior, fallback behavior, or response shapes.

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

## Stabilization Summary

- Issue: non-success controlled-generation runs could finish without a single final diagnostic record that explained where execution stopped.
- Root Cause: the facade already tracked stage progress, but the end-of-call summary was only implicit and some skip/failure branches returned before a structured diagnostic was emitted.
- Implementation: added `AIRuntimeTraceSession.snapshot()` and a final controlled-generation diagnostic emitter in `LLMRuntimeFacade.run_controlled_generation()` so every `SKIPPED` or `FAILED` result logs the stage summary, fallback reason, and exception details before completion.
- Files Changed: `backend/app/llm/runtime_trace.py`, `backend/app/llm/facade.py`, `backend/tests/test_llm_facade.py`
- Backward Compatibility: routing and fallback behavior are unchanged; the new diagnostic is additive and only appears when `AI_RUNTIME_TRACE` is enabled.

## Manual Validation

Validated with targeted backend tests:

```bash
./backend/.venv/bin/python -m pytest backend/tests/test_conversation_manager.py backend/tests/test_llm_facade.py -q
```

Result:

- `21 passed`

Additional direct verification covered the two intended behavior classes:

- general low-risk text now reaches controlled generation
- workflow-owned requests stay deterministic and do not call the facade
- non-success controlled-generation runs now emit a final structured diagnostic before the trace is logged

## Practical Interpretation

- General AI questions such as `What is quantization?` and `What is diabetes?` can now reach Claude through the controlled-generation path.
- Knowledge-backed low-risk questions can combine Vector-less RAG and Claude guidance through the existing composer.
- Booking and other business-owned flows remain on deterministic APIs and do not lose ownership to the LLM path.
