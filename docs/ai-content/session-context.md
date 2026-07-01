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
- Vector-less RAG Phase 4 has a passive backend knowledge repository under `backend/app/knowledge/` that loads curated Markdown/JSON files into an in-memory cache. It is not wired into chat routing, retrieval, APIs, `ConversationManager`, or `WorkflowEngine`.
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
- Knowledge repository: `backend/app/knowledge/documents.py`, `backend/app/knowledge/loader.py`, `backend/app/knowledge/repository.py`, `backend/app/knowledge/sources/`
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
