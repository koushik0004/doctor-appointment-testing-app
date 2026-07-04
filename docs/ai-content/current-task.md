# Current Task

## Active Work

- Status: completed
- Task: implement Phase 5.2 deterministic Prompt Context model
- Completed on: 2026-07-04

## Outcome

- Added a canonical internal `PromptContext` model beneath the inactive backend Prompt Builder, with structured sections for metadata, user context, conversation context, workflow context, knowledge context, system instructions, constraints, and rendering options.
- Refactored `PromptBuilderService` to build and validate `PromptContext` first, then deterministically render the same external `PromptBuildResult` contract and prompt text behavior as Phase 5.1.
- Kept the new model provider-agnostic and fully outside live `ConversationManager`, retrieval, workflow, API, frontend, and database paths.
- Expanded focused backend tests to cover `PromptContext` creation, optional section omission, deterministic defaults, and backward compatibility of the existing prompt builder output.
- Updated the architecture reference and AI context files so future sessions can continue Prompt Builder work without re-deriving the internal contract.

## Prior Work

- Status: completed
- Task: implement Phase 5.1 standalone prompt builder module
- Completed on: 2026-07-04

## Outcome

- Added an inactive backend `PromptBuilderService` with a deterministic internal contract for composing prompt text from caller-supplied user message, conversation state, and preselected knowledge documents.
- Kept the new module fully outside the live `ConversationManager`, `WorkflowEngine`, Vector-less RAG retrieval, business-service, API, and frontend widget request paths.
- Applied prompt-hint constraints only as bounded formatting rules during prompt construction, including intent-based document inclusion, safe-to-quote handling, and optional per-document context clipping.
- Added focused backend tests covering deterministic prompt assembly, prompt-hint constraint handling, and character-budget truncation behavior.
- Updated the compact AI context and architecture reference so future sessions can find the new prompt-builder seam without re-scanning the repository.

## Prior Work

- Status: completed
- Task: refresh test data health without causing data loss
- Completed on: 2026-07-03

## Outcome

- Inspected the live `backend/app.db` schema and data against the current models and booking/search services with an explicit no-data-loss policy.
- Verified the current doctor, patient, and appointment rows remain valid for implemented workflows; no orphaned relationships, duplicate appointment-slot conflicts, or broken demo appointments were found.
- Confirmed the three future `@example.com` demo bookings still behave correctly under generated availability for July 7, July 8, and July 9, 2026.
- Detected one retained legacy inconsistency in `doctor_availability` where Dr. Sarah Jenkins has a historical `TELEMEDICINE` row despite the live profile supporting only `IN_PERSON`, but intentionally did not mutate it because the table is historical and the current flow no longer depends on it.
- Generated `docs/reports/test-data-health-report.md` documenting schema checks, skipped legacy repair candidates, and the fact that zero rows were inserted, updated, or deleted.

## Prior Work

- Status: completed
- Task: fix Phase 4 booking workflow business-validation failures returning HTTP 500/503
- Completed on: 2026-07-03

## Prior Outcome

- Booking workflow execution now converts expected booking validation failures into structured chat workflow responses instead of surfacing them as transport errors from `/api/chat`.
- Covered business validation scenarios include past appointment date, invalid or unavailable appointment time, already-booked slot / duplicate booking, invalid doctor context, and invalid patient email data.
- Validation responses keep the booking workflow active by preserving valid draft fields, clearing only the invalid field when possible, and returning `INPUT_REQUIRED` workflow state with deterministic next-step guidance.
- Chat API error handling now re-raises expected `HTTPException` values and reserves HTTP 500 for unexpected system failures instead of wrapping everything as HTTP 503.
- Added chat endpoint regression coverage for all validation scenarios plus an explicit unexpected-error test, and revalidated the focused Phase 4 backend suite (`65 passed`).

## Prior Work

- Status: completed
- Task: fix Phase 4 booking-workflow entity extraction and continuation regressions
- Completed on: 2026-07-02

## Outcome

- Deterministic booking extraction now recognizes explicit absolute dates in both textual (`2nd July 2026`) and numeric day-month-year (`02/07/2026`) formats, restoring single-message booking prompts that include doctor, date, and time.
- Booking workflow entry now accepts direct doctor-reference prompts such as `Book appointment with Dr. Sarah Jenkins`, so one-field-per-turn booking conversations can start without a prior doctor-search turn.
- Labeled patient-name lines such as `Patient name: John Doe` and `Full name: John Doe` now parse correctly without swallowing the following email label from multi-line structured booking messages.
- Multi-turn booking continuation now progresses deterministically as newly supplied date, time, patient name, and email values are merged into the active workflow draft before missing-field validation.
- Added focused regression coverage for explicit-date extraction plus three booking workflow scenarios: complete single-message structured booking, one-field-per-turn continuation, and partial structured booking followed by incremental replies.
- Revalidated Phase 4 chat coverage with `backend/.venv/bin/python -m pytest backend/tests/test_chat_entity_extractor.py backend/tests/test_knowledge_repository.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py -q` (`58 passed`).

