# Reverse Engineering Report

Date: 2026-07-09

## Scope

This report reverse-engineers the current implementation of the repository as it exists today. It describes the implemented architecture, runtime flow, module boundaries, AI subsystem behavior, configuration surfaces, and test-backed behavior without redesigning or proposing changes.

## System Overview

The repository is a two-application monorepo:

- `frontend/` is a Next.js 15 App Router application running on port `4002` by default.
- `backend/` is a FastAPI application backed by SQLAlchemy and SQLite.
- The default user path is browser -> Next.js UI -> Next.js catch-all proxy route -> FastAPI API -> SQLite.

The product currently implements:

- doctor listing and filtering
- manual appointment booking
- appointment confirmation lookup
- appointment search
- a live AI chat widget with deterministic routing, workflow execution, deterministic knowledge retrieval, and a provider-neutral LLM runtime seam with a real Claude transport behind a gated facade

## Top-Level Architecture

### Frontend application

The frontend is structured around route entry points, feature modules, shared UI, and a self-contained AI widget library.

- `frontend/app/`
  - page routes such as `/`, `/doctors`, `/appointments`, `/appointments/search`, and `/appointments/confirmation`
  - `app/api/[...path]/route.ts` acts as the backend proxy
- `frontend/features/doctors/`
  - doctor API mapping and doctor domain types
- `frontend/features/appointments/`
  - booking/search API mapping, booking form schema, hooks, utilities, and booking UI
- `frontend/components/`
  - route-facing UI composition for doctors and layout
- `frontend/lib/ai-widget/`
  - reusable chat UI, local reducer state, adapters, services, renderers, and types
- `frontend/stores/booking-store.ts`
  - Zustand store carrying booking state across routes

### Backend application

The backend follows a thin-routes, service-layer, repository-backed design.

- `backend/app/api/`
  - HTTP route handlers for health, doctors, availability, appointments, and chat
- `backend/app/services/`
  - business logic, deterministic chat logic, workflow execution, schedule generation, and prompt building
- `backend/app/repositories/`
  - SQLAlchemy query/mutation helpers
- `backend/app/models/`
  - SQLAlchemy ORM models
- `backend/app/schemas/`
  - Pydantic request/response contracts
- `backend/app/knowledge/`
  - deterministic repository-local knowledge ingestion and retrieval
- `backend/app/llm/`
  - provider-neutral LLM runtime seam, composition, activation, execution policy, validation, eligibility, composition, post-processing, facade, transport, and tracing
- `backend/app/db/`
  - engine/session setup, schema creation, and startup seeding

## Runtime Entry Points

### Frontend entry

`frontend/app/layout.tsx` is the global shell. It mounts the header, footer, page container, and `GlobalAiWidget`.

### Frontend API boundary

`frontend/lib/api-client.ts` is the shared fetch wrapper. It:

- targets `NEXT_PUBLIC_API_BASE_URL` or `/api`
- JSON-serializes request bodies
- disables caching
- normalizes backend errors into `ApiError`

`frontend/app/api/[...path]/route.ts` is the only frontend-to-backend transport path. It:

- builds the backend URL from `BACKEND_API_BASE_URL` or `http://localhost:4001`
- forwards method, headers, body, and query string
- strips `host`, `connection`, and `content-length`
- supports `GET`, `POST`, `PATCH`, `PUT`, `DELETE`, and `OPTIONS`

### Backend entry

`backend/app/main.py` creates the FastAPI app, applies CORS, runs `init_db()` during lifespan startup, and mounts the API router under `settings.api_prefix`, which defaults to `/api`.

`backend/app/api/router.py` registers:

- health
- chat
- versioned chat
- doctors
- availability
- appointments

## Business Modules

### Doctor directory

Implemented across:

- frontend: `frontend/app/doctors/page.tsx`, `frontend/components/doctors/*`, `frontend/features/doctors/api.ts`, `frontend/features/doctors/types.ts`
- backend: `backend/app/api/doctors.py`, `backend/app/services/doctor_service.py`, `backend/app/repositories/doctor_repository.py`, `backend/app/schemas/doctor.py`

