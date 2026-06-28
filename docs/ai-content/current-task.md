# Current Task

## Active Work

- Status: completed
- Task: introduce a Conversation Manager as the single orchestration entry point for chat while preserving deterministic assistant behavior
- Completed on: 2026-06-28

## Outcome

- Added `backend/app/services/conversation_manager.py` as the single orchestration entry point for all chat requests.
- Extended backend and frontend chat contracts with optional conversation metadata while keeping plain `message` requests valid.
- Preserved deterministic doctor search, availability, FAQ, booking-help, and cancellation-help behavior.
- Updated `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md` to reflect the new orchestration path.

## Required Files for This Task

- `backend/app/services/conversation_manager.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/api/chat.py`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/types/chat.ts`
- `backend/tests/test_chat_api.py`
- `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md`

## Notes

- No database schema changes were required.
- Existing `/api/chat` and `/api/v1/chat` behavior remains backward-compatible.
