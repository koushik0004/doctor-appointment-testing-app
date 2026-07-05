# Phase 7.4 Controlled Runtime Generation

## Purpose

Add a policy-gated visible-generation branch to the existing LLM runtime facade without changing the default deterministic chat path.

The facade still owns the runtime boundary. Prompt creation still belongs only to `PromptBuilderService`. Execution policy still decides whether generation is allowed.

## What Changed

- Extended `backend/app/llm/facade.py` with a controlled-generation request/result pair and a `run_controlled_generation()` branch.
- Reused the existing execution-policy service to decide whether the caller is allowed to run an LLM-capable mode.
- Reused the existing Prompt Builder and `LLMGenerationOrchestrator` pipeline for the generated path.
- Preserved the existing deterministic fallback path when generation is not allowed or when generation fails.
- Exported the new facade models from `backend/app/llm/__init__.py` for direct runtime use and testing.

## Runtime Flow

1. Caller builds an `LLMControlledGenerationRequest` with an `AIExecutionPolicyRequest` and an `LLMGenerationOrchestrationRequest`.
2. `LLMRuntimeFacade` evaluates the existing execution policy through the composed runtime graph.
3. If the policy does not select an LLM-capable mode, the facade returns a skipped result and leaves deterministic behavior unchanged.
4. If the policy selects `LLM_ONLY` or `HYBRID`, the facade invokes the existing orchestrator.
5. The orchestrator calls `PromptBuilderService`, which assembles the canonical prompt and renders it through `PromptRenderer`.
6. The orchestrator delegates to `LLMIntegrationService`, and the provider path receives only the rendered prompt.
7. The facade returns the generated runtime result to the caller.
8. If any generation step fails, the facade catches the error and returns a safe fallback result instead of raising.

## Safety Guarantees

- No API contract changed.
- No database change was required.
- No frontend change was required.
- No workflow-engine change was required.
- No Vector-less RAG change was required.
- Shadow mode continues to work through the existing branch.
- Default production behavior stays deterministic unless a caller explicitly opts into an LLM-capable policy mode and runtime activation allows it.

## Validation

Commands run:

```bash
pytest backend/tests/test_llm_facade.py backend/tests/test_llm_orchestrator.py backend/tests/test_llm_execution_policy.py backend/tests/test_llm_activation.py -q
pytest backend/tests/test_llm_*.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py backend/tests/test_prompt_builder_service.py -q
```

Observed result:

- `29 passed` in the focused facade, orchestrator, policy, and activation suite
- `164 passed, 1 warning` in the broader backend regression suite
- Warning remains the existing FastAPI/Starlette `httpx` deprecation from the local test environment

## Modified Files

- `backend/app/llm/facade.py`
- `backend/app/llm/__init__.py`
- `backend/tests/test_llm_facade.py`
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/session-context.md`
- `docs/ai-content/report-index.md`

## Architectural Decisions

- The facade remains the single runtime boundary for Phase 7 LLM work.
- Controlled generation is opt-in through existing activation and execution-policy state.
- The generated path reuses the existing orchestrator rather than duplicating prompt assembly or provider delegation.
- Generation failures are contained inside the facade and do not alter the deterministic fallback path.

## Architectural Result

The runtime now has a controlled generation branch that sits beside shadow execution:

`runtime inputs -> execution policy -> Prompt Builder -> PromptRenderer -> orchestrator -> provider request`

That branch stays guarded, deterministic by default, and safe on failure.
