# Feature Report: FAQ Enhancements For Chat Window

## 1. Executive Summary

This enhancement refined the chatbot's FAQ behavior for booking, cancellation, and consultation-fee questions. The work was implemented across four feature-specific commits on June 26, 2026 and completed with aligned backend logic, frontend rendering, and targeted regression coverage.

The primary outcome is that the chatbot now handles common FAQ-style queries deterministically:

- Booking questions return clear in-app booking steps.
- Cancellation questions return a dedicated non-supported-by-chat guidance path.
- Fee questions without a doctor name ask for clarification instead of guessing.
- Fee questions no longer get misrouted into generic booking help.

The frontend was kept intentionally small. It now understands the new backend intent and renders ordered help steps using the existing appointment-help card instead of introducing a new UI pattern.

## 2. Business Objective

Improve the reliability of the chatbot for high-frequency support questions without introducing a real conversational workflow engine.

The target business outcomes were:

- Reduce user confusion for booking and cancellation FAQs.
- Make fee lookup behavior explicit and safe.
- Keep backend and frontend response contracts synchronized.
- Preserve the existing doctor search and availability search behavior while improving FAQ handling.

## 3. Problem Statement

Before this enhancement, FAQ-style questions had three practical problems:

1. Booking help was too generic.
2. Cancellation questions did not have a dedicated response path.
3. Fee-related questions could be misclassified because `consultation` overlapped with appointment-booking keywords.

That created UX and support issues:

- Users asking how to cancel could receive booking-oriented help.
- Users asking only for `consultation fee` could be routed to appointment help instead of being asked which doctor they meant.
- The frontend had no structured `help_steps` field to render guided instructions cleanly.

## 4. Solution Overview

The solution stayed fully deterministic and rule-based.

Backend changes:

- Added a new chat intent: `CANCEL_APPOINTMENT_HELP`.
- Added a new response field: `help_steps`.
- Reworked intent-detection keyword priority so cancellation and fee/detail questions are resolved before generic booking help.
- Changed booking-help output from free text to a step-based response.
- Added a dedicated cancellation-help response.
- Changed fee queries without a matched doctor to return a strict clarification prompt.

Frontend changes:

- Extended the typed chat contract with `CANCEL_APPOINTMENT_HELP` and `help_steps`.
- Reused the existing `AppointmentHelpMessage` component.
- Added ordered-step rendering to that component.
- Mapped both booking help and cancellation help into the same frontend content type with different titles.

## 5. Commit-by-Commit Analysis

### Commit 1

- Commit ID: `a22f4d8`
- Commit message: `Feature 9.1 | Fix Chat Window | Doctors Search BE/UI | initial prompt generation`
- Intent of the change:
  Define the implementation brief for the backend FAQ enhancement, frontend FAQ sync, and the implementation-report requirement.
- Files modified:
  - `docs/analysis/feature-8-chatbot-fix/1-faq-enhancement-report-generation-prompt.md`
  - `docs/prompts/backend/feature-8-chatbot-fix/1-faq-enhancement-support-prompt.md`
  - `docs/prompts/frontend/feature-8-chatbot-fix/1-faq-frontend-enhancement-prompt.md`
- Technical impact:
  Established explicit scope boundaries, including which backend files could change, what frontend behavior must stay untouched, and what exact responses were required.
- Business impact:
  Reduced ambiguity before implementation and kept the feature focused on FAQ correctness rather than feature creep.

### Commit 2

- Commit ID: `a7f40b0`
- Commit message: `Feature 9.1 | Fix Chat Window | Doctors Search BE/UI | FAQ BE API enhancements`
- Intent of the change:
  Implement the backend behavior for booking help, cancellation help, and safer fee clarification.
- Files modified:
  - `backend/app/schemas/chat.py`
  - `backend/app/services/chat_intent_detector.py`
  - `backend/app/services/chat_service.py`
  - `backend/tests/test_chat_api.py`
  - `backend/tests/test_chat_intent_detector.py`
- Technical impact:
  Added a new intent, expanded the response contract, changed keyword routing order, introduced step-based help responses, and added tests for the new FAQ flows.
- Business impact:
  The API now answers common support questions in a stable and predictable way, reducing incorrect guidance and avoiding unsupported in-chat cancellation promises.

### Commit 3