Behavior:

- lists active doctors only
- supports backend filtering by specialty, appointment type, gender, location, and fee range
- orders results by rating, review count, and id
- maps backend doctor records into frontend card models
- allows frontend-side selection, sort by earliest availability, and pagination

### Scheduling and availability

Implemented across:

- backend: `backend/app/api/availability.py`, `backend/app/services/availability_service.py`, `backend/app/services/schedule_service.py`
- frontend: `frontend/features/appointments/api.ts`, `frontend/features/appointments/utils.ts`, booking components on the appointments page

Behavior:

- runtime availability is generated from static slot definitions in `schedule_service.py`
- daily slot start times are `08:00`, `10:00`, `12:00`, `14:00`, `16:00`, `18:00`
- past days are excluded
- elapsed same-day slots are excluded
- already-booked appointment times are excluded
- the legacy `doctor_availability` table still exists in the schema but booking availability is driven by generated schedule plus booked appointments

### Appointment booking

Implemented across:

- frontend: `frontend/app/appointments/page.tsx`, `frontend/features/appointments/components/*`, `frontend/stores/booking-store.ts`
- backend: `backend/app/api/appointments.py`, `backend/app/services/appointment_service.py`, `backend/app/repositories/appointment_repository.py`, `backend/app/repositories/patient_repository.py`, `backend/app/schemas/appointment.py`

Behavior:

- the page resolves `doctorId` from query string or Zustand store
- it fetches doctor details plus date-specific availability
- selected doctor/date/time/patient details are persisted in the booking store
- booking submission posts `AppointmentCreateRequest`
- backend validates:
  - doctor exists
  - appointment type is supported by the doctor
  - slot is in the future
  - slot exists in generated schedule
  - slot is not already booked
- patient identity is deduplicated by email
- appointment creation generates a unique confirmation code and persists a confirmed appointment

### Appointment confirmation

Implemented across:

- frontend: `frontend/app/appointments/confirmation/page.tsx`, `frontend/features/appointments/components/AppointmentSummary.tsx`
- backend: `backend/app/services/appointment_service.py`, `backend/app/api/appointments.py`

Behavior:

- frontend resolves appointment id and doctor id from query params or store
- backend returns full appointment, doctor, and patient details
- frontend falls back to stored booking data where useful
- successful chat-driven booking also redirects into this route

### Appointment search

Implemented across:

- frontend: `frontend/app/appointments/search/page.tsx`, `frontend/features/appointments/hooks/use-appointment-search.ts`, `use-appointment-details.ts`
- backend: `backend/app/api/appointments.py`, `backend/app/services/appointment_search_service.py`, `backend/app/schemas/appointment_search.py`

Behavior:

- supports lookup by partial patient name, exact email, or exact phone
- requires at least one non-empty query input
- joins `appointments`, `patients`, and `doctors`
- orders results by appointment date descending, then time descending
- maps internal appointment status into public search status values

## Data Model and Persistence

### Primary tables

`backend/app/models/doctor.py`

- stores doctor profile data
- serializes `appointment_types` and `languages` as JSON strings in text columns

`backend/app/models/patient.py`

- stores patient identity and contact data
- enforces unique email

`backend/app/models/appointment.py`

- stores appointment confirmation code, doctor/patient ids, date/time, appointment type, health description, status, and timestamps
- enforces a unique `(doctor_id, appointment_date, appointment_time)` constraint

`backend/app/models/availability.py`

- stores historical `doctor_availability` rows
- remains in the schema and repositories but is not the active source of appointment slots for booking

### DB initialization

`backend/app/db/database.py`:

- builds the engine from `DATABASE_URL`
- uses `check_same_thread=False` for SQLite
- exposes `get_db()` for FastAPI dependency injection
- drops and recreates the `doctors` table if required columns are missing
- calls `Base.metadata.create_all`
- runs `seed_doctors(session)`

### Seed data

`backend/app/db/seed.py` seeds the doctor catalog at startup if names do not already exist.

`backend/scripts/seed_test_data.py` is a separate idempotent utility that:

