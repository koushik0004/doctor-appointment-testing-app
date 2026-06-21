# Feature Report: AI Chat Phase 2

## Executive Summary

This feature upgraded the doctor appointment assistant from a generic chat widget into a structured intent-recognition experience that can answer doctor discovery questions, surface availability, show doctor detail cards, and hand the user off to the appointment booking page.

Business value:

- Users can move from a chat question to a bookable doctor view without re-entering the doctor context.
- The assistant now returns structured UI payloads instead of plain text, which makes the interaction more actionable.
- The implementation is deterministic and testable, so behavior is easier to validate than an LLM-driven chat flow.

Major outcomes:

- Backend intent detection now maps user messages to a small, explicit set of chat intents.
- Backend responses now carry typed doctor cards and availability cards.
- Frontend chat rendering now supports structured cards and direct booking navigation.
- Appointment links now preserve the selected doctor through `doctorId` query parameters.

## Feature Overview

### Problem Statement

The assistant initially needed to do more than answer text queries. It had to help users discover doctors, inspect availability, and move directly into the booking flow. Plain text answers were not enough because users still had to search for the doctor again on the booking page.

### Expected Behavior

- A user asks for doctors by specialization.
- A user asks who is available on a given day.
- A user asks for a doctor’s fee or details.
- The assistant returns structured data that the UI can render as cards.
- Each bookable doctor card includes a booking action.
- Clicking the booking action should route to the booking page with the doctor already selected.

### Final Implemented Behavior

- The backend recognizes intents for specialization lookup, availability lookup, doctor details, and appointment help.
- The API returns a normalized `intent`, `message`, `data`, and legacy `response` field.
- The frontend maps structured payloads into doctor cards, availability cards, and appointment help messages.
- Doctor cards and availability cards both expose a booking CTA.
- The CTA routes to `/appointments?doctorId=<id>`, which the booking page consumes to preselect the doctor.

## Architecture Overview

The implementation keeps the assistant deterministic and splits responsibilities cleanly across the stack.

Frontend
→ API client
→ FastAPI chat route
→ chat service
→ intent detector
→ doctor / availability services
→ SQLite-backed data

### Request Flow

```text
User message
  → Chat widget composer
  → POST /api/chat or /api/v1/chat
  → FastAPI chat router
  → create_chat_response()
  → detect_chat_intent()
  → list_doctors() / get_available_slots()
  → ChatResponse payload
  → frontend response mapper
  → MessageContentRenderer
  → DoctorCardMessage / AvailabilityMessage
  → Book Appointment button
  → /appointments?doctorId=<id>
  → appointments page loads doctor + availability
```

### Booking Flow

```text
Chat card
  → Book Appointment
  → buildAppointmentBookingUrl(doctorId)
  → router.push("/appointments?doctorId=...")
  → frontend/app/appointments/page.tsx
  → doctor lookup + availability lookup
  → booking form and slot selection
```

### Current Codebase State

- No database schema or migration changes were required.
- The feature reuses the existing SQLite data and service layer.
- Backend behavior is deterministic and keyword-based rather than LLM-based.
- Frontend rendering is fully componentized inside `frontend/lib/ai-widget`.
- The booking page already accepts a `doctorId` query parameter, so the chat widget only needed to supply the correct navigation target.

## Commit Analysis

### Commit 1

Commit: `8672238`

Purpose:

- Added the implementation prompts that defined the backend intelligence layer and the structured frontend rendering expectations.

Files changed:

- `docs/prompts/backend/feature-6-intent-recognition/1-ai-chat-intelligence-layer-prompt.md`
- `docs/prompts/frontend/feature-6-intent-recognition/1-structured-chat-rendering-prompt.md`

Impact:

- Established the feature contract before code landed.
- Clarified that the backend should produce structured intents and that the frontend should render those intents as UI cards.

### Commit 2

Commit: `38c0d95`

Purpose:

- Added the backend chat intelligence layer.

Files changed:

- `backend/app/schemas/chat.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/app/services/chat_service.py`
- `backend/tests/test_chat_api.py`
- `backend/tests/test_chat_intent_detector.py`

Impact:

- Introduced typed chat intents and structured response schemas.
- Added deterministic intent detection for specialization, availability, doctor details, and appointment help.
- Wired the chat service to doctor and availability lookup services.
- Added test coverage for the main query types and fallback behavior.

### Commit 3

Commit: `42bea09`

Purpose:

- Built the frontend structured chat rendering layer.

Files changed:

