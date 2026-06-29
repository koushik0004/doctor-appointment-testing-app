# Phase 03 Workflow Engine Report

Date: 2026-06-29

## Files Added

- `backend/app/services/workflow_engine.py`
- `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-03-report.md`

## Files Modified

- `backend/app/repositories/appointment_repository.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/appointment_service.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/conversation_manager.py`
- `backend/tests/test_appointments_api.py`
- `backend/tests/test_chat_api.py`
- `backend/tests/test_chat_intent_detector.py`
- `frontend/components/layout/GlobalAiWidget.tsx`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/types/chat.ts`
- `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md`
- `docs/ai-content/current-task.md`
- `docs/ai-content/feature-map.md`
- `docs/ai-content/important-files.md`
- `docs/ai-content/session-context.md`
- `docs/ai-content/report-index.md`

## Workflow Architecture Summary

Phase 03 introduces `WorkflowEngine` as the request-scoped business execution layer under `ConversationManager`. The June 29 stabilization commits keep that architecture intact while correcting routing and multi-turn continuation behavior.

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
6. Stabilization work keeps an unfinished workflow active across incremental turns such as a bare time, bare patient name, or email-only reply.
7. Successful chat-driven bookings now reuse the existing booking store and redirect into `/appointments/confirmation` without introducing a separate chat-only confirmation screen.
8. Deterministic fallback doctor-detail routing now recognizes profile phrasing such as `Who is Dr. Sofia?` and partial `Dr. <first-name>` references when they uniquely match a doctor.

## Integration Points

- `backend/app/services/conversation_manager.py`
  - Workflow-first routing.
  - Preserves deterministic fallback.
  - Writes workflow state back into response conversation metadata and keeps unfinished workflows attached until completion or explicit switching.
- `backend/app/schemas/chat.py`
  - Adds workflow enums, draft state, result payload, and conversation context support.
- `backend/app/services/chat_intent_detector.py`
  - Broadens doctor-profile detection so `profile` and `Who is Dr. ...` phrasing route into doctor details instead of generic fallback.
- `backend/app/services/chat_service.py`
  - Broadens deterministic doctor matching for partial `Dr. <name>` fragments during fallback rendering.
- `frontend/lib/ai-widget/types/chat.ts`
  - Mirrors backend workflow metadata so the widget can round-trip request-scoped state.
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
  - Stores workflow metadata alongside assistant replies for future follow-up turns.
- `frontend/components/layout/GlobalAiWidget.tsx`
  - Intercepts completed booking workflow results, hydrates the existing booking store, and navigates to the standard confirmation route.

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
- Preserve `current_workflow` across turns until it reaches `COMPLETED`, even if the latest user reply is only a single missing field.
- Allow bare 2-4 token patient names only when the active workflow is already waiting for `patient_full_name`, reducing accidental capture from unrelated queries.
- Reuse the existing appointment confirmation page and Zustand booking state instead of introducing a dedicated workflow-result UI.

## Known Limitations

- Workflow state is not persisted outside the current conversation metadata loop.
- Booking data extraction is still heuristic. It now accepts bare patient-name follow-ups, but it still depends on recognizable date, time, email, phone, and doctor cues inside the current conversation loop.
- Cancellation and confirmation workflows require an appointment id or confirmation code.
- Frontend rendering remains text-first for in-progress workflows. Only successful booking completion has a dedicated handoff into the existing confirmation page.
- Workflow switching remains keyword-based (`start over`, `switch`, `something else`, `different question`) rather than stateful disambiguation.

## Stabilization Summary

### 1. Doctor profile response correctness

- Issue:
  Doctor-detail questions such as `Who is Dr. Sofia?` or partial-name prompts like `Tell me about Dr. Sofia` could miss the intended doctor-details path.
- Root Cause:
  Intent detection and fallback doctor matching were too narrow. The detector did not recognize profile phrasing, and the responder relied too heavily on full-name token matches.
- Implementation:
  Added `profile` and `Who is Dr. ...` recognition in `chat_intent_detector.py`, then expanded fallback name matching in `chat_service.py` to accept `Dr. <fragment>` token subsets.
- Files Changed:
  `backend/app/services/chat_intent_detector.py`, `backend/app/services/chat_service.py`, `backend/tests/test_chat_api.py`, `backend/tests/test_chat_intent_detector.py`
- Backward Compatibility:
  Additive only. Existing chat endpoints and response shapes remain unchanged.

### 2. Multi-turn booking continuation and automatic confirmation handoff

- Issue:
  Chat-led booking could lose workflow ownership across incremental turns, especially when the user replied with only a time, only a patient name, or only an email. Successful bookings also stayed inside the widget instead of continuing the normal confirmation flow.
- Root Cause:
  The workflow layer did not keep unfinished state attached strongly enough across all follow-up turns, and patient-name extraction expected explicit patterns such as `my name is ...`. The frontend also did not consume completed workflow metadata for navigation.
- Implementation:
  `ConversationManager` now preserves unfinished workflow state until completion. `WorkflowEngine` keeps booking workflows sticky across follow-ups, recognizes bare patient names when that field is missing, expands follow-up detection, and supports explicit workflow switching keywords. `GlobalAiWidget` now reads completed booking workflow metadata, populates the existing booking store, and redirects to `/appointments/confirmation`.
- Files Changed:
  `backend/app/services/conversation_manager.py`, `backend/app/services/workflow_engine.py`, `backend/tests/test_chat_api.py`, `frontend/components/layout/GlobalAiWidget.tsx`
- Backward Compatibility:
  Backward-compatible. `/api/chat` and `/api/v1/chat` contracts remain the same, workflow metadata stays additive, and the existing confirmation page continues to own final appointment presentation.

## Manual Verification Summary

- No new browser/manual verification artifact was committed in the analyzed commit range.
- Current HEAD verification on 2026-06-29:
  `backend/.venv/bin/pytest tests/test_chat_api.py tests/test_chat_intent_detector.py`
- Result:
  34 tests passed.
- Observed warning:
  Existing `StarletteDeprecationWarning` from `fastapi.testclient` / `starlette.testclient`.

## Suggested Next Phase

- Add a dedicated frontend workflow presentation layer for booking/cancellation state and missing-field prompts.
- Persist conversation and workflow state if multi-session continuation becomes a requirement.
- Replace heuristic field extraction with stricter structured capture once the product defines the exact chat-led booking UX.
- Add richer validation prompts for ambiguous doctor/time references instead of only returning missing field labels.