- targets `backend/app.db` by default
- adds extra demo doctors
- creates future appointments through the service layer
- avoids duplicate bookings and unsafe patient reuse
- writes `docs/reports/test-data-report.md`

## API Layer

### Doctors API

- `GET /api/doctors`
- `GET /api/doctors/{doctor_id}`

### Availability API

- `GET /api/doctors/{doctor_id}/availability?date=YYYY-MM-DD`

### Appointments API

- `POST /api/appointments`
- `GET /api/appointments/search`
- `GET /api/appointments/{appointment_id}`

### Chat API

- `POST /api/chat`
- `POST /api/v1/chat`

The versioned and unversioned chat routes share the same handler. Unexpected exceptions are converted into HTTP 500 with `Chat service is unavailable.`

## Frontend Runtime Flow

### Doctors flow

1. `frontend/app/doctors/page.tsx` renders `DoctorsPageClient`.
2. `DoctorsPageClient` calls `listDoctors(...)`.
3. `listDoctors` calls `apiClient.get("/doctors")`.
4. Next.js proxy forwards to FastAPI.
5. FastAPI routes to `read_doctors`.
6. `doctor_service.list_doctors` calls `doctor_repository.get_doctors_by_filters`.
7. ORM results are mapped to `DoctorResponse`.
8. Frontend maps `DoctorApiRecord` into `Doctor` card models and renders them.

### Booking flow

1. `/appointments` resolves doctor selection from query params or Zustand.
2. Frontend fetches doctor details and doctor availability in parallel.
3. User selects date, time, appointment type, and enters patient details.
4. Booking data is written into `booking-store.ts`.
5. `createAppointment(...)` posts to `/appointments`.
6. Backend validates and persists the appointment.
7. Frontend stores `appointmentId` and `confirmationCode`.
8. User is sent to `/appointments/confirmation`.

### Confirmation flow

1. confirmation page resolves `appointmentId` and `doctorId`
2. it fetches appointment details and doctor details in parallel
3. it renders the summary and can clear booking state through `resetBooking`

### Search flow

1. search page validates name/email/phone with React Hook Form plus Zod
2. `useAppointmentSearch` triggers `searchAppointments(...)`
3. backend validates at least one query field and returns joined results
4. `useAppointmentDetails` fetches a selected result on demand

## AI Modules

The AI-related implementation spans deterministic chat logic, workflow execution, knowledge retrieval, prompt construction, provider-neutral runtime composition, provider adapters, transport, validation, eligibility, response composition, post-processing, and tracing.

### Deterministic chat surface

Frontend AI modules:

- `frontend/components/layout/GlobalAiWidget.tsx`
- `frontend/lib/ai-widget/components/*`
- `frontend/lib/ai-widget/core/*`
- `frontend/lib/ai-widget/services/api-service.ts`
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
- `frontend/lib/ai-widget/adapters/noop-adapter.ts`

Backend AI modules:

- `backend/app/api/chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/conversation_manager.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/services/chat_intent_detector.py`
- `backend/app/services/chat_entity_extractor.py`
- `backend/app/schemas/chat.py`

### Knowledge modules

- `backend/app/knowledge/documents.py`
- `backend/app/knowledge/loader.py`
- `backend/app/knowledge/repository.py`
- `backend/app/knowledge/retrieval.py`
- `backend/app/knowledge/sources/`

### Prompt builder modules

- `backend/app/services/prompt_builder.py`

### LLM runtime seam

- `backend/app/llm/models.py`
- `backend/app/llm/interfaces.py`
- `backend/app/llm/registry.py`
- `backend/app/llm/service.py`
- `backend/app/llm/config.py`
- `backend/app/llm/budget.py`
- `backend/app/llm/adapters.py`
- `backend/app/llm/providers.py`
- `backend/app/llm/composition.py`
- `backend/app/llm/activation.py`
- `backend/app/llm/execution_policy.py`
- `backend/app/llm/operations.py`
- `backend/app/llm/orchestrator.py`
- `backend/app/llm/validation.py`
- `backend/app/llm/eligibility.py`
- `backend/app/llm/composer.py`
- `backend/app/llm/post_processor.py`
- `backend/app/llm/facade.py`
- `backend/app/llm/transport.py`
- `backend/app/llm/runtime_trace.py`

