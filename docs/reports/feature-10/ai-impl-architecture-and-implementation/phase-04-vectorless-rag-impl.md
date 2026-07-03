# Phase 04 Vector-less RAG Implementation Report

Date: 2026-07-03

Commit range analyzed:
- `a1d99e0488ab2483cb93474fe7ca231104bea73c` (2026-07-01)
- `6bbd350abe717cfa3160c9f6267f81b820b7f4f5` (2026-07-02)

Stabilization update scope for this revision:
- `09c46e0ac91fd7c3cbec1485a2d83fe3f754f614` (2026-07-02)
- `b4a21b173bfb8975cda8951438282b401855e885` (2026-07-02)
- `6cd0da4fa952359b176108fdb18dac3b15d0dbc3` (2026-07-02)
- `6bbd350abe717cfa3160c9f6267f81b820b7f4f5` (2026-07-02)
- `46311c7285b564a00105bf6270b9436a686221c7` (2026-07-03)
- `457385da01122ca01b3a3e856aa684436d353dac` (2026-07-03, report generation only)
- `219a37e25fd3be68d5aaaaaf9916c86453afd7a2` (2026-07-03, report update only)

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
12. `46311c7` booking workflow validation/error handling stabilization

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
- `docs/prompts/ai-impl-architecture-and-implementation/phase-4-vectorless-rag/debug-and-issue-fix/4-fix-503-500-in-appontment-booking-prompt.md`
- `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-04-manual-test-checklist.md`

## Files Modified

### Backend runtime and contracts

- `backend/app/api/chat.py`
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
- `backend/tests/test_conversation_manager.py`
- `backend/tests/test_knowledge_repository.py`

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
   - Later commits refined scoring so exact phrase matches and explicit metadata beat weak incidental overlap, while broad tokens such as `online`, `appointment`, `support`, and `methods` no longer dominate unrelated requests.

4. Chat orchestration and UI exposure
   - `backend/app/services/conversation_manager.py` still executes workflows first, then uses knowledge retrieval for eligible non-workflow turns, and falls back to the legacy deterministic engine when retrieval finds nothing useful.
   - The post-implementation stabilization commits tightened that routing so knowledge-backed FAQ replies are emitted before the generic deterministic fallback path for eligible non-workflow turns.
   - Booking-workflow execution now also converts expected booking validation failures into structured `INPUT_REQUIRED` workflow responses, keeping the active draft usable for retry instead of leaking those cases as chat transport failures.
   - `backend/app/schemas/chat.py` adds optional `knowledge_source` metadata to the chat response contract.
   - The frontend AI widget maps and renders that metadata as a small source footer on plain assistant text responses only.

## Integration Points

- Backend chat entrypoint
  - `ConversationManager` now accepts `KnowledgeRetrievalService` and resolves routing between workflow, knowledge, and deterministic fallback paths.
  - The July 2 stabilization commits changed the ordering inside this boundary so knowledge matches can win before the legacy deterministic unknown-response path when no workflow is active.

- Existing deterministic chat engine
  - `chat_service.py` remains the primary non-workflow engine and now also contains the knowledge repository bootstrap and response formatting helpers.

- Existing workflow engine
  - `WorkflowEngine` remains authoritative for booking, cancellation, and appointment confirmation. Knowledge lookup is explicitly skipped while a workflow is active.
  - Booking continuation also now depends on merged draft state from prior turns plus the newer explicit-date and labeled-name extraction patterns, which prevents repeated missing-field prompts during incremental booking conversations.
  - Booking completion now traps expected `HTTPException` and `ValidationError` failures from `create_appointment_booking(...)` and maps them back into deterministic workflow guidance so the same booking session can continue.

- Chat API contract
  - `ChatResponse` now supports `knowledge_source` while preserving `message`, `response`, `data`, `workflow`, and `conversation`.