- `frontend/lib/ai-widget/components/AiWidgetRoot.tsx`
- `frontend/lib/ai-widget/components/AppointmentHelpMessage.tsx`
- `frontend/lib/ai-widget/components/AvailabilityMessage.tsx`
- `frontend/lib/ai-widget/components/ChatWindow.tsx`
- `frontend/lib/ai-widget/components/DoctorCardMessage.tsx`
- `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`
- `frontend/lib/ai-widget/components/MessageList.tsx`
- `frontend/lib/ai-widget/core/state.ts`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/services/mock-service.ts`
- `frontend/lib/ai-widget/types/chat.ts`
- `frontend/lib/ai-widget/types/index.ts`
- `frontend/lib/ai-widget/types/message.ts`
- `frontend/lib/ai-widget/types/widget.ts`

Impact:

- Added support for rendering structured doctor cards and availability cards.
- Added message mapping from backend payloads into frontend widget content.
- Kept the widget service abstraction so the assistant can swap between mock and API-backed behavior.

### Commit 4

Commit: `fcaea44`

Purpose:

- Updated the implementation prompt for the booking action refinement.

Files changed:

- `docs/prompts/frontend/feature-6-intent-recognition/2-fix-book-appointment-action-prompt.md`

Impact:

- Captured the final UX requirement that booking actions must not be decorative.
- Defined the expectation that the card CTA should redirect the user into the actual booking flow.

### Commit 5

Commit: `650b9a5`

Purpose:

- Connected structured chat cards to the appointment booking flow.

Files changed:

- `frontend/lib/ai-widget/components/AvailabilityMessage.tsx`
- `frontend/lib/ai-widget/components/DoctorCardMessage.tsx`
- `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`
- `frontend/lib/ai-widget/services/appointment-navigation.ts`
- `frontend/lib/ai-widget/services/index.ts`

Impact:

- Added a shared booking URL helper for the chat widget.
- Made the doctor card booking button actually navigate.
- Added a booking button to availability cards so users can move from availability discovery into booking.
- Ensured both card types pass the selected doctor into the appointment page.

## Frontend Changes

### `frontend/lib/ai-widget/components/DoctorCardMessage.tsx`

Purpose:

- Render doctor information in a structured assistant card.

Key changes:

- Added a booking CTA at the bottom of the card.
- Wired the CTA to `router.push()` using the doctor ID.
- Preserved an optional callback hook for parent-level analytics or side effects.

Code example:

```tsx
function handleBookAppointment() {
  if (!isBookableDoctor) {
    return;
  }

  onBookAppointment?.(doctor.doctorId);
  router.push(buildAppointmentBookingUrl(doctor.doctorId));
}
```

Explain:

The card now performs real navigation instead of acting like a dead button.

### `frontend/lib/ai-widget/components/AvailabilityMessage.tsx`

Purpose:

- Render availability results as actionable cards.

Key changes:

- Added a booking button to availability results.
- Routed that button to the same appointment booking URL helper.
- Disabled the CTA when the response does not contain a valid doctor ID.

Code example:

```tsx
<button
  type="button"
  onClick={handleBookAppointment}
  disabled={!isBookableDoctor}
>
  Book Appointment
</button>
```

Explain:

Availability cards now support the same booking handoff as doctor cards.

### `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`

Purpose:

- Route each structured message type to the correct UI component.

Key changes:

- Added pass-through support for `onBookAppointment`.
- Rendered doctor lists and availability lists through dedicated content wrappers.

Code example:

```tsx
if (message.content.type === "availability") {
  return (
    <article className={cn(assistantShellClasses, "max-w-[92%]")}>
      <AvailabilityContent
        content={message.content}
        onBookAppointment={onBookAppointment}
      />
    </article>
  );
}
```

Explain:

This is the bridge between backend intent payloads and visible assistant UI.

### `frontend/lib/ai-widget/services/appointment-navigation.ts`

Purpose:

- Centralize booking page URL generation.

Key changes:

- Added a helper that encodes the selected doctor ID into the booking URL.

Code example:

```tsx
export function buildAppointmentBookingUrl(doctorId: number) {
  return `/appointments?doctorId=${encodeURIComponent(String(doctorId))}`;
}
```

Explain:

Using one helper avoids duplicating the booking URL logic across card components.

### `frontend/app/appointments/page.tsx`

Purpose:

- Load the appointment page from the selected doctor context.

Key changes:

- Reads `doctorId` from the query string.
- Uses that ID to fetch doctor and availability data.
- Restores selected booking state from the store when available.

Code example:

```tsx
const searchDoctorId = searchParams.get("doctorId");
const effectiveDoctorId =
  searchDoctorId ??
  (storedDoctorId && /^\d+$/.test(storedDoctorId) ? storedDoctorId : null);
```

Explain:

The booking page can open directly from chat and still resolve the correct doctor.

### `frontend/components/doctors/BookingSummary.tsx`

Purpose:

- Link the standard doctor booking UI into the same appointment flow.

Key changes:

- The “Proceed to Booking” link already uses the `doctorId` query parameter.

Code example:

```tsx
<Link
  href={doctor ? `/appointments?doctorId=${doctor.backendId}` : "/appointments"}
