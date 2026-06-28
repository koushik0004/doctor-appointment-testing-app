# Phase 03 Workflow Engine Report

Date: 2026-06-28

## Files Added

- `backend/app/services/workflow_engine.py`
- `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-03-report.md`

## Files Modified

- `backend/app/repositories/appointment_repository.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/appointment_service.py`
- `backend/app/services/conversation_manager.py`
- `backend/tests/test_appointments_api.py`
- `backend/tests/test_chat_api.py`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/types/chat.ts`
- `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/session-context.md`
- `docs/ai-content/report-index.md`

## Workflow Architecture Summary

Phase 03 introduces `WorkflowEngine` as the request-scoped business execution layer under `ConversationManager`.

Flow:

1. `ConversationManager` builds normalized conversation context and merged search filters.
2. `WorkflowEngine` decides whether the message should:
   - continue an active workflow
   - start a booking workflow
   - start a cancellation workflow
   - start a confirmation lookup workflow
3. If required workflow inputs are missing, the engine returns structured `missing_fields` plus a persisted draft in `conversation.current_workflow`.
4. If all required inputs are present, the engine calls existing appointment business services and returns a structured workflow result.
5. If no workflow applies, `ConversationManager` falls back to the existing deterministic responder unchanged.

## Integration Points

- `backend/app/services/conversation_manager.py`
  - Workflow-first routing.
  - Preserves deterministic fallback.
  - Writes workflow state back into response conversation metadata.
- `backend/app/schemas/chat.py`
  - Adds workflow enums, draft state, result payload, and conversation context support.
- `frontend/lib/ai-widget/types/chat.ts`
  - Mirrors backend workflow metadata so the widget can round-trip request-scoped state.
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
  - Stores workflow metadata alongside assistant replies for future follow-up turns.

## Business APIs Reused

- `create_appointment_booking()`
  - Executes the booking workflow.
- `cancel_appointment_booking()`
  - Executes the cancellation workflow.
- `get_appointment_confirmation_by_reference()`
  - Executes confirmation lookup by appointment id or confirmation code.
- `list_doctors()`
  - Resolves doctor identity when workflow messages reference a doctor by name.

## Design Decisions

- Keep workflow state request-scoped inside chat metadata; no database schema changes.
- Keep chat endpoints unchanged and backward-compatible.
- Keep workflow detection heuristic and deterministic; no LLM or prompt builder.
- Keep actual business mutations inside `appointment_service.py`.
- Default booking workflow appointment type to `IN_PERSON` unless the message explicitly asks for telemedicine.

## Known Limitations

- Workflow state is not persisted outside the current conversation metadata loop.
- Booking data extraction is intentionally simple and depends on explicit user phrasing for fields like patient name, email, phone, and exact start time.
- Cancellation and confirmation workflows require an appointment id or confirmation code.
- Frontend rendering still treats workflow replies as text-first responses; no dedicated workflow UI has been introduced.

## Suggested Next Phase

- Add a dedicated frontend workflow presentation layer for booking/cancellation state and missing-field prompts.
- Persist conversation and workflow state if multi-session continuation becomes a requirement.
- Replace heuristic field extraction with stricter structured capture once the product defines the exact chat-led booking UX.
- Add richer validation prompts for ambiguous doctor/time references instead of only returning missing field labels.
