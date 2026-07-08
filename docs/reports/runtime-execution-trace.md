# Runtime Execution Trace

## Request

`"My wife has been suffering from migraine for 3 weeks. Which specialist should we consult first?"`

## Execution Context Used

- Trace performed against the current repository code without modifying code.
- Direct service invocation confirmed the returned `ChatResponse`.
- Important environment note: `backend/app/llm/config.py` loads `.env` relative to process working directory (`backend/app/llm/config.py:228-235`). In the current repo-root execution context, the composed LLM activation status resolved to `llm_enabled=False`, `shadow_mode=False`, and `generation_available=False`.

## Final Outcome

- HTTP response is returned successfully.
- Visible response owner is Vector-less RAG knowledge fallback, not workflow or Claude.
- The request stops before Claude transport in `backend/app/llm/facade.py`, class `LLMRuntimeFacade`, method `run_shadow_mode`, line `263`, because execution policy returns `should_execute_shadow=False`.
- The policy reason comes from `backend/app/llm/execution_policy.py`, class `AIExecutionPolicyEvaluator`, method `evaluate`, lines `197-215`: shadow execution falls back because shadow mode or runtime generation availability is not enabled.

## Returned Response

Observed returned payload summary:

- `intent`: `UNKNOWN`
- `message`: knowledge fallback from `Appointment Preparation Guide`
- `knowledge_source.document_id`: `faq.preparation.general`
- `knowledge_source.matched_terms`: `["should"]`
- `conversation.routed_to`: `FUTURE_AI_LAYER`
- `workflow`: `null`

## Call Trace

| Component | Entered? | Exit Point | Returned Value | Continued? | Notes |
|---|---|---|---|---|---|
| Chat API endpoint | Yes | `backend/app/api/chat.py`, `_handle_chat`, line `14` | Returns `create_chat_response(session, request)` result | Yes | HTTP entrypoint is `create_chat_reply()` at `backend/app/api/chat.py:24-29` or `create_chat_reply_v1()` at `:32-37`; both delegate to `_handle_chat()`. |
| Conversation Manager | Yes | `backend/app/services/conversation_manager.py`, `ConversationManager.handle`, line `509` | Final `ChatResponse` with knowledge fallback and conversation metadata | Yes | Builds base context, extracts filters, detects intent, runs knowledge lookup, asks workflow engine, then finalizes visible response. |
| Workflow Engine | Yes | `backend/app/services/workflow_engine.py`, `WorkflowEngine.handle`, line `504` | `None` | Yes | `_resolve_workflow_type()` does not produce a workflow for this message, so workflow processing stops immediately. |
| Execution Policy | Yes | `backend/app/llm/execution_policy.py`, `AIExecutionPolicyEvaluator.evaluate`, lines `204-215` | `AIExecutionDecision` with baseline knowledge mode and `should_execute_shadow=False` | No for LLM path | Shadow request is rejected here. Baseline owner is knowledge because `knowledge_eligible=True` and `knowledge_match_available=True` (`backend/app/llm/execution_policy.py:231-233`). |
| Vector-less RAG | Yes | `backend/app/knowledge/retrieval.py`, `KnowledgeRetrievalService.retrieve_top_match`, line `98` | `KnowledgeRetrievalMatch(document_id="faq.preparation.general", title="Appointment Preparation Guide", score=5, matched_terms=("should",))` | Yes | The message is weakly matched to the preparation FAQ on the token `should`. |
| Runtime Facade | Yes | `backend/app/llm/facade.py`, `LLMRuntimeFacade.run_shadow_mode`, lines `263-270` | `LLMShadowModeDispatchResult(scheduled=False, diagnostic=SKIPPED)` | No for LLM path | This is the concrete stop before prompt building and Claude transport. |
| Prompt Builder | No | Not reached | None | No | `LLMRuntimeFacade._execute_shadow_mode()` is never called, so `composition.orchestrator.generate()` is never reached (`backend/app/llm/facade.py:285-289`, `:581-589`). |
| LLM Orchestrator | No | Not reached | None | No | Blocked upstream by `run_shadow_mode()` early return at `backend/app/llm/facade.py:263-270`. |
| LLM Integration Service | No | Not reached | None | No | `LLMIntegrationService.generate()` at `backend/app/llm/service.py:54-88` is never called. |
| Provider Registry | No | Not reached | None | No | No request-time registry lookup occurs because `LLMIntegrationService.generate()` is not entered. |
| Claude Adapter | No | Not reached | None | No | Adapter `generate()` path in `backend/app/llm/adapters.py:14-43` is never called. |
| Claude Transport | No | Not reached | None | No | `ClaudeTransport.invoke()` in `backend/app/llm/transport.py:70-163` is never called. |
| Runtime Validator | No | Not reached | None | No | Validation exists only in controlled generation via `run_controlled_generation()` (`backend/app/llm/facade.py:355-378`), not this shadow-skipped path. |
| Runtime Eligibility | No | Not reached | None | No | Eligibility exists only in controlled generation via `run_controlled_generation()` (`backend/app/llm/facade.py:379-425`). |
| Runtime Composer | No | Not reached | None | No | Composer exists only in controlled generation or deterministic-only facade composition, not in this shadow-skipped chat path. |
| Runtime Post Processor | No | Not reached | None | No | Post-processing exists only after facade composition in controlled generation (`backend/app/llm/facade.py:514-550`). |

