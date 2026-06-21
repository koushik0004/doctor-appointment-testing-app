# Feature Report

## Executive Summary

Feature 7 implemented a reusable AI chat widget for the doctor appointment app and wired it to a backend chat endpoint. The widget now opens globally from the app shell, accepts messages, renders assistant replies, and can switch between noop, mock, and API-backed services.

The backend chat service was upgraded from static keyword replies to a rule-based doctor knowledge layer that reads from the existing SQLite data through the service layer. It can answer about available doctors, specializations, consultation fees, and appointment slots. No LLM integration was added.

## Business Objective

The feature gives users a persistent assistant that can help them discover doctors and booking options without leaving the app. It reduces friction for common questions such as:

- Which doctors are available?
- Which specialties are present?
- What does a specific doctor charge?
- What appointment slots are open?

## Implementation Overview

The work spans the frontend widget package and the backend chat API.

- The frontend now has a reusable widget package under `frontend/lib/ai-widget`.
- The widget is mounted globally from the root layout through `frontend/components/layout/GlobalAiWidget.tsx`.
- The backend exposes `POST /api/chat` and `POST /api/v1/chat`.
- The backend chat responder uses existing doctor and availability services instead of hardcoded strings.

The feature implementation window in git is centered on these commits:

- `8451b91` base widget scaffolding
- `f234264` floating launcher and global layout integration
- `808f3b2` chat window UI refinement
- `488c1fa` mock response engine
- `19fc49b` backend chat API creation
- `a8139e4` frontend integration with the backend chat service
- `6e6bcea` doctor knowledge layer

## Frontend Changes

No page-specific route files were changed for this feature. The widget is injected through the app shell, so it appears across the application.

Added frontend modules:

- `frontend/lib/ai-widget/core/state.ts`
- `frontend/lib/ai-widget/core/context.tsx`
- `frontend/lib/ai-widget/components/AiWidgetRoot.tsx`
- `frontend/lib/ai-widget/components/ChatLauncher.tsx`
- `frontend/lib/ai-widget/components/ChatWindow.tsx`
- `frontend/lib/ai-widget/components/MessageList.tsx`
- `frontend/lib/ai-widget/components/MessageComposer.tsx`
- `frontend/lib/ai-widget/services/noop-service.ts`
- `frontend/lib/ai-widget/services/mock-service.ts`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/adapters/noop-adapter.ts`
- `frontend/components/layout/GlobalAiWidget.tsx`

Behavior implemented on the frontend:

- A floating launcher opens and closes the chat panel.
- The widget keeps local state for open/close, draft text, message history, sending state, and error state.
- The message composer disables input while a request is in flight.
- Messages render in a simple assistant/user conversation thread.
- Quick actions are part of the public widget shape, but the current noop adapter returns none.
- The root layout now mounts the widget on every page.

State management is internal to the widget package. There is no Zustand store involved in this feature.

## Backend Changes

Added or modified backend modules:

- `backend/app/api/chat.py`
- `backend/app/api/router.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/core/errors.py`
- `backend/tests/test_chat_api.py`

Backend behavior:

- `ChatRequest` validates a non-empty `message` string.
- `ChatResponse` returns a single `response` string.
- The route handlers inject a SQLAlchemy session and delegate to the service layer.
- The chat service now queries doctor and availability data through existing services.
- The responder is rule-based and does not call an LLM.

Database changes:

- No schema, model, or migration changes were added for this feature.
- The feature reuses the existing SQLite database and seeded doctor data.

## Integration Changes

Frontend to backend communication was added through the existing API client wrapper.

- Frontend request payload: `{ "message": string }`
- Backend response payload: `{ "response": string }`
- Frontend service: `createApiAiWidgetService()`
- Backend endpoints: `POST /api/chat` and `POST /api/v1/chat`

Request flow:

1. User enters a message in the widget.
2. The widget dispatches a sending state and appends the user message locally.
3. `createApiAiWidgetService()` posts the message to the backend.
4. The backend responder queries the database through `doctor_service` and `availability_service`.
5. The backend returns a plain text response.
6. The frontend converts that response into an assistant message and appends it to the thread.

## AI Chat Widget Details

Widget architecture:

- `AiWidgetRoot` is the public entry point.
- `AiWidgetProvider` and `useAiWidget` live in `frontend/lib/ai-widget/core`.
- `AiWidgetRoot` composes the launcher and chat window.
- `AiWidgetService` abstracts the message transport layer.
- `AiWidgetAdapter` supplies copy and presentation settings.

Folder structure:

- `adapters/` for presentation adapters
- `components/` for launcher, window, composer, and list UI
- `core/` for reducer and context
- `services/` for noop, mock, and API transports
- `styles/` for shared Tailwind class tokens
- `types/` for widget contracts

Public interfaces:

- `AiWidgetRoot`
- `AiWidgetProvider`
- `useAiWidget`
- `createNoopAiWidgetAdapter`
- `createNoopAiWidgetService`
- `createMockAiWidgetService`
- `createApiAiWidgetService`

Current capabilities:

- Open and close the widget
- Capture and submit chat messages
- Render assistant replies
- Show a sending indicator
- Show error text on request failure
- Ask about doctors, specialties, fees, and slots through the backend service

Current limitations:

- No streaming responses
- No persisted conversation history
- No LLM integration
- Quick actions are rendered only when provided by an adapter

## File Structure Changes

Frontend additions:

- `frontend/lib/ai-widget/`
- `frontend/components/layout/GlobalAiWidget.tsx`

Backend additions:

- `backend/app/api/chat.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/chat_service.py`
- `backend/tests/test_chat_api.py`

Modified shell integration:

- `frontend/app/layout.tsx`
- `backend/app/api/router.py`
- `backend/app/core/errors.py`

## APIs

### Backend chat API

`POST /api/chat`

Request:

```json
{
  "message": "Show cardiologists"
}
```

Response:

```json
{
  "response": "Available Cardiology doctors: ..."
}
```

`POST /api/v1/chat`

- Same request and response contract as `/api/chat`
- Registered in `backend/app/api/router.py`

### Frontend widget service interface

`AiWidgetService.sendMessage(request)`

Request shape:

```ts
{
  message: string;
  conversation: AiWidgetMessage[];
}
```

Response shape:

```ts
{
  reply: AiWidgetMessage;
}
```

## Data Flow

The current data flow is database-backed and rule-based.

1. User sends a message in the chat widget.
2. Frontend appends the user message to local widget state.
3. The API service posts the message to the backend chat endpoint.
4. `chat_service.py` normalizes the message and checks intent keywords.
5. For doctor knowledge requests, the service loads doctors from the database using `list_doctors()` and slots using `get_available_slots()`.
6. The responder formats a plain-text answer and returns it through `ChatResponse`.
7. The frontend appends that response as an assistant message.

## Technical Decisions

- The widget was isolated under `frontend/lib/ai-widget` to keep it reusable and easy to extract later.
- A reducer and context were used for local widget state so the UI stays self-contained.
- Adapter and service abstractions were added early so the widget can swap transport or presentation behavior without rewriting the UI.
- The backend chat handler delegates to a service layer and never queries the database in the route handler.
- The doctor knowledge layer is rule-based on purpose, matching the prompt requirement to avoid LLM integration for now.
- Slot answers are generated from the existing availability service rather than a separate AI memory layer.

## Current Capabilities

- Global floating assistant launcher in the app shell
- Expandable chat window with message history
- Mock service for local UI behavior
- API service that talks to the backend
- Backend answers about doctors, specialties, consultation fees, and available slots
- Test coverage for greeting, specialty lookup, fee lookup, slot lookup, blank input validation, and fallback messaging

## Known Limitations

- The chat logic is deterministic and rule-based.
- No natural-language parsing for dates has been added.
- No session persistence or conversation storage exists.
- Quick actions are not wired to actual click behavior yet.
- The assistant answers from existing database records only.

## Future Enhancements

- Add an actual LLM layer behind the same `AiWidgetService` contract.
- Parse dates and more natural slot queries instead of relying on fixed-time heuristics.
- Add clickable quick actions that prefill the composer.
- Persist conversation state if product requirements call for it.
- Expand the backend knowledge layer beyond doctor and availability lookup.

## Recommended Next Steps

1. Implement the booking flow pages and APIs that this assistant is meant to support.
2. Add richer chat intents for search and appointment creation once the manual booking flow is complete.
3. Replace the rule-based responder with an LLM-backed service behind the same transport interface if needed.
4. Add end-to-end UI tests for the widget against the running frontend and backend.

## Files Modified

- `backend/app/api/chat.py`
- `backend/app/api/router.py`
- `backend/app/core/errors.py`
- `backend/app/schemas/chat.py`
- `backend/app/services/chat_service.py`
- `backend/tests/test_chat_api.py`
- `frontend/app/layout.tsx`
- `frontend/components/layout/GlobalAiWidget.tsx`
- `frontend/lib/ai-widget/adapters/index.ts`
- `frontend/lib/ai-widget/adapters/noop-adapter.ts`
- `frontend/lib/ai-widget/components/AiWidgetRoot.tsx`
- `frontend/lib/ai-widget/components/ChatLauncher.tsx`
- `frontend/lib/ai-widget/components/ChatWindow.tsx`
- `frontend/lib/ai-widget/components/MessageComposer.tsx`
- `frontend/lib/ai-widget/components/MessageList.tsx`
- `frontend/lib/ai-widget/components/index.ts`
- `frontend/lib/ai-widget/core/context.tsx`
- `frontend/lib/ai-widget/core/index.ts`
- `frontend/lib/ai-widget/core/state.ts`
- `frontend/lib/ai-widget/index.ts`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/services/index.ts`
- `frontend/lib/ai-widget/services/mock-service.ts`
- `frontend/lib/ai-widget/services/noop-service.ts`
- `frontend/lib/ai-widget/styles/index.ts`
- `frontend/lib/ai-widget/styles/tokens.ts`
- `frontend/lib/ai-widget/types/adapter.ts`
- `frontend/lib/ai-widget/types/index.ts`
- `frontend/lib/ai-widget/types/message.ts`
- `frontend/lib/ai-widget/types/service.ts`
- `frontend/lib/ai-widget/types/widget.ts`

## Commit Summary

- `2b003b9` created the chatbot prompt scaffold for the feature sequence.
- `8451b91` introduced the reusable widget package, core state, and base UI components.
- `f234264` added the floating launcher and mounted the widget in the app shell.
- `808f3b2` refined the chat window UI and widget state handling.
- `488c1fa` added the mock response engine for local behavior.
- `19fc49b` added the backend chat API, schemas, error handling, and API service integration.
- `a8139e4` connected the frontend widget to the backend chat service.
- `6e6bcea` replaced static replies with a doctor knowledge layer backed by existing database services.
