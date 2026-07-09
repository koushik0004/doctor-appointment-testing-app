# Session Context

## Project Summary

Doctor appointment booking app with a Next.js frontend, FastAPI backend, and SQLite database. Core implemented flows are doctor listing, appointment booking, booking confirmation, appointment search, and a rule-based AI chat assistant.

## Current Architecture

- `frontend/`: Next.js App Router app with feature APIs, booking UI, doctor UI, and the global AI widget.
- `backend/`: FastAPI app with thin routes, service-layer business logic, SQLAlchemy models/repositories, and SQLite persistence.
- Request path: frontend UI -> `frontend/lib/api-client.ts` -> `frontend/app/api/[...path]/route.ts` -> backend API/services -> SQLite.
- Chat orchestration path: `backend/app/api/chat.py` -> `backend/app/services/conversation_manager.py` -> `backend/app/services/workflow_engine.py` -> deterministic fallback in `backend/app/services/chat_service.py`, with low-risk requests now able to continue into controlled generation through `backend/app/llm/facade.py`.
- Doctor-details chat routing now explicitly handles partial `Dr. <first-name>` mentions and `Who is Dr. ...` profile queries in the deterministic fallback path.
- Active booking chat workflows now retain ownership across incremental turns, preserve merged draft fields in conversation metadata, and auto-complete booking once all mandatory fields are present.
- The frontend AI widget now redirects directly to `/appointments/confirmation` after a successful chat booking using the returned workflow payload plus the existing booking store.
- Vector-less RAG Phase 4 has backend knowledge components under `backend/app/knowledge/`: a Markdown/JSON repository cache plus a deterministic retrieval service that returns the top title/keyword match. `ConversationManager` now preserves workflow-first behavior, uses knowledge responses before the legacy deterministic chatbot for FAQ-style non-workflow turns, returns optional `knowledge_source` metadata on those replies, and still falls back to the existing deterministic chat engine when retrieval returns no usable match.
- Bundled knowledge coverage now includes booking help, cancellation guidance, consultation hours, telemedicine, appointment preparation, payment methods, insurance, parking, and assistant capabilities; retrieval token filtering excludes broad terms that previously stole doctor search, availability, fee, and unrelated fallback requests.
- Knowledge documents now carry additive retrieval metadata (`category`, `keywords`, `synonyms`, `aliases`) and the deterministic scoring model prioritizes title, alias, keyword, synonym, category, then body-text matches; exact phrase hits are weighted above weak single-token overlap so informational queries resolve to the intended FAQ more reliably.
- The chat entity extractor now uses word-boundary gender matching, preventing unrelated informational prompts such as `payment methods` from being misclassified as male-doctor searches.
- Booking extraction now also supports explicit absolute dates (`2nd July 2026`, `02/07/2026`), labeled patient-name lines, and direct `Book appointment with Dr. ...` entry prompts so incremental booking turns progress without repeating stale missing-field prompts.
- Booking workflow execution now maps expected booking validation failures back into deterministic `BOOK_APPOINTMENT` workflow responses, preserving active draft state for retry instead of letting those cases escape as chat API 500/503 errors.
- Phase 5.1 added an inactive standalone backend prompt-builder module at `backend/app/services/prompt_builder.py`; Phase 5.2 now gives it a canonical provider-agnostic internal `PromptContext` model, Phase 5.2.5 adds a dedicated deterministic validation gate over that model, Phase 5.3 adds an internal Conversation Context Collector for caller-supplied conversation state, Phase 5.4 adds an internal Workflow Context Collector for caller-supplied workflow state, Phase 5.5 adds an internal Knowledge Context Collector for already-selected repository documents, Phase 5.6 adds an internal System Instruction Builder for deterministic application-rule and caller-instruction construction, Phase 5.7 adds an internal Prompt Assembly Pipeline that turns validated context into ordered renderable sections, and Phase 5.8 adds a dedicated PromptRenderer as the final deterministic rendering stage. It is still not wired into `ConversationManager`, retrieval, workflows, or any external API.
- Phase 6.1 adds a new inactive backend provider-neutral LLM Integration seam at `backend/app/llm/` with internal request/response models, provider/registry protocols, and an `LLMIntegrationService` facade. Phase 6.2 refines that seam with explicit request/response translator contracts, a shared adapter base class, and an inactive in-memory registry implementation. Phase 6.3 refines the canonical contract itself so requests and responses can carry provider-neutral structured-output, tool-calling, reasoning, streaming, citation, provider/model metadata, and multimodal-intent fields while remaining backward compatible and fully disconnected from `ConversationManager`, `WorkflowEngine`, Vector-less RAG, Prompt Builder, FastAPI routes, and frontend chat flows. Phase 6.4 adds an inactive `LLMGenerationOrchestrator` that coordinates already-collected generation input through `PromptBuilderService`, canonical request construction, `LLMIntegrationService`, and normalized result shaping without changing runtime wiring or Prompt Builder ownership. Phase 6.5 adds an inactive provider-neutral configuration seam at `backend/app/llm/config.py` with canonical provider settings, nested environment mapping, deterministic defaults, provider validation, and `.env.example` documentation for OpenAI, Claude, Gemini, OpenRouter, and Ollama, still without SDK integration or runtime wiring. Phase 6.5.5 adds an inactive `backend/app/llm/budget.py` seam with canonical generation-budget profiles and configuration-backed overrides for reasoning effort, token budgets, latency preference, quality preference, and cost preference; adapters remain responsible for future provider-native translation. Phase 6.6 adds inactive concrete adapters in `backend/app/llm/providers.py` for OpenAI, Claude, Gemini, OpenRouter, and Ollama plus explicit transport injection and a config-backed adapter factory. Phase 6.7 adds an inactive `backend/app/llm/composition.py` composition root that loads configuration once, creates transports separately, instantiates enabled adapters, builds the registry, resolves the default provider, and composes `LLMIntegrationService` plus `LLMGenerationOrchestrator` through explicit constructor injection while keeping runtime wiring unchanged. Phase 6.8 adds an inactive `backend/app/llm/activation.py` seam that evaluates runtime feature flags, selected-provider readiness, transport and adapter presence, authentication and generation-budget readiness, and safe activation diagnostics without changing routing or enabling live generation. Phase 6.9 adds an inactive `backend/app/llm/execution_policy.py` seam that turns activation status plus provider-neutral request hints into canonical routing decisions for workflow, knowledge, deterministic, hybrid, LLM-only, and shadow execution modes without wiring any of those decisions into the live chat path. Phase 6.10 adds an inactive `backend/app/llm/operations.py` seam that derives provider-neutral observability, accounting, health, retry, timeout, audit, privacy, rollout, and performance-readiness models from the composed subsystem without enabling runtime execution or rollout. Phase 7 adds `backend/app/llm/facade.py` as the public runtime boundary; Phase 7.2 extends that facade so `ConversationManager` can trigger hidden shadow-mode orchestration, capture provider-neutral diagnostics, and discard all LLM output while preserving the exact visible workflow, knowledge, and deterministic chat responses; Phase 7.3 completes that hidden path by ensuring each shadow execution reaches the full Prompt Builder -> Prompt Renderer -> Orchestrator pipeline with canonical workflow context included in the rendered prompt; Phase 7.4 adds a policy-gated controlled-generation branch on that same facade so LLM-capable modes can return generated runtime results only when activation and execution policy explicitly allow it; Phase 7.5 adds a provider-neutral runtime-response validation gate on that same facade so controlled generation is validated against canonical response requirements before any visible LLM output and falls back safely on invalid runtime results; Phase 7.6 adds a provider-neutral runtime-response eligibility gate on that same facade so only explicitly approved low-risk conversational responses can be exposed to the user after validation while workflow-owned requests remain deterministic; Phase 7.7 adds a provider-neutral runtime-response composer on that same facade so deterministic-only, LLM-only, and hybrid final responses can preserve business truth while optionally appending validated and eligible LLM guidance; Phase 7.8 adds a provider-neutral runtime-response post processor on that same facade so composed responses can be normalized for presentation, sanitized for presentation-only metadata, and returned with separate post-processing diagnostics before frontend visibility. Phase 8 adds `backend/app/llm/transport.py` plus a `ProductionLLMProviderTransportFactory` default so Claude now has a real Anthropic-SDK-backed production transport with normalized error mapping, structured transport logging, request/response id extraction, usage extraction, activation diagnostics, and a provider-specific request serializer that now strips internal runtime metadata from outgoing Anthropic `messages.create(...)` payloads while preserving supported fields such as `user_id`. The July 8, 2026 runtime-trace follow-up adds `backend/app/llm/runtime_trace.py` plus request-scoped instrumentation across `ConversationManager`, the facade, orchestrator, integration service, adapters, and Claude transport so `AI_RUNTIME_TRACE=true` now emits structured backend diagnostics for end-to-end LLM-path debugging, including explicit `llm_not_invoked` stop reasons when execution never reaches transport or a controlled-generation skip point. The same follow-up now emits a final controlled-generation summary on every SKIPPED or FAILED result with execution mode, provider readiness, orchestration progress, stage flags, fallback reason, and exception details. The broader observability-layer follow-up now writes one raw JSON trace per request through an independent `ai.runtime.trace` rotating file logger, emits exactly once from the `ConversationManager` `finally` block, auto-creates `logs/ai-runtime-trace.log`, normalizes every required stage to `entered`/`completed`/`duration_ms`/`status`, and records exception component/type/message/stack traces across workflow, retrieval, integration, adapter, and transport boundaries.
- Manual-test demo data now uses an idempotent seed utility at `backend/scripts/seed_test_data.py`; the July 3, 2026 update added four extra doctor profiles to `backend/app.db`, preserved the earlier seeded appointments/patients, and now pins the default SQLite target to the absolute backend DB path so root-level runs do not write elsewhere.
- A July 3, 2026 data-health refresh validated the live `backend/app.db` dataset without mutating any rows; it confirmed current doctor/patient/appointment records remain valid for implemented flows, and documented one retained legacy `doctor_availability` mismatch plus the historical-only status of that table in `docs/reports/test-data-health-report.md`.
- The frontend AI widget now surfaces optional `knowledge_source` metadata on assistant text replies with a minimal source footer while leaving structured workflow cards unchanged.
- Phase 4.7 added a dedicated manual test checklist for the Vector-less RAG prototype covering positive, negative, edge, regression, workflow, and existing chatbot scenarios.
- AI assistant master reference: `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md`.
- Whole-platform master architecture reference: `docs/reports/architecture/architecture.md`.
- AI Assistant API design reference: `docs/reports/architecture/AI-Assistant-API-Design.md`.
- AI runtime sequence diagram reference: `docs/reports/architecture/AI-Runtime-Sequence-Diagrams.md`.
- Whole-repository reverse-engineering reference: `docs/reports/architecture/reverse-engineering-report.md`.
- Whole-repository high-level design reference: `docs/reports/architecture/HLD.md`.
- Whole-repository low-level design reference: `docs/reports/architecture/LLD.md`.
- AI execution decision record: `docs/analysis/hybrid-ai-assistant-architecture/adr-001-deterministic-ai-engine-primary.md`.
- Vector-less RAG reference: `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`.
- LLM integration seam reference: `docs/analysis/hybrid-ai-assistant-architecture/llm-integration-architecture.md`.
- LLM runtime composition reference: `docs/analysis/hybrid-ai-assistant-architecture/llm-runtime-composition-architecture.md`.
- LLM runtime activation reference: `docs/analysis/hybrid-ai-assistant-architecture/llm-runtime-activation-architecture.md`.
- LLM execution policy reference: `docs/analysis/hybrid-ai-assistant-architecture/llm-execution-policy-architecture.md`.
- LLM operational readiness reference: `docs/analysis/hybrid-ai-assistant-architecture/llm-operational-readiness-architecture.md`.

