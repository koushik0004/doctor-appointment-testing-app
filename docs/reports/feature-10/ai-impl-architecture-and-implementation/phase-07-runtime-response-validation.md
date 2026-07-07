# Phase 7.5 Runtime Response Validation

## Purpose

Add a provider-neutral runtime-response validation gate to the existing LLM runtime facade so controlled generation cannot become visible unless the canonical response is structurally valid.

The facade still owns the runtime boundary. Prompt creation still belongs only to `PromptBuilderService`. Execution policy still decides whether generation is allowed.

## What Changed

- Added `backend/app/llm/validation.py` with canonical validation request, issue, result, status, and validator models.
- Extended `backend/app/llm/facade.py` so controlled generation now passes through the validator before any generated runtime result is returned.
- Preserved deterministic fallback behavior when validation fails, without exposing validation exceptions or provider internals.
- Exported the new validation seam from `backend/app/llm/__init__.py` for direct runtime use and testing.

## Runtime Flow

1. Caller builds an `LLMControlledGenerationRequest` with an `AIExecutionPolicyRequest` and an `LLMGenerationOrchestrationRequest`.
2. `LLMRuntimeFacade` evaluates the existing execution policy through the composed runtime graph.
3. If the policy does not select an LLM-capable mode, the facade returns a skipped result and leaves deterministic behavior unchanged.
4. If the policy selects `LLM_ONLY` or `HYBRID`, the facade invokes the existing orchestrator.
5. The orchestrator calls `PromptBuilderService`, which assembles the canonical prompt and renders it through `PromptRenderer`.
6. The orchestrator delegates to `LLMIntegrationService`, and the provider path receives only the rendered prompt.
7. The facade passes the canonical orchestration result to the new runtime-response validator.
8. If validation succeeds, the validated runtime result is returned to the caller.
9. If validation fails, the facade returns a deterministic fallback result instead of surfacing the invalid response.

## Validation Rules

- Reject empty generated content.
- Reject whitespace-only generated content.
- Reject malformed structured output.
- Reject invalid finish reasons.
- Reject invalid canonical metadata.
- Reject missing required canonical response fields.

The validator does not:

- perform business validation
- inspect workflow state
- inspect Vector-less RAG retrieval
- inspect provider-native payloads
- inspect Prompt Builder internals

## Safety Guarantees

- No API contract changed.
- No database change was required.
- No frontend change was required.
- No workflow-engine change was required.
- No Vector-less RAG change was required.
- Validation failures do not surface provider errors or validation exceptions.
- Default production behavior stays deterministic unless a caller explicitly opts into an LLM-capable policy mode and runtime activation allows it.

## Validation

Commands run:

```bash
pytest backend/tests/test_llm_validation.py backend/tests/test_llm_facade.py backend/tests/test_llm_orchestrator.py backend/tests/test_llm_execution_policy.py backend/tests/test_llm_activation.py -q
pytest backend/tests/test_llm_*.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py backend/tests/test_prompt_builder_service.py -q
```

Observed result:

- `36 passed` in the focused validation, facade, orchestrator, policy, and activation suite
- `171 passed, 1 warning` in the broader backend regression suite
- Warning remains the existing FastAPI/Starlette `httpx` deprecation from the local test environment

## Modified Files

- `backend/app/llm/__init__.py`
- `backend/app/llm/facade.py`
- `backend/app/llm/validation.py`
- `backend/tests/test_llm_facade.py`
- `backend/tests/test_llm_validation.py`
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/report-index.md`
- `docs/ai-content/session-context.md`

## Architectural Decisions

- The runtime facade remains the single boundary for controlled generation and validation.
- Validation operates only on canonical orchestration models and never on provider-native payloads.
- Validation failures are contained inside the facade and fall back deterministically.
- Prompt Builder, Prompt Renderer, orchestrator, execution policy, runtime activation, and provider adapters remain unchanged.

## Architectural Result

The runtime now has a guarded generation path with a mandatory canonical quality gate:

`runtime inputs -> execution policy -> Prompt Builder -> PromptRenderer -> orchestrator -> provider request -> canonical response -> runtime-response validator`

That branch stays provider-neutral, deterministic by default, and safe on failure.