- Chat API transport boundary
  - `backend/app/api/chat.py` now re-raises expected `HTTPException` values and reserves HTTP 500 for unexpected failures only, replacing the earlier behavior that collapsed business-validation cases into HTTP 503.

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

- Prefer phrase-level and metadata-aware ranking over raw token overlap.
  Manual-test regressions showed that weak single-token matches were not precise enough, so the retrieval service now gives stronger weight to title/alias/keyword phrase hits before body-text overlap.

- Keep knowledge metadata optional on the wire.
  Existing clients can ignore `knowledge_source`, and the frontend renders it only when present.

- Fix regressions in the same phase rather than deferring them.
  Manual testing exposed routing noise and booking continuation regressions, so the phase closed with retrieval tuning plus workflow-entry extraction fixes.

- Keep expected business validation failures inside the workflow layer.
  Booking errors such as past dates, invalid doctor context, unavailable times, duplicate slots, and invalid patient fields now return structured workflow guidance instead of being treated as transport-level chat outages.

## Stabilization Summary

### Fix 1: Knowledge responses were losing to deterministic fallback on FAQ-style prompts

- Issue
  Eligible informational queries could fall through to the legacy deterministic response path instead of returning the matched knowledge document.
- Root Cause
  `ConversationManager` workflow-first behavior was intact, but the non-workflow branch did not consistently prioritize the retrieved knowledge match ahead of the generic deterministic fallback response.
- Implementation
  The routing logic was tightened so workflows still win first, active workflows still bypass retrieval, and otherwise a successful knowledge match returns a knowledge-backed response before the legacy fallback path runs.
- Files Changed
  `backend/app/services/conversation_manager.py`, `backend/app/knowledge/retrieval.py`, `backend/tests/test_conversation_manager.py`, `backend/tests/test_chat_api.py`, `backend/tests/test_knowledge_repository.py`
- Backward Compatibility
  Chat endpoints and response structure stayed unchanged; only the answer-selection order changed for eligible non-workflow turns.

### Fix 2: Weak retrieval matches were stealing unrelated informational requests

- Issue
  Queries such as consultation-hours, telemedicine, payment-method, and unrelated fallback prompts could resolve to the wrong FAQ because broad single tokens matched too easily.
- Root Cause
  Early deterministic scoring leaned too heavily on token overlap, and the knowledge corpus did not yet expose enough explicit metadata to disambiguate similar FAQ domains.
- Implementation
  Retrieval scoring was upgraded to consider title, alias, keyword, synonym, and category phrase matches separately; new stopwords and phrase normalization reduced noisy tokens; and the FAQ source files were enriched with targeted retrieval metadata plus new bundled documents for insurance, parking, payment methods, consultation hours, telemedicine, and appointment preparation.
- Files Changed
  `backend/app/knowledge/documents.py`, `backend/app/knowledge/retrieval.py`, `backend/app/knowledge/sources/faq/appointment-preparation.md`, `backend/app/knowledge/sources/faq/booking.md`, `backend/app/knowledge/sources/faq/cancellation.md`, `backend/app/knowledge/sources/faq/consultation-hours.md`, `backend/app/knowledge/sources/faq/insurance.md`, `backend/app/knowledge/sources/faq/parking.md`, `backend/app/knowledge/sources/faq/payment-methods.md`, `backend/app/knowledge/sources/faq/telemedicine.md`, `backend/tests/test_knowledge_repository.py`, `backend/tests/test_chat_api.py`
- Backward Compatibility
  The retrieval service remains read-only and single-document; the change improves ranking without altering API contracts or workflow ownership of state-changing actions.

### Fix 3: Informational prompts containing words like `methods` triggered false gender extraction

- Issue
  A prompt such as `What payment methods do you accept?` could be misread as a male-doctor search instead of an informational FAQ request.
- Root Cause
  Gender extraction matched male/female markers by substring rather than word boundary, so unrelated words containing `men` or similar fragments polluted entity extraction.
- Implementation
  Gender matching was restricted to explicit whole-word patterns and covered with regression tests tied to payment-method prompts.
