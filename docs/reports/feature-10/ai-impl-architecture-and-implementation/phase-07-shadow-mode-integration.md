# Phase 7.2 Shadow Mode Integration

## Summary

Phase 7.2 wires the existing LLM runtime facade into the live chat orchestration path in a way that preserves all current user-visible behavior.
The deterministic assistant, workflow engine, and Vector-less RAG responses remain the only responses returned to the frontend.
When the existing runtime activation and execution policy allow `SHADOW` mode, the facade now executes the composed Prompt Builder and LLM generation pipeline in the background for diagnostics only.
All generated LLM output is discarded after observability, audit, and token-usage metadata are captured.
Any shadow-mode failure is contained and never changes booking, cancellation, confirmation, FAQ, or fallback behavior.

## Purpose

- Validate the composed LLM runtime path without exposing model output to end users.
- Reuse the existing runtime-activation, execution-policy, composition, prompt-builder, provider-registry, and orchestrator seams rather than introducing a second AI runtime.
- Establish a provider-neutral diagnostics trail for future rollout decisions while keeping the current deterministic assistant as the production truth.

## Runtime Sequence

1. `ConversationManager` resolves the normal response exactly as before through workflow, knowledge, or deterministic ownership.
2. The normal `ChatResponse` is finalized with the existing conversation context and returned unchanged to the caller.
3. `ConversationManager` sends a read-only shadow request to `LLMRuntimeFacade`.
4. The facade evaluates the existing `AIExecutionPolicyService` using `preferred_mode=SHADOW`.
5. If shadow mode is unavailable, the facade records a skipped diagnostic and exits.
6. If shadow mode is available, the facade schedules background execution through the composed `LLMGenerationOrchestrator`.
7. The orchestrator invokes the existing `PromptBuilderService`, routes generation through the existing provider registry and integration service, and returns a normalized provider-neutral result.
8. The facade captures diagnostics and discards the generated assistant content.

## Safety Guarantees

- No frontend API contract changed.
- No workflow ownership rule changed.
- No Vector-less RAG ownership rule changed.
- No business API was bypassed.
- No LLM output is returned to the frontend.
- Shadow failures are swallowed after diagnostics are captured.
- The visible chatbot response remains the same response the deterministic stack already chose.

## Diagnostics Captured

- Request ID
- Correlation ID
- Execution ID
- Execution status: `SKIPPED`, `SUCCEEDED`, or `FAILED`
- Execution-policy decision
- Provider name
- Model name
- End-to-end shadow duration
- Provider-latency placeholder based on the same wall-clock duration
- Token usage when the provider returns usage metadata
- Error type and error message when shadow execution fails
- Audit timestamps

## Rollback Strategy

- Set the existing runtime flags so shadow mode is not selected.
- Remove the optional facade injection from `ConversationManager` if a code rollback is required.
- Since no user-visible API or schema changed, rollback is isolated to backend orchestration only.

## Modified Files

- `backend/app/llm/facade.py`
- `backend/app/llm/__init__.py`
- `backend/app/services/conversation_manager.py`
- `backend/app/services/chat_service.py`
- `backend/tests/test_llm_facade.py`
- `backend/tests/test_conversation_manager.py`
- `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/session-context.md`
- `docs/ai-content/report-index.md`

## Architectural Decisions

- The facade remains the single runtime boundary for Phase 7 LLM work.
- Shadow execution is best-effort and backgrounded through a runner instead of blocking the live chat response.
- Diagnostics reuse the existing operational models (`LLMObservabilityRecord`, `LLMTraceContext`, `LLMTimingBreakdown`, `LLMTokenAccounting`, `LLMAuditTrailRecord`) to avoid a parallel telemetry shape.
- `ConversationManager` owns only the trigger point and request shaping; the facade owns execution-policy evaluation, orchestration, and diagnostic persistence.

## Validation

- `pytest backend/tests/test_llm_facade.py backend/tests/test_conversation_manager.py -q`
  - `11 passed`
- `pytest backend/tests/test_llm_*.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py -q`
  - `120 passed`

## User-Visible Impact

There is no intended user-visible behavior change in this phase.
The live chatbot still returns the same deterministic, workflow, and knowledge-backed responses it returned before this implementation.