- Commit ID: `755eb1f`
- Commit message: `Feature 9.1 | Fix Chat Window | Doctors Search BE/UI | FAQ FE setup enhancements`
- Intent of the change:
  Sync the widget UI with the updated backend FAQ payloads.
- Files modified:
  - `frontend/lib/ai-widget/components/AppointmentHelpMessage.tsx`
  - `frontend/lib/ai-widget/services/chat-response-mapper.ts`
  - `frontend/lib/ai-widget/services/mock-service.ts`
  - `frontend/lib/ai-widget/types/chat.ts`
  - `frontend/lib/ai-widget/types/message.ts`
- Technical impact:
  Added typed support for the new intent and help steps, updated response mapping, and allowed the existing help card to render ordered instructions.
- Business impact:
  Users now see clearer, more actionable FAQ guidance in the widget without any UI/backend mismatch.

### Commit 4

- Commit ID: `afb4da4`
- Commit message: `Feature 9.1 | Fix Chat Window | Doctors Search BE/UI | initial prompt generation`
- Intent of the change:
  Narrow the reporting requirement into a dedicated analysis prompt after implementation work had started.
- Files modified:
  - `docs/analysis/feature-8-chatbot-fix/1-faq-enhancement-report-generation-prompt.md`
- Technical impact:
  Added explicit reporting expectations, including commit-level analysis and API contract documentation.
- Business impact:
  Improves maintainability by requiring future-facing implementation documentation for this enhancement.

## 6. Backend Changes

### `backend/app/schemas/chat.py`

- Why it changed:
  The response schema needed to represent a new FAQ intent and structured guidance steps.
- What changed:
  - Added `CANCEL_APPOINTMENT_HELP` to `ChatIntent`.
  - Added `help_steps: list[str]` to `ChatResponse`.
- Business purpose:
  Allow the API to distinguish cancellation guidance from booking guidance and provide UI-ready step sequences.
- Important implementation details:
  The legacy `response` field remains synchronized from `message`, preserving backward compatibility for older consumers.

### `backend/app/services/chat_intent_detector.py`

- Why it changed:
  FAQ routing was too coarse and incorrectly overlapped booking and fee language.
- What changed:
  - Split booking and cancellation keywords.
  - Expanded doctor-detail keywords to better catch fee and charge phrasing.
  - Changed intent priority order to:
    1. cancellation
    2. doctor details / fee
    3. booking help
    4. availability
    5. specialization
- Business purpose:
  Make the bot answer the user's actual support question instead of the first loosely related keyword match.
- Important implementation details:
  This ordering fixes the key regression where `consultation fee` was previously captured by booking logic because `consultation` appeared in appointment-related keywords.

### `backend/app/services/chat_service.py`

- Why it changed:
  The responder needed to emit structured help steps and a dedicated cancellation response.
- What changed:
  - `_build_response()` now accepts `help_steps`.
  - `_respond_with_appointment_help()` now returns an explicit five-step booking guide.
  - Added `_respond_with_cancellation_help()`.
  - `_respond_with_doctor_details()` now returns exact clarification when no doctor match is found.
  - `generate()` now handles `CANCEL_APPOINTMENT_HELP`.
- Business purpose:
  Return safe, explicit guidance for support-style questions while keeping unsupported operations outside the chatbot.
- Important implementation details:
  The fee clarification intentionally does not guess or return a list of candidate doctors for generic fee questions. That reduces ambiguity and keeps the prompt focused on identifying one doctor.

### `backend/tests/test_chat_intent_detector.py`

- Why it changed:
  Intent routing was the highest-risk part of this enhancement.
- What changed:
  Added coverage for:
  - booking-process help
  - cancellation help
  - fee query without doctor name
- Business purpose:
  Protect the deterministic FAQ-routing contract against future keyword regressions.
- Important implementation details:
  The tests validate classification only, which isolates keyword and priority behavior from API orchestration concerns.

### `backend/tests/test_chat_api.py`

- Why it changed:
  The endpoint contract changed and needed end-to-end verification.
- What changed:
  Added or updated assertions for:
  - booking help message and `help_steps`
  - cancellation help message and `help_steps`
  - clarification for generic fee questions
- Business purpose:
  Ensure the public chat API returns the exact payload shape and content the frontend expects.
- Important implementation details:
  These tests cover message text, intent values, empty `data` behavior, and structured `help_steps`.

## 7. Frontend Changes

