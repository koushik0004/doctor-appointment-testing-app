# Phase 7.6 Controlled User-visible LLM Responses

## Purpose

Add a provider-neutral user-visibility gate to the existing runtime facade so validated LLM responses are exposed only for explicitly approved low-risk conversational scenarios.

The facade still owns the final runtime boundary. Prompt creation still belongs to `PromptBuilderService`. Execution policy still decides whether generation is allowed. This phase adds a second, deterministic gate that decides whether a validated response may be shown to the user.

## What Changed

- Added `backend/app/llm/eligibility.py` with a provider-neutral runtime-response eligibility evaluator, request/result models, and deterministic diagnostics.
- Extended `backend/app/llm/facade.py` so controlled generation now passes through validation and then eligibility before any visible LLM output can be returned.
- Preserved deterministic fallback for workflow-owned and other non-approved scenarios by returning a skipped controlled-generation result instead of exposing the generated response.
- Exported the new eligibility contracts from `backend/app/llm/__init__.py` for direct runtime use and testing.
- Added focused backend tests covering eligible conversational responses, booking and cancellation rejection, invalid-validation interaction, deterministic fallback, and serialization determinism.

## Runtime Flow

1. Caller builds an `LLMControlledGenerationRequest` with an `AIExecutionPolicyRequest` and an `LLMGenerationOrchestrationRequest`.
2. `LLMRuntimeFacade` evaluates the existing execution policy through the composed runtime graph.
3. If the policy does not select an LLM-capable mode, the facade returns a skipped result and leaves deterministic behavior unchanged.
4. If the policy selects `LLM_ONLY` or `HYBRID`, the facade invokes the existing orchestrator.
5. The orchestrator calls `PromptBuilderService`, which assembles the canonical prompt and renders it through `PromptRenderer`.
6. The orchestrator delegates to `LLMIntegrationService`, and the provider path receives only the rendered prompt.
7. The facade validates the canonical orchestration result.
8. If validation passes, the facade evaluates runtime-response eligibility against canonical execution-policy and orchestration metadata.
9. If eligibility passes, the facade returns the generated runtime result.
10. If eligibility fails, the facade preserves deterministic behavior and does not expose the generated LLM response.

## Safety Guarantees

- No API contract changed.
- No database change was required.
- No frontend change was required.
- No workflow-engine change was required.
- No Vector-less RAG change was required.
- Validation still blocks malformed or invalid canonical output before eligibility runs.
- Eligibility still blocks workflow-owned or other non-approved requests after validation.
- Provider errors, validation errors, and eligibility details remain internal to the backend facade.

## Validation

Commands run:

```bash
pytest backend/tests/test_llm_eligibility.py backend/tests/test_llm_facade.py backend/tests/test_llm_validation.py backend/tests/test_llm_execution_policy.py backend/tests/test_llm_activation.py -q
pytest backend/tests/test_llm_*.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py backend/tests/test_prompt_builder_service.py -q
```

Observed result:

- `38 passed` in the focused LLM eligibility, facade, validation, policy, and activation suite
- `177 passed, 1 warning` in the broader backend regression suite
- Warning remains the existing FastAPI/Starlette `httpx` deprecation from the local test environment

## Modified Files

- `backend/app/llm/eligibility.py`
- `backend/app/llm/facade.py`
- `backend/app/llm/__init__.py`
- `backend/tests/test_llm_eligibility.py`
- `backend/tests/test_llm_facade.py`
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/report-index.md`
- `docs/ai-content/session-context.md`

## Architectural Decisions

- The facade remains the single runtime boundary for Phase 7 LLM work.
- Validation remains a hard prerequisite before eligibility evaluation.
- Eligibility is intentionally conservative and only approves a narrow low-risk allowlist.
- The generated path reuses the existing orchestrator rather than duplicating prompt assembly or provider delegation.
- Deterministic fallback stays the default for workflow-owned and non-approved scenarios.

## Architectural Result

The runtime now has a second guard beside validation that controls user-visible exposure:

`runtime inputs -> execution policy -> Prompt Builder -> PromptRenderer -> orchestrator -> provider request -> validation -> eligibility -> visible LLM reply or deterministic fallback`

That branch stays guarded, deterministic by default, and safe on failure.
