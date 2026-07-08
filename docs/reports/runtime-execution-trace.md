# Runtime Execution Trace

## Purpose

This report captures the routing change that makes controlled generation reachable from the live chat path.

It is both an implementation report and a runtime trace summary for the same request class:

`"My wife has been suffering from migraine for 3 weeks. Which specialist should we consult first?"`

## Files Modified

- `backend/app/llm/facade.py`
- `backend/app/services/conversation_manager.py`
- `backend/tests/test_llm_facade.py`
- `backend/tests/test_conversation_manager.py`

## What Changed

Before this change, `ConversationManager` always finished the visible response and then attempted hidden shadow execution. That shadow path stopped early in `LLMRuntimeFacade.run_shadow_mode()` whenever `should_execute_shadow` was false, so Prompt Builder, Orchestrator, Provider Registry, Claude Adapter, Claude Transport, Validator, Eligibility, Composer, and Post Processor were never reached.

After this change, `ConversationManager` routes eligible low-risk chat requests into `LLMRuntimeFacade.run_controlled_generation()` instead of shadow mode. Workflow-owned requests still stay deterministic, doctor search and availability remain deterministic, and active workflows still block LLM participation. The visible response is replaced only when controlled generation succeeds.

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

The visible trace still emits `llm_not_invoked` when the facade is missing, policy blocks the request, or controlled generation fails safely before provider execution.

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

## Practical Interpretation

- General AI questions such as `What is quantization?` and `What is diabetes?` can now reach Claude through the controlled-generation path.
- Knowledge-backed low-risk questions can combine Vector-less RAG and Claude guidance through the existing composer.
- Booking and other business-owned flows remain on deterministic APIs and do not lose ownership to the LLM path.
