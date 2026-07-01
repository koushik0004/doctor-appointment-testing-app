# Current Task

## Active Work

- Status: completed
- Task: implement Phase 4.5 Chat API Enhancement for Vector-less RAG
- Completed on: 2026-07-01

## Outcome

- Added optional `knowledge_source` metadata to `ChatResponse` so knowledge-backed replies can expose their source without breaking existing fields.
- Wired the deterministic knowledge retrieval service into `ConversationManager` as a read-only fallback when no workflow is active.
- Existing workflow-first routing still wins whenever a workflow is active or the workflow engine returns a response.
- The deterministic fallback remains intact and still handles queries that do not produce a knowledge match.
- Extended focused backend tests to cover knowledge-backed fallback routing, workflow exclusion, title ranking, content keyword matching, response metadata serialization, and default exclusion of deprecated documents.

## Required Files for This Task

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
