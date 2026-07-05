# Phase 07.7 - Hybrid Response Strategy

## Purpose

Phase 7.7 adds a provider-neutral runtime response composer under `backend/app/llm/composer.py` and wires it through `backend/app/llm/facade.py`.

The goal is to support three final-response modes without changing the existing conversation manager, workflow engine, prompt builder, prompt renderer, provider adapters, or business APIs:

- deterministic only
- LLM only
- hybrid deterministic plus optional LLM augmentation

## Runtime Flow

Execution Policy

↓

Prompt Builder

↓

Prompt Renderer

↓

LLMGenerationOrchestrator

↓

Provider

↓

Runtime Validator

↓

Runtime Eligibility

↓

Runtime Response Composer

↓

Final Runtime Response

## What Changed

- Added `backend/app/llm/composer.py` with canonical response-envelope models, composition diagnostics, and a deterministic composer that supports deterministic-only, LLM-only, and hybrid modes.
- Extended `backend/app/llm/facade.py` so controlled generation can now emit a composed final response after validation and eligibility while preserving deterministic fallback paths.
- Added an optional deterministic response envelope to `LLMControlledGenerationRequest` so the facade can preserve business truth when composing hybrid responses.
- Extended `LLMControlledGenerationResult` with `final_response` and `composition_result` so callers can inspect the composed runtime response without losing the existing orchestration, validation, and eligibility diagnostics.
- Added focused backend tests covering deterministic-only composition, LLM-only composition, hybrid composition, business-field preservation, augmentation placement, validation compatibility, eligibility compatibility, deterministic fallback, and serialization determinism.

## Safety Guarantees

- Deterministic business fields are preserved by deep-copying the deterministic response payload during composition.
- Hybrid composition appends LLM guidance without replacing the deterministic business response.
- The composer uses only canonical orchestration, validation, and eligibility metadata.
- Invalid validation or eligibility never enables LLM augmentation.
- The facade continues to fall back safely without exposing provider internals.

## Validation

Commands run:

```bash
pytest backend/tests/test_llm_composer.py backend/tests/test_llm_facade.py backend/tests/test_llm_validation.py backend/tests/test_llm_eligibility.py backend/tests/test_llm_execution_policy.py -q
pytest backend/tests/test_llm_*.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py backend/tests/test_prompt_builder_service.py -q
```

Results:

- `38 passed`
- `183 passed, 1 warning`

The warning is the existing FastAPI/Starlette `httpx` deprecation warning in the local test environment.

## Modified Files

- `backend/app/llm/composer.py`
- `backend/app/llm/facade.py`
- `backend/app/llm/__init__.py`
- `backend/tests/test_llm_composer.py`
- `backend/tests/test_llm_facade.py`
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/report-index.md`
- `docs/ai-content/session-context.md`

## Result

The runtime facade now has a provider-neutral final-response composition layer that keeps deterministic business truth intact and only appends validated, eligible LLM guidance when the runtime mode supports it.

