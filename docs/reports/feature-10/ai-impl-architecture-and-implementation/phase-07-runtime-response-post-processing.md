# Phase 7.8 Runtime Response Post Processing

## Purpose

Phase 7.8 adds a provider-neutral runtime response post processor under `backend/app/llm/post_processor.py` and wires it through `backend/app/llm/facade.py`.

The goal is to normalize presentation right before a runtime response becomes visible while preserving deterministic business truth, runtime diagnostics, and the existing composer ownership model.

## Runtime Flow

Execution Policy

↓

Prompt Builder

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

Runtime Response Post Processor

↓

Final Runtime Response

## What Changed

- Added `backend/app/llm/post_processor.py` with canonical post-processing request/result models, presentation-only diagnostics, and a deterministic processor for final runtime response envelopes.
- Extended `backend/app/llm/facade.py` so controlled generation now passes composed responses through the post processor before returning them to callers.
- Preserved deterministic business data by deep-copying the response payload and leaving booking IDs, appointment IDs, doctor names, consultation fees, workflow state, validation state, and eligibility state untouched.
- Sanitized presentation-only metadata into separate post-processing diagnostics while keeping runtime composition metadata and other deterministic metadata intact.
- Added focused backend tests covering whitespace normalization, duplicate newline removal, markdown normalization, metadata sanitization, business-data preservation, deterministic-only compatibility, LLM-only compatibility, hybrid compatibility, and serialization determinism.

## Normalization Rules

- Trim leading and trailing whitespace.
- Normalize CRLF and CR line breaks to LF.
- Collapse duplicate blank lines.
- Normalize supported markdown presentation patterns such as headings, lists, and blockquotes.
- Remove presentation-only metadata keys from the visible response envelope and preserve them in post-processing diagnostics.

## Safety Guarantees

- Deterministic business data is preserved without mutation.
- Validation and eligibility results remain unchanged.
- Composition results remain unchanged.
- Workflow ownership remains outside the LLM layer.
- The facade continues to own the runtime boundary.

## Validation

Commands run:

```bash
pytest backend/tests/test_llm_post_processor.py backend/tests/test_llm_facade.py backend/tests/test_llm_composer.py -q
pytest backend/tests/test_llm_*.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py backend/tests/test_prompt_builder_service.py -q
```

Results:

- `26 passed` in the focused post-processor, facade, and composer suite
- `191 passed, 1 warning` in the broader backend regression suite
- The warning is the existing FastAPI/Starlette `httpx` deprecation warning in the local test environment

## Modified Files

- `backend/app/llm/post_processor.py`
- `backend/app/llm/facade.py`
- `backend/app/llm/__init__.py`
- `backend/tests/test_llm_post_processor.py`
- `backend/tests/test_llm_facade.py`
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/report-index.md`
- `docs/ai-content/session-context.md`

## Result

The runtime facade now includes a final presentation-only post-processing stage that normalizes visible text and sanitizes presentation metadata without changing business truth or upstream runtime decisions.