### `frontend/lib/ai-widget/types/chat.ts`

- Why it changed:
  The frontend payload type needed to match the backend contract.
- What changed:
  - Added `CANCEL_APPOINTMENT_HELP` to `AiWidgetChatIntent`.
  - Added optional `help_steps` to `AiWidgetChatResponsePayload`.
- UI behavior:
  The UI can now understand a cancellation-help reply and step-based help payloads without type gaps.
- Integration with backend:
  Mirrors the updated `ChatResponse` schema from the backend.

### `frontend/lib/ai-widget/types/message.ts`

- Why it changed:
  The internal widget message model needed to carry ordered help steps.
- What changed:
  Added optional `steps` to `AiWidgetAppointmentHelpMessageContent`.
- UI behavior:
  The help card can render a sequence of instructions instead of plain prose only.
- Integration with backend:
  Receives the mapped `help_steps` values from the backend payload.

### `frontend/lib/ai-widget/services/chat-response-mapper.ts`

- Why it changed:
  The mapper is the boundary between backend payloads and widget content types.
- What changed:
  - Appointment-help content now includes `steps`.
  - `CANCEL_APPOINTMENT_HELP` maps to the same content type as `APPOINTMENT_HELP`.
  - The title switches between `Appointment help` and `Cancellation help`.
- UI behavior:
  The widget shows the same card shell for both help cases, but the label and step list change based on the backend intent.
- Integration with backend:
  Consumes `intent`, `message`, and `help_steps` directly from the backend response.

### `frontend/lib/ai-widget/components/AppointmentHelpMessage.tsx`

- Why it changed:
  The existing help card needed to visualize step-based guidance.
- What changed:
  Added ordered-list rendering when `content.steps` exists.
- UI behavior:
  Booking and cancellation help now appear as structured, readable instructions rather than a single paragraph.
- Integration with backend:
  Renders the mapped `steps` array produced from backend `help_steps`.

### `frontend/lib/ai-widget/services/mock-service.ts`

- Why it changed:
  Local widget development needs mock payloads that reflect real backend behavior.
- What changed:
  - Updated booking-help mock response to include the new message and steps.
  - Added a dedicated cancellation-help mock response.
  - Ensured cancellation matching runs before generic booking matching.
- UI behavior:
  Developers can exercise the FAQ cards without a live backend.
- Integration with backend:
  Mirrors the final API contract closely enough to prevent frontend-only drift.

### `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`

- Why it did not change:
  The existing renderer already delegates `appointment_help` content to `AppointmentHelpMessage`.
- UI behavior:
  Both booking help and cancellation help now flow through the same rendering path after mapper normalization.
- Integration with backend:
  No direct backend contract change was required in this component.

## 8. API Contract Changes

### New Intent

`CANCEL_APPOINTMENT_HELP`

- Purpose:
  Distinguish cancellation guidance from generic appointment help.

### Modified Response Contract

`ChatResponse` now includes:

```json
{
  "intent": "APPOINTMENT_HELP | CANCEL_APPOINTMENT_HELP | ...",
  "message": "string",
  "data": [],
  "search_filters": {},
  "help_steps": ["string"],
  "response": "string"
}
```

For FAQ-style intents, `search_filters` may still be present because the response passes through the shared extraction pipeline. Consumers should treat `intent`, `message`, and `help_steps` as the primary contract for booking-help and cancellation-help replies.

### Request Example

```http
POST /api/chat
Content-Type: application/json

{
  "message": "How do I cancel my booking?"
}
```

### Response Example: Cancellation Help

```json
{
  "intent": "CANCEL_APPOINTMENT_HELP",
  "message": "Appointment cancellation is not supported through AI chat. Please use the app's existing cancellation flow or contact support for help.",
  "data": [],
  "search_filters": {},
  "help_steps": [
    "Open the existing cancellation flow in the app.",
    "Find your booked appointment details.",
    "Follow the cancellation instructions shown there.",
    "If you cannot access the booking, contact support."
  ],
  "response": "Appointment cancellation is not supported through AI chat. Please use the app's existing cancellation flow or contact support for help."
}
```

### Response Example: Fee Clarification

```json
{
  "intent": "SHOW_DOCTOR_DETAILS",
  "message": "Which doctor's consultation fee would you like to know?",
  "data": [],
  "search_filters": {
    "specialization": null,
    "gender": null,
    "minimum_fee": null,
    "maximum_fee": null,
    "date": null,
    "time_preference": null,
    "clinic_location": null
  },
  "help_steps": [],
  "response": "Which doctor's consultation fee would you like to know?"
}
```

