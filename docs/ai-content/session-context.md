# Session Context

## Project Summary

Doctor appointment booking app with a Next.js frontend, FastAPI backend, and SQLite database. Core implemented flows are doctor listing, appointment booking, booking confirmation, appointment search, and a rule-based AI chat assistant.

## Current Architecture

- `frontend/`: Next.js App Router app with feature APIs, booking UI, doctor UI, and the global AI widget.
- `backend/`: FastAPI app with thin routes, service-layer business logic, SQLAlchemy models/repositories, and SQLite persistence.
- Request path: frontend UI -> `frontend/lib/api-client.ts` -> `frontend/app/api/[...path]/route.ts` -> backend API/services -> SQLite.
- Chat orchestration path: `backend/app/api/chat.py` -> `backend/app/services/conversation_manager.py` -> `backend/app/services/workflow_engine.py` -> deterministic fallback in `backend/app/services/chat_service.py`.
- Doctor-details chat routing now explicitly handles partial `Dr. <first-name>` mentions and `Who is Dr. ...` profile queries in the deterministic fallback path.
- Active booking chat workflows now retain ownership across incremental turns, preserve merged draft fields in conversation metadata, and auto-complete booking once all mandatory fields are present.
- The frontend AI widget now redirects directly to `/appointments/confirmation` after a successful chat booking using the returned workflow payload plus the existing booking store.
- Vector-less RAG Phase 4 has backend knowledge components under `backend/app/knowledge/`: a Markdown/JSON repository cache plus a deterministic retrieval service that returns the top title/keyword match. `ConversationManager` now preserves workflow-first behavior, uses knowledge responses before the legacy deterministic chatbot for FAQ-style non-workflow turns, returns optional `knowledge_source` metadata on those replies, and still falls back to the existing deterministic chat engine when retrieval returns no usable match.
- Bundled knowledge coverage now includes booking help, cancellation guidance, consultation hours, telemedicine, appointment preparation, payment methods, insurance, parking, and assistant capabilities; retrieval token filtering excludes broad terms that previously stole doctor search, availability, fee, and unrelated fallback requests.
- Knowledge documents now carry additive retrieval metadata (`category`, `keywords`, `synonyms`, `aliases`) and the deterministic scoring model prioritizes title, alias, keyword, synonym, category, then body-text matches; exact phrase hits are weighted above weak single-token overlap so informational queries resolve to the intended FAQ more reliably.
- The chat entity extractor now uses word-boundary gender matching, preventing unrelated informational prompts such as `payment methods` from being misclassified as male-doctor searches.
- Booking extraction now also supports explicit absolute dates (`2nd July 2026`, `02/07/2026`), labeled patient-name lines, and direct `Book appointment with Dr. ...` entry prompts so incremental booking turns progress without repeating stale missing-field prompts.
- Booking workflow execution now maps expected booking validation failures back into deterministic `BOOK_APPOINTMENT` workflow responses, preserving active draft state for retry instead of letting those cases escape as chat API 500/503 errors.
- Phase 5.1 added an inactive standalone backend prompt-builder module at `backend/app/services/prompt_builder.py`; Phase 5.2 now gives it a canonical provider-agnostic internal `PromptContext` model, Phase 5.2.5 adds a dedicated deterministic validation gate over that model, and Phase 5.3 adds an internal Conversation Context Collector that normalizes caller-supplied conversation state before validation and prompt rendering. It is still not wired into `ConversationManager`, retrieval, workflows, or any external API.
- Manual-test demo data now uses an idempotent seed utility at `backend/scripts/seed_test_data.py`; the July 3, 2026 update added four extra doctor profiles to `backend/app.db`, preserved the earlier seeded appointments/patients, and now pins the default SQLite target to the absolute backend DB path so root-level runs do not write elsewhere.
- A July 3, 2026 data-health refresh validated the live `backend/app.db` dataset without mutating any rows; it confirmed current doctor/patient/appointment records remain valid for implemented flows, and documented one retained legacy `doctor_availability` mismatch plus the historical-only status of that table in `docs/reports/test-data-health-report.md`.
- The frontend AI widget now surfaces optional `knowledge_source` metadata on assistant text replies with a minimal source footer while leaving structured workflow cards unchanged.
- Phase 4.7 added a dedicated manual test checklist for the Vector-less RAG prototype covering positive, negative, edge, regression, workflow, and existing chatbot scenarios.
- AI assistant master reference: `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md`.
- AI execution decision record: `docs/analysis/hybrid-ai-assistant-architecture/adr-001-deterministic-ai-engine-primary.md`.
- Vector-less RAG reference: `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`.

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

## Task Resume Rule

- Check `docs/ai-content/current-task.md` first for active work.
- Then read files listed there plus the relevant entries from `important-files.md` and `feature-map.md`.
- Restart broader analysis only if the recorded task context is missing or stale.
