# Current Task

## Active Work

- Status: completed
- Task: stabilize deterministic doctor-details routing for `Dr. <name>` and doctor profile queries in chat
- Completed on: 2026-06-28

## Outcome

- Fixed deterministic doctor-details routing for partial `Dr. <first-name>` queries such as `Tell me about Dr. Sofia`.
- Added doctor-profile intent coverage for prompts like `Who is Dr. Sofia?` and `Doctor profile of Dr. Sofia`.
- Kept the Conversation Manager and Workflow Engine architecture unchanged and preserved existing booking, cancellation, confirmation, and availability behavior.

## Required Files for This Task

- `backend/app/services/chat_service.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/tests/test_chat_api.py`
- `backend/tests/test_chat_intent_detector.py`

## Notes

- No database schema or business API changes were required.
- Existing `/api/chat` and `/api/v1/chat` contracts remain backward-compatible.
- The fix is limited to deterministic intent recognition and doctor-name matching for doctor-details queries.