>
  Proceed to Booking
</Link>
```

Explain:

The chat widget now matches the app’s existing booking navigation pattern.

## Backend Changes

### `backend/app/schemas/chat.py`

Purpose:

- Define the structured contract for chat requests and responses.

Key changes:

- Added a typed `ChatIntent` enum.
- Added `ChatDoctorCard` and `ChatAvailabilityCard` response models.
- Preserved a legacy `response` field that mirrors `message`.

Code example:

```python
class ChatResponse(BaseModel):
    intent: ChatIntent
    message: str
    data: list[ChatDoctorCard | ChatAvailabilityCard] = Field(default_factory=list)
    response: str = ""
```

Explain:

This schema lets the frontend render content deterministically from the backend payload.

### `backend/app/services/chat_intent_detector.py`

Purpose:

- Detect the user’s intent from plain text input.

Key changes:

- Added specialty aliases.
- Added keyword sets for appointment help, availability, and doctor details.
- Added simple date extraction for today, tomorrow, and day after tomorrow.

Code example:

```python
if _contains_keyword(normalized_message, AVAILABILITY_KEYWORDS):
    return ChatIntentMatch(
        intent=ChatIntent.SHOW_AVAILABLE_DOCTORS,
        specialty=specialty,
        target_date=target_date or (date.today() + timedelta(days=1)),
    )
```

Explain:

The assistant uses deterministic rules instead of model-generated intent classification.

### `backend/app/services/chat_service.py`

Purpose:

- Resolve intents into database-backed structured answers.

Key changes:

- Converts doctors into chat doctor cards.
- Collects availability slots for the selected date.
- Formats consultation fee ranges and fallback messages.
- Chooses the response branch from the detected intent.

Code example:

```python
if intent_match.intent == ChatIntent.SHOW_DOCTOR_DETAILS:
    return self._respond_with_doctor_details(message, doctors)
```

Explain:

The service layer is the orchestration point between intent detection and the existing doctor data services.

### `backend/app/api/chat.py`

Purpose:

- Expose the chat service through FastAPI routes.

Key changes:

- Added `/chat` and `/v1/chat` endpoints.
- Wrapped service failures in the project’s standardized chat error handler.

Code example:

```python
@router.post("", response_model=ChatResponse)
def create_chat_reply(
    request: ChatRequest,
    session: Session = Depends(get_db),
) -> ChatResponse:
    return _handle_chat(request, session)
```

Explain:

The route layer stays thin and delegates business logic to the service layer.

## API Changes

### `POST /api/chat`

Request:

```json
{
  "message": "Show cardiologists"
}
```

Response:

```json
{
  "intent": "SHOW_DOCTORS_BY_SPECIALIZATION",
  "message": "Found 2 doctors for Cardiology.",
  "data": [],
  "response": "Found 2 doctors for Cardiology."
}
```

### `POST /api/v1/chat`

- Same request and response contract as `/api/chat`.
- Added for versioned compatibility.

### Response Contract Notes

- `intent` tells the frontend which UI renderer to use.
- `message` is the human-readable summary.
- `data` carries typed doctor or availability cards.
- `response` mirrors `message` for legacy compatibility.

## Chat Widget Changes

- The widget now receives structured backend payloads through `createApiAiWidgetService()`.
- `chat-response-mapper.ts` converts backend card data into frontend card content.
- `MessageContentRenderer.tsx` decides whether a message is plain text, a doctor list, an availability list, or appointment help.
- `AiWidgetRoot` passes an optional booking callback down the component tree.
- `MessageList` and `ChatWindow` keep rendering responsibilities separate from chat transport logic.

## Navigation Flow

1. The assistant renders a doctor card or availability card.
2. The user clicks `Book Appointment`.
3. The card builds `/appointments?doctorId=<id>`.
4. Next.js navigates to the appointment page.
5. The appointment page reads `doctorId`.
6. The page fetches the doctor record and availability data.
7. The booking form opens with the correct doctor already selected.

## Data Flow

```text
User message
  → API client
  → chat route
  → chat service
  → intent detector
  → doctor service / availability service
  → SQLite
  → structured ChatResponse
  → frontend response mapper
  → chat widget renderer
```

This flow keeps data access in the backend and presentation logic in the frontend.

## Technical Decisions

- Used deterministic intent detection instead of an LLM to keep the feature fast, predictable, and easy to test.
- Returned structured response objects instead of plain strings so the frontend can render richer UI.
- Kept the booking URL helper in one place to avoid path drift between chat cards and the booking page.
- Reused the existing appointment page rather than creating a separate booking route for chat.
- Avoided database schema changes because the feature only needed existing doctor and availability data.

## Code Examples

### 1. Intent detection

```python
if _contains_keyword(normalized_message, DOCTOR_DETAILS_KEYWORDS):
    return ChatIntentMatch(
        intent=ChatIntent.SHOW_DOCTOR_DETAILS,
        specialty=specialty,
        target_date=target_date,
    )
