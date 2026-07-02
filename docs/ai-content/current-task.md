# Current Task

## Active Work

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

- `backend/app/services/chat_entity_extractor.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/services/conversation_manager.py`
- `backend/tests/test_chat_entity_extractor.py`
- `backend/tests/test_conversation_manager.py`
- `backend/tests/test_chat_api.py`

## Notes

- Keep Phase 3 workflow-first routing intact: `ConversationManager` should continue deferring to the workflow engine before knowledge retrieval or deterministic fallback.
- Booking regressions in this area are most likely to come from deterministic extraction or draft-merging behavior inside `WorkflowEngine`, not from the Phase 4 knowledge layer.
- Validate with `backend/.venv/bin/python -m pytest backend/tests/test_chat_entity_extractor.py backend/tests/test_knowledge_repository.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py -q` when changing this area.
