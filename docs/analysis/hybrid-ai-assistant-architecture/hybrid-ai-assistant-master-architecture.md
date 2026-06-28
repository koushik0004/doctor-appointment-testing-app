# Hybrid AI Assistant Master Architecture

## Purpose

This document is the reference architecture for the existing Doctor Appointment AI Assistant. It describes the current implementation, the intentional boundaries between layers, and the migration path for future AI phases without changing current runtime behavior.

This document reflects the codebase as of June 28, 2026.

## Architecture Goals

- Keep the current manual booking flow stable.
- Keep the deterministic assistant as the active execution engine.
- Separate UI, API, AI orchestration, knowledge access, and workflow handoff concerns.
- Preserve backward compatibility for existing frontend and backend modules.
- Create explicit seams for future evolution without introducing new runtime dependencies now.

## Current System Snapshot

The AI assistant is implemented as a rule-based chat experience embedded in the Next.js frontend and backed by FastAPI endpoints. It can:

- Answer greetings and booking-help questions.
- Search doctors by specialization, gender, fee, and location.
- Find date-based and time-filtered availability.
- Return structured doctor cards and availability cards.
- Maintain multi-turn conversation context through a backend conversation manager.
- Link users into the existing manual booking flow.

It does not currently:

- Execute browser automation.
- Perform bookings through chat.
- Use an LLM.
- Introduce a separate workflow engine process.

## Layer Model

### 1. Frontend Layer

Primary responsibility: user interaction, chat rendering, and navigation handoff.

Current modules:

