# Phase 04 Vector-less RAG Implementation Report

Date: 2026-07-03

Commit range analyzed:
- `a1d99e0488ab2483cb93474fe7ca231104bea73c` (2026-07-01)
- `6bbd350abe717cfa3160c9f6267f81b820b7f4f5` (2026-07-02)

Analyzed commits:
1. `a1d99e0` Vector-less RAG prompt generation and planning docs
2. `a4312dc` backend knowledge repository implementation
3. `0a664eb` deterministic knowledge retrieval service
4. `7aeb1bd` conversation manager integration
5. `6a78a9c` chat API enhancement for knowledge metadata
6. `c62e2b4` frontend knowledge-source mapping
7. `d988bbe` manual test checklist
8. `09c46e0` routing fixes from manual testing
9. `b4a21b1` retrieval quality improvement
10. `6cd0da4` additional retrieval tuning from manual outcomes
11. `6bbd350` booking workflow entry and extraction regression fixes

## Files Added

### Backend knowledge layer

- `backend/app/knowledge/__init__.py`
- `backend/app/knowledge/documents.py`
- `backend/app/knowledge/loader.py`
- `backend/app/knowledge/repository.py`
- `backend/app/knowledge/retrieval.py`
- `backend/app/knowledge/sources/README.md`
- `backend/app/knowledge/sources/faq/appointment-preparation.md`
- `backend/app/knowledge/sources/faq/booking.md`
- `backend/app/knowledge/sources/faq/cancellation.md`
- `backend/app/knowledge/sources/faq/consultation-hours.md`
- `backend/app/knowledge/sources/faq/insurance.md`
- `backend/app/knowledge/sources/faq/parking.md`
- `backend/app/knowledge/sources/faq/payment-methods.md`
- `backend/app/knowledge/sources/faq/telemedicine.md`
- `backend/app/knowledge/sources/structured/assistant-capabilities.json`

### Backend tests

- `backend/tests/test_conversation_manager.py`
- `backend/tests/test_knowledge_repository.py`

### Architecture and implementation docs