```

Why it matters:

This is the entry point for all structured responses.

### 2. Response schema

```python
class ChatResponse(BaseModel):
    intent: ChatIntent
    message: str
    data: list[ChatDoctorCard | ChatAvailabilityCard] = Field(default_factory=list)
```

Why it matters:

The frontend needs both a message and typed data to render cards.

### 3. Doctor card mapping

```ts
function mapDoctorCard(card: AiWidgetChatDoctorCard): AiWidgetDoctorCardContent {
  return {
    doctorId: card.doctor_id,
    doctorName: card.doctor_name,
    specialization: card.specialty,
    consultationFeeMin: card.consultation_fee_min,
    consultationFeeMax: card.consultation_fee_max,
    nextAvailableSlot: card.next_available_slot,
    clinicName: card.clinic_name,
    location: card.location,
  };
}
```

Why it matters:

Backend snake_case data becomes frontend camelCase UI data.

### 4. Content routing

```tsx
switch (payload.intent) {
  case "SHOW_DOCTORS_BY_SPECIALIZATION":
  case "SHOW_DOCTOR_DETAILS":
    return createDoctorListContent(payload);
```

Why it matters:

The intent controls which assistant card component is rendered.

### 5. Booking helper

```tsx
export function buildAppointmentBookingUrl(doctorId: number) {
  return `/appointments?doctorId=${encodeURIComponent(String(doctorId))}`;
}
```

Why it matters:

This keeps booking navigation consistent across all card components.

### 6. Booking CTA

```tsx
<button type="button" onClick={handleBookAppointment}>
  Book Appointment
</button>
```

Why it matters:

The assistant now supports a real booking action, not just an informational card.

### 7. Appointment page handoff

```tsx
const searchDoctorId = searchParams.get("doctorId");
```

Why it matters:

The booking page can reconstruct the selected doctor from the chat redirect.

## Files Modified

### Frontend

- `frontend/lib/ai-widget/components/AiWidgetRoot.tsx`
- `frontend/lib/ai-widget/components/AppointmentHelpMessage.tsx`
- `frontend/lib/ai-widget/components/AvailabilityMessage.tsx`
- `frontend/lib/ai-widget/components/ChatWindow.tsx`
- `frontend/lib/ai-widget/components/DoctorCardMessage.tsx`
- `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`
- `frontend/lib/ai-widget/components/MessageList.tsx`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/services/appointment-navigation.ts`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/services/index.ts`
- `frontend/lib/ai-widget/services/mock-service.ts`
- `frontend/lib/ai-widget/types/chat.ts`
- `frontend/lib/ai-widget/types/index.ts`
- `frontend/lib/ai-widget/types/message.ts`
- `frontend/lib/ai-widget/types/widget.ts`
- `frontend/app/appointments/page.tsx`
- `frontend/components/doctors/BookingSummary.tsx`

### Backend

- `backend/app/api/chat.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/app/services/chat_service.py`
- `backend/tests/test_chat_api.py`
- `backend/tests/test_chat_intent_detector.py`

### Shared / Docs

- `docs/prompts/backend/feature-6-intent-recognition/1-ai-chat-intelligence-layer-prompt.md`
- `docs/prompts/frontend/feature-6-intent-recognition/1-structured-chat-rendering-prompt.md`
- `docs/prompts/frontend/feature-6-intent-recognition/2-fix-book-appointment-action-prompt.md`

## Testing Performed

- Automated backend tests cover specialty lookup, availability lookup, doctor details, appointment help, greeting, fallback, and blank input validation.
- Intent detector tests verify the keyword-based classification rules and date extraction behavior.
- The appointment page path supports direct navigation with `doctorId`, so the chat card redirect has an existing consumer.
- The frontend build path is compatible with the structured chat rendering components and the booking redirect helper.

## Current Capabilities

- Detects specialization queries and returns doctor cards.
- Detects availability queries and returns availability cards.
- Detects doctor detail and consultation fee queries.
- Detects appointment help requests.
- Handles greetings and fallback responses.
- Renders structured chat payloads in the frontend widget.
- Lets users book directly from the assistant cards.
- Routes users to the appointment page with the selected doctor preserved.
- Supports both `/api/chat` and `/api/v1/chat`.

## Known Limits

- Intent detection is rule-based, so it only understands the expressions covered by the keyword sets.
- The feature does not persist conversation history.
- The assistant does not stream responses.
- There is no LLM layer in this implementation.
- Booking still depends on the existing appointment page and doctor data being available.