## 9. Chat Behaviour Improvements

### Example 1: `How to book appointment?`

- Before:
  `I can help you book an appointment. Share a doctor, preferred date, time, and appointment type.`
- After:
  `Here is how to book an appointment in the app.`
  With steps:
  1. Choose a doctor.
  2. Select an available date.
  3. Choose a time slot.
  4. Enter patient details.
  5. Confirm the appointment.

### Example 2: `How to cancel appointment?`

- Before:
  Routed through generic appointment-help logic because cancellation language was not separated clearly.
- After:
  `Appointment cancellation is not supported through AI chat. Please use the app's existing cancellation flow or contact support for help.`
  With steps:
  1. Open the existing cancellation flow in the app.
  2. Find your booked appointment details.
  3. Follow the cancellation instructions shown there.
  4. If you cannot access the booking, contact support.

### Example 3: `How much consultation fee?`

- Before:
  Could be misclassified as booking help because `consultation` overlapped with booking keywords and was evaluated earlier.
- After:
  `Which doctor's consultation fee would you like to know?`

### Example 4: `Fee of Dr Elena`

- Before:
  Unclear and inconsistent depending on keyword routing and doctor matching.
- After:
  `Which doctor's consultation fee would you like to know?`

This is intentional. The system does not guess an unknown doctor identity.

## 10. Testing

### New automated tests

- `backend/tests/test_chat_intent_detector.py`
  - booking process intent
  - cancellation help intent
  - fee query without doctor name
- `backend/tests/test_chat_api.py`
  - booking help payload including `help_steps`
  - cancellation help payload including `help_steps`
  - fee clarification payload

### Existing regression tests

The targeted backend suite still covers:

- specialization search responses
- filtered availability search
- doctor-details responses for known doctors
- time-based availability routing
- greeting handling
- validation for blank messages
- fallback response behavior

### Validation performed

- Backend:
  `./.venv/bin/pytest tests/test_chat_intent_detector.py tests/test_chat_api.py`
  Result: `23 passed`
- Frontend:
  `npm run lint`
  Result: no ESLint warnings or errors
- Manual runtime verification:
  Confirmed the live responses for:
  - `How to book appointment?`
  - `How to cancel appointment?`
  - `How much consultation fee?`
  - `Fee of Dr Elena`

## 11. Files Modified

### Backend

- `backend/app/schemas/chat.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/app/services/chat_service.py`

### Frontend

- `frontend/lib/ai-widget/types/chat.ts`
- `frontend/lib/ai-widget/types/message.ts`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/components/AppointmentHelpMessage.tsx`
- `frontend/lib/ai-widget/services/mock-service.ts`

### Tests

- `backend/tests/test_chat_intent_detector.py`
- `backend/tests/test_chat_api.py`

### Documentation

- `docs/prompts/backend/feature-8-chatbot-fix/1-faq-enhancement-support-prompt.md`
- `docs/prompts/frontend/feature-8-chatbot-fix/1-faq-frontend-enhancement-prompt.md`
- `docs/analysis/feature-8-chatbot-fix/1-faq-enhancement-report-generation-prompt.md`
- `docs/reports/feature-8-chatbot-fix/report-faq-enhancements.md`

## 12. Current Capabilities

The chatbot can now:

- show doctors by specialization
- show available doctors and slots
- answer doctor fee/details questions for matched doctors
- ask for clarification when a fee question does not identify a doctor
- explain the booking flow with ordered in-app steps
- explain how to use the existing cancellation flow
- return structured data the frontend can render as cards, summaries, and help content

## 13. Known Limitations

The following are intentionally not implemented in this phase:

- conversation memory
- multi-turn workflow
- appointment booking through chat
- cancellation workflow
- vector-less RAG
- vector DB
- LLM

This remains a deterministic rule-based support layer, not a transactional assistant.

## 14. Recommended Next Step

Recommended next phase:

**Vector-less RAG + Appointment Workflow Engine**

That phase should focus on two gaps:

1. Retrieval of richer support knowledge beyond hardcoded FAQ rules.
2. A controlled workflow layer that can guide users through appointment actions without pretending that the current chat endpoint performs those actions directly.
