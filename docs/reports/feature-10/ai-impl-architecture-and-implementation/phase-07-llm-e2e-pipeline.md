# Phase 7.3 LLM End-to-End Prompt Pipeline

## Purpose

Complete the hidden shadow-mode prompt path so every LLM execution uses the existing Prompt Builder pipeline end to end.

The deterministic assistant remains the only user-visible response path.

## What Changed

- Kept `ConversationManager`, workflow routing, Vector-less RAG retrieval, API contracts, and frontend behavior unchanged.
- Preserved `LLMRuntimeFacade` as the runtime boundary and `LLMGenerationOrchestrator` as the only path into provider execution.
- Extended `backend/app/services/prompt_builder.py` so rendered prompts now include canonical workflow context in addition to user, conversation, and knowledge sections.
- Left prompt creation ownership entirely inside `PromptBuilderService` and `PromptRenderer`; no manual prompt concatenation was added anywhere in the runtime facade or orchestrator path.

## Runtime Flow

1. `ConversationManager` finalizes the official deterministic, knowledge, or workflow response.
2. `LLMRuntimeFacade` evaluates existing shadow execution policy.
3. If shadow execution is allowed, the facade builds an `LLMGenerationOrchestrationRequest`.
4. `LLMGenerationOrchestrator` calls `PromptBuilderService`.
5. `PromptBuilderService` runs Conversation, Workflow, and Knowledge collectors, creates canonical `PromptContext`, validates it, assembles ordered sections, and delegates final rendering to `PromptRenderer`.
6. The orchestrator passes only the rendered prompt into the canonical `LLMGenerationRequest`.
7. The provider adapter executes through the existing registry and transport path.
8. The facade records diagnostics and discards the LLM response.

## Gap Closed

Before this phase, the shadow path already used `PromptBuilderService`, but the rendered prompt omitted workflow context even when the canonical collector populated it.

Phase 7.3 closes that gap by rendering a `Workflow State` section into the final prompt and exposing it through prompt blocks for deterministic inspection.

## Safety Guarantees

- No change to visible chat responses.
- No change to workflow ownership or workflow execution.
- No change to knowledge retrieval behavior.
- No change to request or response schemas.
- No database migration.
- No provider-specific prompt logic introduced upstream of adapters.

## Validation

Commands run:

```bash
pytest backend/tests/test_prompt_builder_service.py backend/tests/test_llm_facade.py -q
pytest backend/tests/test_llm_*.py backend/tests/test_prompt_builder_service.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py -q
```

Observed result:

- `45 passed` in the focused prompt-builder and facade suite
- `160 passed, 1 warning` in the broader backend regression suite
- Warning remains the existing FastAPI/Starlette `httpx` deprecation from the local test environment

## Modified Files

- `backend/app/services/prompt_builder.py`
- `backend/tests/test_prompt_builder_service.py`
- `backend/tests/test_llm_facade.py`
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/session-context.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/report-index.md`

## Architectural Result

Prompt creation is now consistently owned by the Prompt Builder pipeline for hidden runtime LLM execution:

`runtime inputs -> PromptContext collectors -> PromptContext -> assembly -> PromptRenderer -> orchestrator -> provider request`

That path remains shadow-only and diagnostics-only.