## Deterministic Chat Runtime Flow

### Chat request flow

1. The widget sends `{ message, conversation }` to `/api/chat`.
2. `create_chat_response(session, request)` is invoked from `chat_service.py`.
3. `create_chat_response` constructs:
   - a `RuleBasedChatResponder`
   - knowledge loader/repository/retrieval service
   - prompt builder
   - `LLMRuntimeCompositionRoot`
   - `LLMRuntimeFacade`
   - `ConversationManager`
4. `ConversationManager.handle(...)` becomes the single orchestration entry point.

### Conversation context flow

`ConversationManager`:

- rebuilds `ChatConversationContext` from request history plus prior context
- merges active filters from historical turns
- restores selected doctor identity from history
- restores active workflow state from context
- increments turn count and records last user/assistant messages

### Intent and filter extraction

Intent detection is handled by `detect_chat_intent(...)` in `chat_intent_detector.py`.

Search/entity extraction is handled by `extract_chat_search_filters(...)` and related helpers in `chat_entity_extractor.py`.

Extracted dimensions include:

- specialization
- gender
- fee range
- target date
- time preference
- clinic location

Date parsing supports:

- today/tomorrow/day after tomorrow
- numeric day/month/year
- textual month dates
- ordinal dates
- named weekdays

### Deterministic responder behavior

`RuleBasedChatResponder`:

- handles greetings
- lists specializations
- returns doctors by specialization
- returns doctor detail cards and consultation fee details
- returns availability cards using generated schedule
- answers generic help and informational fallbacks

The responder uses backend doctor and availability services directly rather than calling HTTP routes internally.

## Workflow Execution Flow

`WorkflowEngine` owns structured multi-turn workflows for:

- `BOOK_APPOINTMENT`
- `CANCEL_APPOINTMENT`
- `APPOINTMENT_CONFIRMATION`

### Workflow entry

`ConversationManager` asks `WorkflowEngine.handle(...)` before knowledge fallback or deterministic fallback when the request appears workflow-related or when an active workflow already exists.

### Booking workflow behavior

The workflow engine:

- detects doctor references
- extracts direct booking details from free text
- keeps a draft across conversation metadata
- computes missing required fields
- returns `INPUT_REQUIRED` until booking prerequisites are present
- executes `create_appointment_booking(...)` when ready
- converts known validation failures into workflow-safe chat responses instead of surfacing backend 500/503 errors

Required booking fields are:

- doctor
- appointment date
- start time
- patient full name
- patient email

### Cancellation and confirmation workflows

The workflow engine extracts either:

- appointment id
- confirmation code

It then calls:

- `cancel_appointment_booking(...)`
- `get_appointment_confirmation_by_reference(...)`

### Workflow output

Workflow results are returned through `ChatWorkflowResult`, including:

- workflow type
- status
- missing fields
- updated draft
- appointment summary when completed

The frontend AI widget inspects workflow metadata. If a booking workflow completes, `GlobalAiWidget` writes the confirmed booking into Zustand and navigates to the confirmation route.

## Vector-less RAG Flow

### Document loading

`FileSystemKnowledgeLoader` recursively loads `backend/app/knowledge/sources/`, skipping `README.md`, and supports:

- Markdown with required front matter
- JSON objects

Documents are validated into `KnowledgeDocument`.

### Repository behavior

`InMemoryKnowledgeRepository` lazily loads and caches all knowledge documents, indexing by document id and returning them sorted by priority and id.

### Retrieval behavior

`KnowledgeRetrievalService.retrieve_top_match(...)`:

- tokenizes the query
- removes broad stopwords
- computes weighted matches against:
  - title
  - aliases
  - keywords
  - synonyms
  - category
  - summary/body/tags
- returns the top scoring document match

Phrase matches are weighted more heavily than weak token overlap. Retrieval also records trace metadata when runtime tracing is enabled.

### Knowledge routing

`ConversationManager` only consults retrieval when:

- no active workflow is running
- a knowledge retrieval service exists

Knowledge is considered mainly for intents such as `UNKNOWN` and `APPOINTMENT_HELP`. If a match is chosen, the response message is built from document content, summary, or title, and `knowledge_source` metadata is attached to the chat response.

### Frontend knowledge rendering

`chat-response-mapper.ts` preserves `knowledge_source` in assistant message metadata. `MessageContentRenderer.tsx` renders a small knowledge-source footer for assistant text messages.

## Prompt Construction Flow

`backend/app/services/prompt_builder.py` defines a deterministic prompt-building pipeline.

### Prompt builder responsibilities

It normalizes caller input into a canonical `PromptContext` consisting of:

- user context
- conversation context
- workflow context
- knowledge context
- system instructions
- constraints
- rendering options

### Internal collectors

The module contains dedicated collectors for:

- conversation state
- workflow state
- knowledge documents
- system instructions

### Assembly model

Prompt context is converted into ordered sections such as:

- system instructions
- user message
- conversation state
- workflow state
- knowledge document sections

The output is then rendered into a bounded prompt string with optional truncation metadata.

### Runtime use

The prompt builder is not directly used by deterministic chat. It is used by the LLM orchestration path through `LLMGenerationOrchestrator`, including shadow-mode and controlled-generation flows inside the runtime facade.

## Provider Abstraction and LLM Execution Flow

### Canonical contract

`backend/app/llm/models.py` defines provider-neutral models for:

- messages
- generation requests/responses
- constraints
- structured output
- tool definitions and calls
- reasoning settings/results
- streaming settings/results
- citations
- token usage
- provider capabilities/descriptors
- generation budgets

### Registry and service

- `InMemoryLLMProviderRegistry` stores composed adapters.
- `LLMIntegrationService` resolves a provider and calls `provider.generate(...)`.

### Configuration

`backend/app/llm/config.py` loads nested `LLM_*` environment variables into:

- runtime flags
- selected provider
- per-provider configuration
- provider feature flags
- provider generation budget profiles

Providers modeled are:

- OpenAI
- Claude
- Gemini
- OpenRouter
- Ollama

### Budgeting

`backend/app/llm/budget.py` defines canonical profiles:

- `FAST`
- `BALANCED`
- `WORKFLOW`
- `QUALITY`
- `MAXIMUM`

These control reasoning effort, output/context token ceilings, latency preference, quality preference, and cost preference.

### Provider adapters

`backend/app/llm/providers.py` defines configurable adapters. They translate the canonical request into provider-private payloads and translate provider responses back into canonical `LLMGenerationResponse`.

The adapter layer supports transport injection. If no transport exists, the adapter remains inactive and raises a controlled runtime error.

### Composition root

`LLMRuntimeCompositionRoot` is the assembly point. It:

1. loads configuration
2. creates provider transports
3. creates provider adapters
4. evaluates activation
5. builds the provider registry
6. creates `LLMIntegrationService`
7. creates `LLMGenerationOrchestrator`
8. creates execution-policy and operational-readiness services

The default transport factory is `ProductionLLMProviderTransportFactory`, which currently creates a real transport only for Claude.

### Activation

`LLMRuntimeActivationEvaluator` determines whether the selected provider is healthy and generation-ready using:

- global runtime flags
- provider enabled state
- adapter presence
- transport presence
- authentication config
- generation budget resolution
- provider feature flags

### Execution policy

`AIExecutionPolicyEvaluator` chooses among canonical execution modes:

- `DETERMINISTIC_ONLY`
- `LLM_ONLY`
- `HYBRID`
- `SHADOW`

It also computes the official owner of the response:

- workflow
- knowledge
- deterministic
- LLM

Workflow ownership takes precedence over knowledge or LLM paths.

### Orchestration

`LLMGenerationOrchestrator`:

1. builds a prompt via `PromptBuilderService`
2. creates a canonical `LLMGenerationRequest`
3. invokes `LLMIntegrationService`
4. normalizes the result into `LLMGenerationOrchestrationResult`

### Validation

`LLMRuntimeResponseValidator` validates canonical runtime results after orchestration. It checks:

- required prompt/result fields
- assistant role
- non-empty response content
- valid canonical finish reason
- structured output presence/shape when requested
- metadata validity

### Eligibility

`LLMRuntimeResponseEligibilityEvaluator` decides whether validated LLM output is eligible to be exposed to the user. This is a provider-neutral gate layered after validation.

### Composition

`LLMRuntimeResponseComposer` merges deterministic business truth and LLM output into:

- deterministic-only final responses
- LLM-only final responses
- hybrid responses

For hybrid mode, deterministic business fields are preserved and optional LLM guidance is appended.

### Post-processing

`LLMRuntimeResponsePostProcessor` performs final presentation normalization:

- newline normalization
- trailing-space trimming
- markdown heading/list/blockquote cleanup
- duplicate blank line collapsing
- removal of presentation-only metadata keys

### Facade

`LLMRuntimeFacade` is the public runtime boundary. It supports:

- save-ready runtime snapshots
- shadow-mode execution
- controlled generation
- validation
- eligibility
- composition
- post-processing

## Shadow and Controlled Generation Behavior

### Shadow mode

`ConversationManager` can call `LLMRuntimeFacade.run_shadow_mode(...)`.

This preserves the visible deterministic/knowledge/workflow response and runs the LLM path for diagnostics only. Shadow execution can be asynchronous or inline.

### Controlled generation

`ConversationManager` can also call `run_controlled_generation(...)` for low-risk conversational scenarios.

The current implementation:

- keeps workflow-owned requests deterministic
- may run hybrid generation for approved non-workflow turns
- validates and checks eligibility before exposing generated content
- composes final responses so business truth remains intact

Test coverage shows controlled generation can append LLM guidance to a deterministic business response when execution policy and activation allow it.

## Concrete Provider Transport

`backend/app/llm/transport.py` contains the live production transport implementation for Claude.

### Claude transport behavior

`ClaudeTransport`:

- builds Anthropic `messages.create(...)` payloads
- resolves `max_tokens` from request or generation budget
- forwards supported tool and tool-choice payloads
- forwards supported system prompt, temperature, top-p, and stop sequences
- whitelists only supported outbound metadata, currently `user_id`
- strips internal routing/runtime metadata from outbound provider payloads
- normalizes Anthropic responses into provider payload dictionaries used by the adapter
- records request id, response id, token usage, citations, tool calls, and thinking summary where present
- raises normalized `LLMTransportError` instances on failures

Only Claude has a production transport in the current implementation. Other configured providers remain architecture-level seams unless transports are added.

## Tracing and Logging

### Runtime trace

`backend/app/llm/runtime_trace.py` provides request-scoped tracing through `AIRuntimeTraceSession`.

The trace payload records:

- request and conversation ids
- redacted user message
- intent
- execution mode
- selected provider
- activation snapshot
- stop component and stop reason
- final response source/preview
- per-stage execution state
- exceptions with component, type, message, and stack trace

Tracked stages include:

- conversation manager
- workflow engine
- vectorless RAG
- execution policy
- runtime facade
- prompt builder
- llm integration
- provider adapter
- provider transport
- runtime validator
- eligibility
- composer
- post processor
- final response

When tracing is enabled, exactly one JSON line per request is emitted to `logs/ai-runtime-trace.log` via a dedicated rotating logger.

### Other logging

`backend/app/db/database.py` logs a warning when it rebuilds the seeded `doctors` table because of schema mismatch.

## Extension Points

The current codebase exposes several extension seams already reflected in the implementation:

- new FastAPI API domains can be added through `backend/app/api/router.py`
- new deterministic chat intents can be added through `chat_intent_detector.py`, `chat_entity_extractor.py`, and `chat_service.py`
- new workflows can be added through `workflow_engine.py` and chat schema enums
- new knowledge documents can be added under `backend/app/knowledge/sources/`
- new retrieval ranking behaviors can be added in `knowledge/retrieval.py`
- new provider adapters can be added in `backend/app/llm/providers.py`
- new transports can be added through `LLMProviderTransportFactory`
- new runtime-response gates can be added around the facade pipeline
- the frontend AI widget can swap adapters or services without changing page code