## Prior Work

- Status: completed
- Task: improve Phase 4 Vector-less RAG retrieval quality and informational routing
- Completed on: 2026-07-02

## Outcome

- Knowledge documents now support additive retrieval metadata fields: `category`, `keywords`, `synonyms`, and `aliases`, while remaining backward compatible with existing Markdown and JSON sources.
- Deterministic retrieval scoring now weights title, alias, keyword, synonym, category, and body-text matches separately, and exact phrase matches now outrank weak incidental token overlap so targeted FAQ metadata beats unrelated partial matches.
- Added bundled FAQ knowledge for payment methods, insurance, and parking, and enriched the existing telemedicine, booking, cancellation, consultation-hours, and appointment-preparation documents with retrieval metadata.
- Fixed a narrow entity-extraction bug where substring matching inside words such as `methods` incorrectly produced `gender=Male`, which previously diverted payment-method questions into doctor search.
- Verified informational prompts now return knowledge-backed responses for online consultation, payment methods, appointment preparation, and consultation hours while booking workflows still route through the workflow engine unchanged.
- A focused manual API pass also confirmed casing, punctuation, pluralization, and multi-sentence online-consultation prompts resolve correctly, while unrelated `prescription refill online` prompts now fall back cleanly instead of misrouting to telemedicine.

## Prior Work

- Status: completed
- Task: fix Phase 4 Vector-less RAG routing so knowledge answers win before deterministic fallback
- Completed on: 2026-07-02

## Outcome

- `ConversationManager` now keeps workflow responses first, but returns a knowledge-backed response before the legacy deterministic chatbot for FAQ-style non-workflow turns.
- Knowledge-backed replies now route consistently with populated `knowledge_source` metadata instead of depending on the generic unknown fallback text.
- Retrieval token filtering was tightened so broad words such as `appointment`, `consultation`, `available`, and `support` do not hijack doctor search, availability, fee, or unrelated fallback flows.
- Added bundled FAQ knowledge documents for consultation hours, telemedicine, and appointment preparation so the documented manual-test examples resolve to real repository content.
- Added focused regression coverage for conversation-manager ordering plus repository and API verification of knowledge-hit, no-match fallback, and workflow-first behavior.

## Prior Work

- Status: completed
- Task: implement Phase 4.7 Manual Test Support for Vector-less RAG prototype
- Completed on: 2026-07-01

## Outcome

- A dedicated manual QA checklist now covers positive, negative, edge, regression, workflow, and existing chatbot scenarios for the Vector-less RAG prototype.
- The checklist is stored in `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-04-manual-test-checklist.md`.
- The phase-4 context files now point to the new manual test artifact for future validation work.

## Prior Work

- Status: completed
- Task: implement Phase 4.6 Frontend Mapping for Vector-less RAG chat metadata
- Completed on: 2026-07-01

## Prior Outcome

- The global AI widget now renders optional `knowledge_source` metadata on assistant text replies when the backend returns a knowledge-backed response.
- The existing workflow cards, appointment booking redirect, and structured response rendering remain unchanged.
- The chat response contract now stays backward compatible while exposing knowledge source identity, path, and matched-term context to the UI.

## Earlier Work

- Status: completed
- Task: implement Phase 4.5 Chat API Enhancement for Vector-less RAG
- Completed on: 2026-07-01

## Earlier Outcome

- Added optional `knowledge_source` metadata to `ChatResponse` so knowledge-backed replies can expose their source without breaking existing fields.
- Wired the deterministic knowledge retrieval service into `ConversationManager` as a read-only fallback when no workflow is active.
- Existing workflow-first routing still wins whenever a workflow is active or the workflow engine returns a response.
- The deterministic fallback remains intact and still handles queries that do not produce a knowledge match.
- Extended focused backend tests to cover knowledge-backed fallback routing, workflow exclusion, title ranking, content keyword matching, response metadata serialization, and default exclusion of deprecated documents.

## Required Files for This Task

- `backend/app/services/prompt_builder.py`
- `backend/tests/test_prompt_builder_service.py`
- `backend/app/services/__init__.py`
- `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`

## Notes

- The prompt builder and its new canonical `PromptContext` model are intentionally inactive in production and currently have no callers in the request path.
- No API, UI, workflow, retrieval, or database behavior changed in this phase.