- `frontend/components/layout/GlobalAiWidget.tsx`
- `frontend/lib/ai-widget/components/*`
- `frontend/lib/ai-widget/core/*`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/services/appointment-navigation.ts`
- `frontend/lib/api-client.ts`
- `frontend/app/api/[...path]/route.ts`

Responsibilities:

- Mount the assistant globally.
- Capture user chat input and local widget state.
- Send chat requests to the frontend API proxy.
- Map backend chat payloads into UI-specific message content.
- Render structured outputs such as doctor lists, availability cards, and help steps.
- Route the user into the manual appointment flow through links like `/appointments?doctorId=...`.

Boundaries:

- No business rules for doctor search or slot computation.
- No direct database access.
- No direct backend-origin decision making beyond presentation mapping.

### 2. API Layer

Primary responsibility: stable transport boundary between frontend and backend.

Current modules:

- `frontend/app/api/[...path]/route.ts`
- `frontend/lib/api-client.ts`
- `backend/app/api/chat.py`
- `backend/app/api/router.py`
- `backend/app/main.py`
- `backend/app/schemas/chat.py`

Responsibilities:

- Accept frontend chat requests at `/api/chat`.
- Proxy those requests from Next.js to FastAPI.
- Validate request and response payloads.
- Expose both `/api/chat` and `/api/v1/chat` for compatibility.
- Normalize transport behavior and error handling.

Boundaries:

- The API layer does not interpret user intent.
- The API layer does not decide doctor ranking or slot availability.
- The API layer remains thin so AI behavior changes stay in backend services.

### 3. AI Layer

Primary responsibility: deterministic interpretation and response generation.

Current modules:

- `backend/app/services/conversation_manager.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/app/services/chat_entity_extractor.py`

Responsibilities:

- Centralize request orchestration through the Conversation Manager.
- Detect intent from free-text messages.
- Extract structured entities such as specialization, gender, fee range, date, time preference, and location.
- Maintain canonical conversation context, lifecycle, and routing state.
- Resolve the response path for doctor search, availability search, doctor detail lookup, booking help, and cancellation help.
- Build the canonical chat response contract.

Boundaries:

- No direct UI rendering.
- No browser automation.
- No workflow execution outside deterministic service calls.
- No prompt-based reasoning or LLM dependency.

### 4. Workflow Layer

Primary responsibility: translate assistant outcomes into safe user actions and controlled handoffs.

Current modules and seams:

- `frontend/lib/ai-widget/services/appointment-navigation.ts`
- `frontend/lib/ai-widget/adapters/noop-adapter.ts`
- `backend/app/services/conversation_manager.py`
- booking entry route `/appointments?doctorId=...`

Current behavior:

- The workflow layer is intentionally minimal.
- The assistant can recommend actions and deep-link the user into the manual booking flow.
- The frontend adapter is a noop presentation adapter, which means the assistant is informational and navigational rather than operational.
- The Conversation Manager routes every live request to the deterministic engine and reserves the workflow seam for future phases.

Architectural role:

- Preserve a dedicated seam where future phases can introduce orchestrated actions.
- Prevent chat response generation from being tightly coupled to browser automation or booking-side effects.

Boundaries:

- No autonomous booking execution.
- No hidden user actions.
- No mutation of booking state outside existing manual flows.

### 5. Knowledge Layer

Primary responsibility: provide trusted domain data and derived scheduling facts.

Current modules:

- `backend/app/services/doctor_service.py`
- `backend/app/services/availability_service.py`
- `backend/app/services/schedule_service.py`
- `backend/app/repositories/doctor_repository.py`
- `backend/app/repositories/appointment_repository.py`
- `backend/app/models/*`
- `backend/app/schemas/doctor.py`
- `backend/app/schemas/availability.py`
- `backend/app/schemas/appointment.py`
- SQLite database in `backend/app.db`

Responsibilities:

- Return doctor records with normalized API-facing fields.
- Generate available slots from schedule rules plus booked appointments.
- Read persisted appointment state to suppress already-booked slots.
- Supply the deterministic AI layer with the same authoritative data used by the manual booking flow.

Boundaries:

- No chat rendering logic.
- No intent detection logic.
- No frontend presentation mapping.

### 6. Backend Platform Layer

Primary responsibility: application lifecycle, routing composition, persistence access, and cross-cutting concerns.

Current modules:

- `backend/app/main.py`
- `backend/app/db/database.py`
- `backend/app/api/router.py`

Responsibilities:

- Start the FastAPI app.
- Initialize the database at startup.
- Register API routers.
- Provide shared dependency injection and session access.

Boundaries:

- No feature-specific decision logic beyond composition.

## High-Level Request Flow

### Current Assistant Request Flow

```text
User enters chat message in AI widget
  ->
AiWidgetRoot submits message through createApiAiWidgetService()
  ->
frontend/lib/api-client.ts sends POST /api/chat
  ->
frontend/app/api/[...path]/route.ts proxies request to FastAPI
  ->
backend/app/api/chat.py validates ChatRequest and calls create_chat_response()
  ->
ConversationManager loads conversation context, merges entities, and selects routing target
  ->
chat_intent_detector.py classifies intent
  ->
chat_entity_extractor.py extracts structured filters
  ->
chat_service.py queries doctor_service and availability_service as needed
  ->
ChatResponse is returned with intent + message + structured data + conversation metadata
  ->
chat-response-mapper.ts maps payload to widget message content
  ->
Frontend renders doctor cards, availability cards, or help content
  ->
User optionally follows booking link into the manual appointment flow
```

### Manual Booking Handoff Flow

```text
Assistant response contains doctor or availability card
  ->
Frontend builds /appointments?doctorId=...
  ->
Existing booking page loads doctor and availability data
  ->
User completes patient details and confirms booking manually
```

## Component Interaction Map

### Frontend Interaction

- `GlobalAiWidget` mounts the reusable widget shell at app level.
- `AiWidgetRoot` owns chat submission and local widget state transitions.
- `createApiAiWidgetService()` calls the frontend API client.
- `chat-response-mapper.ts` converts backend response contracts into frontend-renderable message types.
- `appointment-navigation.ts` keeps booking handoff logic isolated from rendering code.

### Backend Interaction

- `chat.py` is a thin transport endpoint.
- `create_chat_response()` is the stable entry point for assistant behavior.
- `ConversationManager` is the single orchestration entry point for all chat requests.
- `detect_chat_intent()` decides the initial route category.
- `extract_chat_search_filters()` derives structured filters independently from transport.
- `ConversationManager` merges prior context with current-turn entities and tracks routing state.
- `RuleBasedChatResponder` remains the deterministic execution engine and coordinates read-only domain service calls plus response assembly.
- `doctor_service.py` provides doctor search data.
- `availability_service.py` provides slot visibility using appointment-backed schedule generation.

## Dependency Rules

Allowed dependency direction:

```text
Frontend UI
  -> Frontend service/mapping layer
  -> API layer
  -> AI layer
  -> Knowledge layer
  -> Repositories / database
```

Rules:

- Frontend UI depends on frontend service abstractions, not backend internals.
- API routes depend on schemas and services, not frontend types.
- AI services depend on domain services and schemas, not repository internals where a service abstraction exists.
- Knowledge services depend on repositories and schedule logic, not chat UI modules.
- Workflow handoff depends on route contracts, not database mutation.

Forbidden coupling:

- Frontend components directly encoding backend search rules.
- Chat endpoint logic embedding SQL or repository-specific response shaping.
- AI modules directly mutating appointment records as part of chat.
- Future automation logic bypassing existing API and service boundaries.

## Why The Deterministic Engine Remains Primary

The current deterministic engine is the correct primary execution layer because it provides:

- Predictable behavior for a medical-adjacent scheduling flow.
- Straightforward regression coverage.
- Stable structured outputs for the widget UI.
- Tight reuse of existing doctor and availability services.
- Low operational complexity compared with adding LLM inference or workflow automation.

This is especially important because the current assistant’s value is mostly retrieval, clarification, and guided navigation, not autonomous execution.

## ADR Summary

See `docs/analysis/hybrid-ai-assistant-architecture/adr-001-deterministic-ai-engine-primary.md`.

Decision summary:

- Keep the rule-based assistant as the production execution engine.
- Treat future LLM or orchestration capabilities as additive adapters, not replacements for current domain services.
- Preserve the current request and response contracts to avoid breaking the manual booking flow or the widget rendering pipeline.

## Migration Strategy

The intended evolution path is incremental and backward-compatible.

### Phase 1: Stabilize Current Deterministic Assistant

- Keep current chat contracts unchanged.
- Continue using deterministic intent detection and entity extraction.
- Maintain manual booking as the only state-changing execution path.

### Phase 2: Introduce Optional Orchestration Seams

- Add a workflow coordinator behind the current AI service boundary if needed.
- Keep chat responses schema-compatible with existing frontend rendering.
- Continue routing authoritative data access through doctor and availability services.

### Phase 3: Add Optional LLM Assistance Behind Guardrails

- Restrict LLM use to interpretation, summarization, or fallback classification.
- Keep final domain actions validated by deterministic service rules.
- Preserve deterministic post-processing before any user-visible action or structured response is emitted.

### Phase 4: Add Controlled Action Execution

- Introduce explicit user-approved workflow actions.
- Reuse existing booking APIs and validation services.
- Keep autonomous execution disabled unless new architecture and product requirements explicitly allow it.

## Backward Compatibility Requirements

- `/api/chat` remains supported.
- `/api/v1/chat` remains supported.
- `ChatRequest` continues to accept a plain `message` without requiring conversation metadata.
- `ChatResponse` continues to expose `message`, `intent`, `data`, `search_filters`, and `help_steps`, while adding optional `conversation` metadata.
- Frontend widget message mapping remains contract-driven rather than inference-driven.
- Manual booking routes remain the only supported appointment mutation path.

## Non-Goals In This Architecture

- Replacing the existing booking flow.
- Adding browser automation.
- Adding new APIs or transport formats.
- Moving logic into prompts.
- Adding long-running agent infrastructure.

## Implementation Boundaries For Future Work

Any future AI architecture phase should preserve these constraints unless a new ADR explicitly changes them:

- Keep domain truth in backend services and persisted data.
- Keep the assistant read-heavy and side-effect-light by default.
- Keep state-changing actions behind explicit, validated application flows.
- Keep frontend rendering decoupled from AI decision logic.

## Reference Files

- `frontend/components/layout/GlobalAiWidget.tsx`
- `frontend/lib/ai-widget/components/AiWidgetRoot.tsx`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/services/appointment-navigation.ts`
- `frontend/app/api/[...path]/route.ts`
- `frontend/lib/api-client.ts`
- `backend/app/api/chat.py`
- `backend/app/api/router.py`
- `backend/app/main.py`
- `backend/app/services/conversation_manager.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/app/services/chat_entity_extractor.py`
- `backend/app/services/doctor_service.py`
- `backend/app/services/availability_service.py`