## Boundaries

- Keep frontend UI/state/proxy logic in `frontend/`.
- Keep backend routes, business rules, schemas, and DB logic in `backend/`.
- Do not mix frontend and backend logic in the same change.

## Context Loading Rules

- Read only AI context files first.
- Do not scan the full repo unless the task requires it.
- Prefer summaries over full reports.

## Read First

1. `docs/ai-content/current-task.md`
2. `docs/ai-content/important-files.md`
3. `docs/ai-content/feature-map.md`
4. `docs/ai-content/report-index.md`
5. `docs/ai-content/project-map.md` when architecture context is needed

## Important Runtime Files

- Frontend shell/proxy: `frontend/app/layout.tsx`, `frontend/app/api/[...path]/route.ts`, `frontend/lib/api-client.ts`
- Booking flow: `frontend/app/appointments/page.tsx`, `frontend/features/appointments/api.ts`, `frontend/stores/booking-store.ts`
- Backend entry/router: `backend/app/main.py`, `backend/app/api/router.py`, `backend/app/db/database.py`
- Booking/chat services: `backend/app/services/availability_service.py`, `backend/app/services/appointment_service.py`, `backend/app/services/conversation_manager.py`, `backend/app/services/workflow_engine.py`, `backend/app/services/chat_service.py`
- Knowledge components: `backend/app/knowledge/documents.py`, `backend/app/knowledge/loader.py`, `backend/app/knowledge/repository.py`, `backend/app/knowledge/retrieval.py`, `backend/app/knowledge/sources/`
- Routing regression tests: `backend/tests/test_conversation_manager.py`, `backend/tests/test_knowledge_repository.py`, `backend/tests/test_chat_api.py`, `backend/tests/test_chat_entity_extractor.py`
- Chat booking frontend handoff: `frontend/components/layout/GlobalAiWidget.tsx`, `frontend/stores/booking-store.ts`

## Commands To Run

- No canonical dev/test command list is recorded in the current AI context files.
- Prefer task-specific commands already captured in reports when validating the same feature area.

## Report Loading Rule

- Use `docs/ai-content/report-index.md` first.
- Read a full file under `docs/reports/` only when the task directly matches that report, the summary says deeper context is needed, or implementation is blocked.

## Known Gaps

- Confirmation email is documented but not evident as an active backend feature.
- AI chat is implemented, but frontend automation/navigation remains limited.
- Conversation and workflow context are request-scoped and transported through chat metadata; there is no persisted conversation store yet.
- `backend/app/llm/__init__.py` now uses lazy re-exports so importing `app.llm.runtime_trace` during startup does not re-enter the orchestrator/prompt-builder chain.

## Task Resume Rule

- Check `docs/ai-content/current-task.md` first for active work.
- Then read files listed there plus the relevant entries from `important-files.md` and `feature-map.md`.
- Restart broader analysis only if the recorded task context is missing or stale.
