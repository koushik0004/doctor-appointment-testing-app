# Current Task

## Active Work

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

- `frontend/components/layout/GlobalAiWidget.tsx`
- `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/types/chat.ts`
- `frontend/lib/ai-widget/types/message.ts`
- `backend/app/knowledge/documents.py`
- `backend/app/knowledge/loader.py`
- `backend/app/knowledge/repository.py`
- `backend/app/knowledge/retrieval.py`
- `backend/app/knowledge/sources/`
- `backend/app/schemas/chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/conversation_manager.py`
- `backend/tests/test_knowledge_repository.py`
- `backend/tests/test_chat_api.py`
- `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`

## Notes

- `ConversationManager` now consults `KnowledgeRetrievalService` only when no workflow is active.
- Knowledge-backed chat replies now carry optional `knowledge_source` metadata with document identity, source path, and deterministic match details.
- Token normalization is intentionally small and deterministic; it handles common suffixes such as plural `s` and `ing`, while filtering very broad stopwords to avoid stealing the generic fallback.
- Validate with `backend/.venv/bin/python -m pytest backend/tests/test_knowledge_repository.py backend/tests/test_chat_api.py backend/tests/test_chat_intent_detector.py` when changing this area.