- `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/1-vectorless-rag-architecture-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/10-report-generation-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/2-backend-knowledge-repo-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/3-knowledge-retrieval-service-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/4-conversation-manager-integration-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/5-chat-api-enhancement-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/6-frontend-mapping-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/7-manual-test-support-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/8-defect-fix-iteration.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/9-validation-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/debug-and-issue-fix/1-fix-vectorless-routing-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/debug-and-issue-fix/2-retrieval-quality-improvement-prompt.md`
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/debug-and-issue-fix/3-regression-booking-wf-entry-extraction.md`
- `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-04-manual-test-checklist.md`

## Files Modified

### Backend runtime and contracts

- `backend/app/schemas/chat.py`
- `backend/app/services/chat_entity_extractor.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/conversation_manager.py`
- `backend/app/services/workflow_engine.py`
- `backend/pyproject.toml`
- `backend/app.db`

### Backend verification

- `backend/tests/test_chat_api.py`
- `backend/tests/test_chat_entity_extractor.py`

### Frontend AI widget

- `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/types/chat.ts`
- `frontend/lib/ai-widget/types/message.ts`

### Project and AI context docs

- `README.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/report-index.md`
- `docs/ai-content/session-context.md`

## Files Removed

- None in the inspected commit range.

## Architecture Summary

Phase 04 adds a repository-local, deterministic Vector-less RAG layer without replacing the existing workflow-first chat architecture.

The implementation is split into four parts:

1. Knowledge content and schema
   - `backend/app/knowledge/documents.py` defines a typed document contract for Markdown and JSON sources.
   - `backend/app/knowledge/sources/` stores curated FAQ and assistant-capability content inside the repository.

2. Knowledge loading and caching
   - `backend/app/knowledge/loader.py` loads Markdown front matter and JSON payloads, validates them, and normalizes them into `KnowledgeDocument` instances.
   - `backend/app/knowledge/repository.py` keeps an in-memory cache, exact-id lookup, domain filtering, and tag filtering.

3. Deterministic retrieval
   - `backend/app/knowledge/retrieval.py` tokenizes user text, removes broad stopwords, scores title, alias, keyword, synonym, category, and body matches, and returns a single highest-ranked document.
   - Later commits refined scoring so exact phrase matches and explicit metadata beat weak incidental overlap.

4. Chat orchestration and UI exposure
   - `backend/app/services/conversation_manager.py` still executes workflows first, then uses knowledge retrieval for eligible non-workflow turns, and falls back to the legacy deterministic engine when retrieval finds nothing useful.
   - `backend/app/schemas/chat.py` adds optional `knowledge_source` metadata to the chat response contract.
   - The frontend AI widget maps and renders that metadata as a small source footer on plain assistant text responses only.

## Integration Points

- Backend chat entrypoint
  - `ConversationManager` now accepts `KnowledgeRetrievalService` and resolves routing between workflow, knowledge, and deterministic fallback paths.

- Existing deterministic chat engine
  - `chat_service.py` remains the primary non-workflow engine and now also contains the knowledge repository bootstrap and response formatting helpers.

- Existing workflow engine
  - `WorkflowEngine` remains authoritative for booking, cancellation, and appointment confirmation. Knowledge lookup is explicitly skipped while a workflow is active.

- Chat API contract
  - `ChatResponse` now supports `knowledge_source` while preserving `message`, `response`, `data`, `workflow`, and `conversation`.

- Frontend widget rendering
  - `chat-response-mapper.ts` forwards `knowledge_source` into message metadata.
  - `MessageContentRenderer.tsx` renders document title, source path, and matched terms in a footer for text replies.
  - Structured doctor, availability, and help cards are intentionally unchanged.

- Knowledge content packaging
  - `backend/pyproject.toml` includes bundled knowledge files so the backend package ships the repository-local FAQ/JSON sources.

## Business APIs Reused

The phase reuses existing domain and workflow services instead of introducing new booking logic:

- `app.services.appointment_service.create_appointment_booking`
- `app.services.appointment_service.cancel_appointment_booking`
- `app.services.appointment_service.get_appointment_confirmation_by_reference`
- `app.services.doctor_service.list_doctors`
- `app.services.availability_service.get_available_slots`

This kept Vector-less RAG read-only for informational turns while leaving all booking and appointment state mutations in the pre-existing business layer.

## Design Decisions

- Keep workflow-first orchestration.
  Knowledge retrieval only runs for non-active-workflow turns so booking, cancellation, and confirmation flows cannot be displaced by FAQ matches.

- Use repository-local curated knowledge instead of embeddings or an external vector store.
  The implementation stays deterministic, inspectable, testable, and deployable with the current stack.

- Return one top document rather than assembling multi-document context.
  This keeps the first phase small and predictable, and it matches the current plain-text response model.

- Prefer explicit retrieval metadata over body-text coincidence.
  `category`, `keywords`, `synonyms`, and `aliases` were added so important FAQ prompts can be steered without changing the document body.

- Keep knowledge metadata optional on the wire.
  Existing clients can ignore `knowledge_source`, and the frontend renders it only when present.

- Fix regressions in the same phase rather than deferring them.
  Manual testing exposed routing noise and booking continuation regressions, so the phase closed with retrieval tuning plus workflow-entry extraction fixes.

## Known Limitations

- Retrieval is still deterministic single-document matching, not semantic retrieval.
- There is no confidence threshold or multi-document synthesis beyond score-based best-match selection.
- Knowledge coverage is limited to the bundled FAQ/capability documents added in this phase.
- Conversation state is still request-scoped metadata passed through the chat payload; there is no persisted conversation store.
- Manual testing artifacts exist, but the inspected commits do not include a full final human execution log inside this report file.
- `backend/app.db` changed during the range, but the Vector-less RAG architecture itself does not depend on a new database schema.

## Backward Compatibility

The implementation is backward compatible for the current app surface for four reasons:

1. Chat endpoints are unchanged.
   The API still returns the existing `message`, `response`, `data`, `workflow`, and `conversation` fields.

2. Knowledge metadata is additive.
   `knowledge_source` is optional, so older frontend behavior still works when that field is ignored or absent.

3. Workflow execution still owns state-changing operations.
   Booking, cancellation, and confirmation reuse the existing appointment services instead of introducing a parallel path.

4. Structured UI behavior is preserved.
   Doctor cards, availability cards, help cards, booking redirects, and confirmation handoff remain on the previous rendering path.

## Manual Verification Summary

- Added a dedicated checklist in `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-04-manual-test-checklist.md`.
- Manual-testing commits on 2026-07-02 drove two classes of fixes:
  - routing fixes so knowledge responses win before generic deterministic fallback for eligible FAQ-style turns
  - retrieval quality fixes so broad terms such as `online`, `appointment`, or `methods` do not steal unrelated requests
- Regression coverage was expanded in:
  - `backend/tests/test_knowledge_repository.py`
  - `backend/tests/test_conversation_manager.py`
  - `backend/tests/test_chat_api.py`
  - `backend/tests/test_chat_entity_extractor.py`
- The added tests verify:
  - bundled knowledge loading and validation
  - knowledge-hit vs no-match fallback behavior
  - workflow-first routing
  - knowledge metadata serialization
  - phrase-priority retrieval ranking
  - protection against weak single-token overlap
  - booking workflow entry and continuation extraction for explicit dates and structured patient details