## Detailed Step-by-Step Path

1. The request enters `POST /chat` or `POST /v1/chat` and is passed to `_handle_chat()` in `backend/app/api/chat.py:12-21`.
2. `_handle_chat()` calls `create_chat_response(session, request)` at `backend/app/api/chat.py:14`.
3. `create_chat_response()` constructs `ConversationManager(...)` and calls `manager.handle(request)` at `backend/app/services/chat_service.py:666-681`.
4. `ConversationManager.handle()` builds request-scoped conversation state at `backend/app/services/conversation_manager.py:353-374`.
5. It extracts search filters at `:375-376`. For this message, all filters are `None`.
6. It detects intent at `:377`. `detect_chat_intent()` returns `APPOINTMENT_HELP` because the normalized message contains the booking keyword `consult` (`backend/app/services/chat_intent_detector.py:15-24`, `:104-115`).
7. It runs Vector-less RAG at `backend/app/services/conversation_manager.py:388`. `retrieve_top_match()` returns the `Appointment Preparation Guide` document on a weak token match `("should",)` (`backend/app/knowledge/retrieval.py:81-98`, `:149-177`).
8. It calls `WorkflowEngine.handle()` at `backend/app/services/conversation_manager.py:400-404`.
9. `WorkflowEngine.handle()` resolves workflow type at `backend/app/services/workflow_engine.py:498-503`. `_resolve_workflow_type()` returns `None` because the message is not an actionable booking/cancellation/confirmation workflow and there is no selected doctor or workflow follow-up context (`backend/app/services/workflow_engine.py:246-275`).
10. Control returns to `ConversationManager.handle()`. Since workflow returned `None` and knowledge exists and knowledge is allowed for `APPOINTMENT_HELP`, the visible response is created from the knowledge document at `backend/app/services/conversation_manager.py:421-430`.
11. `ConversationManager` sets `response.conversation.routed_to = FUTURE_AI_LAYER` at `backend/app/services/conversation_manager.py:449-461`.
12. `ConversationManager._run_shadow_mode()` is called at `backend/app/services/conversation_manager.py:462-469`.
13. `_run_shadow_mode()` calls `LLMRuntimeFacade.run_shadow_mode(...)` at `backend/app/services/conversation_manager.py:290-318`.
14. `LLMRuntimeFacade.run_shadow_mode()` evaluates shadow policy at `backend/app/llm/facade.py:262`.
15. `AIExecutionPolicyEvaluator.evaluate()` receives a shadow request and enters the shadow branch at `backend/app/llm/execution_policy.py:197`.
16. Because `activation.shadow_mode` and `activation.generation_available` are not both true, policy returns the fallback decision at `backend/app/llm/execution_policy.py:204-215`.
17. `LLMRuntimeFacade.run_shadow_mode()` sees `decision.should_execute_shadow == False` and returns immediately at `backend/app/llm/facade.py:263-270`.
18. Since that early return happens, `_execute_shadow_mode()` is never called, so the entire downstream path is skipped: Prompt Builder, Orchestrator, Integration Service, Registry lookup, Claude Adapter, Claude Transport, Validator, Eligibility, Composer, Post Processor.
19. `ConversationManager.handle()` emits the final response and returns at `backend/app/services/conversation_manager.py:488-509`.
20. `_handle_chat()` returns that `ChatResponse` to FastAPI at `backend/app/api/chat.py:14`.

## Exact Stop Before Claude Transport

Primary stop location for this execution:

- File: `backend/app/llm/facade.py`
- Class: `LLMRuntimeFacade`
- Method: `run_shadow_mode`
- Line: `263`
- Condition: `if not decision.should_execute_shadow:`

Why it stopped:

- The decision was produced in `backend/app/llm/execution_policy.py`, class `AIExecutionPolicyEvaluator`, method `evaluate`, lines `197-215`.
- Shadow execution was rejected because runtime activation did not satisfy the shadow-execution gate.
- In the current repo-root execution context, the composed activation snapshot resolved to `llm_enabled=False`, `shadow_mode=False`, and `generation_available=False`, so the shadow request cannot proceed.

## Practical Interpretation

- The user-facing answer for this request is currently not a specialist recommendation.
- The request is misrouted into the knowledge FAQ path because `consult` is treated as a booking/help keyword by the intent detector, and the knowledge retriever accepts a weak match on `should`.
- The Claude path is not reached at all for this execution because shadow execution is blocked before prompt generation begins.