- Files Changed
  `backend/app/services/chat_entity_extractor.py`, `backend/tests/test_chat_entity_extractor.py`, `backend/tests/test_chat_api.py`
- Backward Compatibility
  Existing valid gender-filter prompts still work; only accidental false positives were removed.

### Fix 4: Booking workflow continuation dropped new values or failed to start from direct doctor-reference prompts

- Issue
  Incremental booking conversations could repeat stale missing-field prompts, and direct entry prompts such as `Book appointment with Dr. Sarah Jenkins` did not always progress correctly.
- Root Cause
  The draft-building path did not fully merge newly supplied date, time, patient-name, and email values into the active workflow state before validating missing fields, and extraction coverage for absolute dates plus labeled name fields was incomplete.
- Implementation
  Booking extraction now supports explicit absolute dates in textual and numeric forms, labeled patient-name lines, bare-name follow-up replies when the workflow is specifically waiting for the patient name, and direct doctor-reference entry prompts. `WorkflowEngine` now carries the merged draft forward so continuation turns progress deterministically.
- Files Changed
  `backend/app/services/chat_entity_extractor.py`, `backend/app/services/workflow_engine.py`, `backend/tests/test_chat_entity_extractor.py`, `backend/tests/test_chat_api.py`
- Backward Compatibility
  The booking workflow type, API shape, and existing step-by-step booking behavior remain unchanged; the fix only broadens accepted input forms and removes continuation regressions.

### Fix 5: Booking validation failures were escaping as chat API 503/500 errors

- Issue
  Expected booking failures such as past dates, already-booked slots, invalid doctor context, invalid appointment times, and invalid patient email data were surfacing as HTTP 503 or HTTP 500 instead of a recoverable booking response.
- Root Cause
  `WorkflowEngine` called the booking service directly and let expected `HTTPException` and `ValidationError` failures bubble out. `backend/app/api/chat.py` then wrapped generic exceptions as a chat-service transport failure, so business validation errors were misclassified as server outages.
- Implementation
  `WorkflowEngine` now catches expected booking validation failures, clears only the invalid draft field when possible, and returns a structured `BOOK_APPOINTMENT` workflow response with `INPUT_REQUIRED` status and deterministic retry guidance. The chat API now re-raises expected `HTTPException` values and returns HTTP 500 only for unexpected failures.
- Files Changed
  `backend/app/api/chat.py`, `backend/app/services/workflow_engine.py`, `backend/tests/test_chat_api.py`
- Backward Compatibility
  Endpoint paths and chat response fields remain unchanged. The behavior change is limited to error classification: expected booking validation failures now stay inside the existing workflow contract instead of becoming transport-level failures.

## Known Limitations

- Retrieval is still deterministic single-document matching, not semantic retrieval.
- There is no confidence threshold or multi-document synthesis beyond score-based best-match selection.
- Knowledge coverage is limited to the bundled FAQ/capability documents added in this phase.
- Retrieval quality still depends on manually curated metadata and stopword tuning; new FAQ areas may need additional aliases, synonyms, or phrase labels to rank correctly.
- Conversation state is still request-scoped metadata passed through the chat payload; there is no persisted conversation store.
- Some booking-validation mappings depend on current service exception details (`already passed`, `already booked`, `not available for the chosen date`), so future wording changes in the appointment service will require matching updates in the workflow error-normalization layer.
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
- A later regression pass also fixed booking-workflow continuation behavior for direct doctor-reference prompts, explicit absolute dates, and labeled patient-name inputs.
- The July 3 defect-fix commit added endpoint-level regression coverage for recoverable booking validation failures plus the unexpected-error path, confirming that past-date, already-booked, invalid-doctor, invalid-time, duplicate-booking, and invalid-patient cases now return structured workflow responses instead of HTTP 503/500.
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
  - payment-method prompts no longer inferring `gender=Male`
  - booking workflow entry and continuation extraction for explicit dates and structured patient details