## Reusable Platform Components

The following components act as platform-style building blocks rather than being specific to one business flow:

- `frontend/lib/api-client.ts`
- `frontend/app/api/[...path]/route.ts`
- `frontend/lib/ai-widget/*`
- `backend/app/db/database.py`
- `backend/app/knowledge/*`
- `backend/app/services/prompt_builder.py`
- `backend/app/llm/*`
- `backend/app/llm/runtime_trace.py`

## Business-Specific Components

The following components encode product-specific doctor-booking behavior:

- `backend/app/services/doctor_service.py`
- `backend/app/services/availability_service.py`
- `backend/app/services/schedule_service.py`
- `backend/app/services/appointment_service.py`
- `backend/app/services/appointment_search_service.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/db/seed.py`
- `frontend/features/doctors/*`
- `frontend/features/appointments/*`
- `frontend/stores/booking-store.ts`

## Runtime Configuration Surface

### Frontend configuration

- `NEXT_PUBLIC_API_BASE_URL`
- `BACKEND_API_BASE_URL`

### Backend application configuration

Defined in `backend/app/core/config.py`:

- `APP_NAME`
- `API_PREFIX`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `AI_RUNTIME_TRACE`

### LLM runtime configuration

Defined in `backend/app/llm/config.py` with `LLM_` prefix and nested keys, including:

- selected provider
- global runtime enablement
- shadow mode
- generation allow/deny
- streaming/tool/reasoning flags
- provider enabled state
- provider model name
- provider api key
- provider base URL
- timeout and retry configuration
- generation budget defaults and overrides

## Testing Infrastructure

### Backend test stack

The backend uses:

- `pytest`
- `fastapi.testclient`
- SQLite test databases
- fixture-driven environment isolation

### Test organization

Tests exist for:

- doctors API
- appointments API
- appointment DB behavior
- availability service
- appointment search service
- chat API
- chat intent detection
- chat entity extraction
- conversation manager
- knowledge repository and retrieval
- prompt builder
- LLM models
- LLM integration service
- orchestrator
- config
- budget
- activation
- execution policy
- operations
- provider adapters
- facade
- transport
- validation
- eligibility
- composer
- post-processor
- runtime trace

### Testing role in architecture

The tests do more than unit validation. They also lock in behavioral contracts such as:

- workflow-first chat routing
- knowledge-before-deterministic fallback for eligible turns
- controlled generation skipping and success paths
- prompt builder inclusion of workflow and conversation state
- outbound Claude request sanitization
- exact-once runtime trace emission

## Architectural Decisions Reflected by the Implementation

The current implementation reflects the following decisions in code:

- Next.js is used as both UI runtime and backend proxy layer.
- FastAPI routes stay thin and delegate business logic to services.
- SQLAlchemy repositories isolate persistence queries from route handlers.
- Doctor availability is generated at runtime from a schedule rather than read from the legacy availability table during booking flow execution.
- Deterministic chat remains the primary visible assistant path.
- Chat orchestration is centralized in `ConversationManager`.
- Workflow execution takes precedence over retrieval and general deterministic responses.
- Knowledge retrieval is deterministic, local, and vector-less.
- Prompt construction is separated from runtime routing and provider transport.
- The LLM subsystem is provider-neutral at the contract level.
- Runtime activation and execution policy explicitly gate whether LLM output can affect user-visible responses.
- Validation, eligibility, composition, and post-processing are separate canonical stages after generation.
- Runtime tracing is first-class and request-scoped, with a dedicated rotating JSON log sink.
- Only Claude currently has a production transport, while the rest of the provider surface remains a composed extension seam.

## Current Implementation Boundary

The implementation currently includes a real Claude transport and controlled-generation capability behind gating, but the system still preserves deterministic ownership for workflows and business-critical responses. The repository therefore combines:

- a fully implemented doctor-booking application
- a live deterministic AI chat assistant
- a live deterministic knowledge retrieval layer
- a provider-neutral LLM runtime architecture with a production Claude provider boundary and guarded response exposure
