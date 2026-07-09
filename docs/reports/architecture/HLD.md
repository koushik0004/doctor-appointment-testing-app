# High Level Design

Date: 2026-07-09

## Executive Summary

This application is a monorepo-based doctor appointment platform with a Next.js frontend, a FastAPI backend, and a SQLite database. The implemented product supports doctor discovery, appointment booking, booking confirmation, appointment search, and an AI assistant that combines deterministic routing, request-scoped workflows, deterministic knowledge retrieval, and a guarded provider-neutral LLM runtime seam. The current production request path is browser -> Next.js App Router frontend -> Next.js backend proxy route -> FastAPI services -> SQLite. The AI runtime remains business-rule-first: workflow-owned and operational requests stay deterministic, while only explicitly approved low-risk conversational responses may surface controlled LLM output through a gated facade.

## Business Objectives

- Allow patients to discover doctors by specialty and profile attributes.
- Allow patients to book appointments against valid future time slots.
- Allow patients to retrieve booked appointment details and confirmation data.
- Allow patients to search for existing appointments using contact identifiers.
- Provide an assistant surface that can answer support questions, help with doctor discovery, expose doctor availability, and guide booking without bypassing business validations.

## Scope

The current implementation includes:

- Doctor listing and filtering
- Manual appointment booking
- Appointment confirmation lookup
- Appointment search
- Global AI chat widget
- Deterministic chat orchestration with request-scoped workflow execution
- Deterministic Vector-less RAG knowledge retrieval
- Provider-neutral prompt-building and LLM runtime layers
- Claude-backed production transport behind the gated LLM facade
- Backend runtime tracing for AI execution

## Non-Scope

The current implementation does not include:

- Persisted conversation history
- Multi-user authentication or authorization
- Payment processing
- Email confirmation delivery in the active runtime path
- Browser automation driven by the assistant
- Vector database, embeddings, or semantic retrieval
- Multi-node deployment coordination or distributed tracing infrastructure

## Functional Requirements

- Display doctor profiles and support API-level doctor filtering.
- Generate bookable availability from schedule rules and existing appointments.
- Prevent booking into past or already-booked slots.
- Create appointments with persisted patient and appointment records.
- Return appointment confirmation details by appointment id.
- Search appointments by patient name, email, or phone.
- Accept chat requests through a frontend widget and backend chat API.
- Route chat requests through workflow-first orchestration.
- Support booking, cancellation-help, confirmation, doctor search, doctor details, and availability responses in chat.
- Retrieve FAQ-style knowledge from repository-local Markdown and JSON sources when no workflow is active.
- Optionally run shadow or controlled LLM execution through a provider-neutral facade when runtime policy allows it.
- Emit backend AI runtime traces when enabled by configuration.

## Non-Functional Requirements

- Preserve thin route handlers with business logic in services.
- Keep frontend and backend concerns isolated by application boundary.
- Maintain deterministic business truth for booking and workflow-owned actions.
- Validate request and response contracts with Pydantic and TypeScript domain models.
- Support local development with SQLite and minimal setup.
- Provide deterministic test coverage around booking, search, chat, knowledge, and LLM seams.
- Ensure controlled LLM output passes validation, eligibility, composition, and post-processing gates before frontend visibility.

## System Context

```txt
Patient Browser
  -> Next.js Frontend (port 4002 default)
  -> Next.js API Proxy (/api/[...path])
  -> FastAPI Backend (port 4001 default)
  -> SQLAlchemy Services and Repositories
  -> SQLite (backend/app.db by default)

AI Chat Requests
  -> Frontend AI Widget
  -> FastAPI Chat API
  -> ConversationManager
  -> Workflow Engine / Knowledge Retrieval / Deterministic Chat
  -> Optional LLM Runtime Facade
  -> Claude Transport when policy and activation allow
```

## High-Level Architecture

```txt
Frontend
  - Next.js App Router pages
  - Feature modules
  - Zustand booking store
  - AI widget library
  - Catch-all backend proxy

Backend
  - FastAPI routes
  - Service layer
  - Repository layer
  - SQLAlchemy models
  - Pydantic schemas
  - Knowledge repository and retrieval
  - Workflow engine
  - Prompt builder
  - Provider-neutral LLM runtime
  - Runtime tracing

Persistence
  - SQLite database
  - Repository-local knowledge documents
  - Rotating AI runtime trace log
```

## Component Responsibilities

### Frontend

- `frontend/app/`: Route entry points and page composition.
- `frontend/app/api/[...path]/route.ts`: Backend proxy for all frontend API calls.
- `frontend/features/doctors/`: Doctor-domain API mapping and frontend types.
- `frontend/features/appointments/`: Booking, confirmation, and search API contracts, hooks, schemas, and utilities.
- `frontend/stores/booking-store.ts`: Request-to-route booking state handoff.
- `frontend/lib/ai-widget/`: Reusable chat UI, local state, response mapping, and navigation hooks.

### Backend Business Runtime

- `backend/app/api/`: Thin HTTP route handlers.
- `backend/app/services/doctor_service.py`: Doctor query orchestration.
- `backend/app/services/availability_service.py`: Bookable slot calculation.
- `backend/app/services/schedule_service.py`: Static schedule generation rules.
- `backend/app/services/appointment_service.py`: Appointment creation and confirmation retrieval.
- `backend/app/services/appointment_search_service.py`: Search behavior over appointments, patients, and doctors.
- `backend/app/services/conversation_manager.py`: Primary chat orchestration entry point.
- `backend/app/services/workflow_engine.py`: Request-scoped booking and support workflows.
- `backend/app/services/chat_service.py`: Deterministic chat fallback and structured response generation.

### Backend AI Runtime

- `backend/app/knowledge/`: Deterministic knowledge loading, caching, and retrieval.
- `backend/app/services/prompt_builder.py`: Deterministic prompt construction pipeline.
- `backend/app/llm/`: Provider-neutral LLM runtime models, configuration, composition, activation, execution policy, orchestration, validation, eligibility, response composition, post-processing, facade, transport, and tracing.

### Persistence

- `backend/app/models/`: SQLAlchemy ORM models for doctors, patients, appointments, and legacy availability.
- `backend/app/repositories/`: Database query and mutation helpers.
- `backend/app/db/database.py`: Engine, session, schema initialization, and startup seeding.

## Runtime Layers

1. Presentation layer: Next.js routes, components, and chat widget.
2. API boundary layer: Next.js proxy and FastAPI route handlers.
3. Business service layer: Doctor, booking, search, workflow, and chat services.
4. Knowledge and AI orchestration layer: retrieval, prompt building, execution policy, facade, and transport.
5. Data access layer: repositories and ORM models.
6. Persistence and file layer: SQLite, knowledge-source files, and runtime trace log file.

## Deployment View

The current deployment shape is local-process oriented:

- Frontend application process running the Next.js app
- Backend application process running FastAPI
- SQLite database file stored at `backend/app.db` by default
- Knowledge files loaded from `backend/app/knowledge/sources/`
- AI runtime trace file written to `logs/ai-runtime-trace.log` when enabled

There is no separate cache tier, queue, worker, vector database, or external state store in the current implementation.

## Integration Points

- Frontend to backend via the Next.js catch-all proxy route.
- Backend to SQLite via SQLAlchemy ORM and repositories.
- Backend chat runtime to knowledge sources via filesystem-backed loader and in-memory repository.
- Backend LLM facade to provider adapters through the provider-neutral orchestration path.
- Claude adapter to Anthropic via the production transport layer.

## External Dependencies

- Next.js 15 and React for frontend runtime.
- FastAPI and Pydantic for backend API and schema handling.
- SQLAlchemy for persistence.
- SQLite for the v1 database.
- Zustand for lightweight frontend shared state.
- Anthropic SDK for live Claude transport.
- Repository-local Markdown and JSON files as knowledge sources.

## Request Lifecycle

### Standard business request

1. User action originates in the browser.
2. Frontend page or feature module calls `frontend/lib/api-client.ts`.
3. Request passes through `frontend/app/api/[...path]/route.ts`.
4. FastAPI route handler validates input and delegates to a service.
5. Service reads or writes through repositories and ORM models.
6. Response is serialized through backend schemas and returned to the frontend.
7. Frontend maps the payload into route-specific UI state.

### Appointment booking request

1. User selects doctor, date, time, and patient details.
2. Frontend submits an appointment creation payload.
3. Backend validates doctor existence, supported appointment type, future date/time, slot validity, and slot availability.
4. Backend creates or reuses the patient record, then inserts the appointment.
5. Frontend stores confirmation state and navigates to the confirmation page.

## AI Runtime Flow

1. Frontend AI widget posts a chat request to the backend chat API.
2. `ConversationManager` builds request-scoped conversation context.
3. `WorkflowEngine` evaluates and executes active or newly detected workflow paths first.
4. If no workflow owns the request, deterministic knowledge retrieval is attempted for FAQ-style prompts.
5. If retrieval does not produce the final response, deterministic chat logic handles the turn.
6. After the official response is chosen, the LLM facade may run shadow or controlled generation depending on runtime activation and execution policy.
7. Controlled generation can only become visible after validation, eligibility, response composition, and post-processing succeed.
8. Final response plus trace summary are returned, and runtime trace emission occurs once from the `ConversationManager` finalization path.

## LLM Runtime

The LLM runtime is implemented as a provider-neutral subsystem under `backend/app/llm/`.

- `config.py` loads runtime flags and provider settings.
- `budget.py` resolves provider-neutral generation-budget profiles.
- `providers.py`, `adapters.py`, `interfaces.py`, and `registry.py` define adapter and registry boundaries.
- `composition.py` assembles transports, adapters, registry, integration service, orchestrator, activation, execution policy, and operational-readiness services.
- `orchestrator.py` transforms prompt-builder output into canonical LLM generation requests.
- `facade.py` is the public runtime boundary used by the chat runtime.
- `validation.py`, `eligibility.py`, `composer.py`, and `post_processor.py` gate and normalize any user-visible controlled output.
- `transport.py` currently provides the live Anthropic-backed Claude transport.

The subsystem is intentionally policy-gated. Workflow-owned requests remain deterministic, and user-visible LLM output is restricted to explicitly approved low-risk conversational paths.

## Configuration Strategy

Configuration is environment-driven.

- Frontend uses `NEXT_PUBLIC_API_BASE_URL` and `BACKEND_API_BASE_URL`.
- Backend core settings define API prefix, CORS behavior, database URL, and tracing flags.
- LLM runtime settings define provider selection, enablement, credentials, transport parameters, feature flags, and budget profiles.
- Deterministic defaults exist so the app can run without activating live provider generation.

## Security Considerations

- All write operations pass through backend validation rather than direct frontend persistence.
- Appointment uniqueness is protected both in service logic and by a database uniqueness constraint.
- The frontend proxy strips connection-sensitive headers before forwarding requests.
- Controlled LLM output is not trusted by default and must pass validation and eligibility gates.
- Runtime tracing redacts common patient PII patterns before trace persistence.
- Conversation state is request-scoped and not persisted as a long-lived chat history store.

## Scalability

The current implementation is optimized for local or small-scale deployment rather than horizontal scale.

- SQLite provides simple single-node persistence.
- Knowledge retrieval is in-memory and file-backed.
- Runtime traces are local file outputs.
- The AI runtime is modular enough to support future provider expansion, but there is no distributed coordination layer in the current design.

## Extensibility

The implementation exposes clear extension seams:

- Additional frontend pages and feature modules can reuse the shared proxy and API client.
- New backend business capabilities can follow the existing route -> service -> repository pattern.
- Knowledge sources can expand by adding Markdown or JSON documents with supported metadata.
- Additional LLM providers can be added through the provider adapter and transport abstractions.
- Execution policy and eligibility rules can evolve without changing the main chat route contract.

## Observability

- Standard backend logging exists through FastAPI and service-level logging.
- `backend/app/llm/runtime_trace.py` provides request-scoped structured AI runtime tracing.
- When `AI_RUNTIME_TRACE=true`, one raw JSON trace is written per chat request to `logs/ai-runtime-trace.log`.
- Trace payloads include routing decisions, stage timing, provider readiness, stop reasons, exceptions, and controlled-generation outcome summaries.

## Error Handling

- Frontend API calls normalize backend failures into a shared `ApiError`.
- FastAPI route handlers rely on schema validation and explicit HTTP exceptions.
- Appointment booking failures remain deterministic and surface as business errors.
- Chat workflow validation failures are mapped back into workflow responses instead of surfacing as infrastructure failures where possible.
- LLM runtime failures fall back safely to deterministic behavior unless an already-approved controlled result has completed all gates successfully.

## Technology Stack

- Frontend: Next.js App Router, React, TypeScript, Tailwind CSS, Zustand
- Backend: FastAPI, Pydantic, SQLAlchemy
- Database: SQLite
- Testing: pytest-based backend test suite
- AI runtime: deterministic orchestration, repository-local knowledge retrieval, provider-neutral LLM architecture, Anthropic-backed Claude transport

## Risks

- SQLite limits write concurrency and multi-node deployment options.
- Conversation and workflow state are not persisted across independent sessions.
- Knowledge retrieval is deterministic and single-document oriented, which constrains recall breadth.
- The legacy `doctor_availability` table remains present and can be misread as the active slot source.
- The live provider transport exists only for Claude; other configured providers remain architecture-ready but not production-connected.

## Assumptions

- The application is currently intended for local development or low-scale deployment.
- Deterministic services remain the source of truth for business-owned operations.
- Appointment availability is generated from schedule rules plus booked appointments, not from the legacy availability table.
- Repository-local documents are the only active knowledge corpus.
- Controlled-generation feature flags and provider credentials may be absent in many environments.

## Future Extension Points

- Persisted conversation storage
- Additional provider transports beyond Claude
- Expanded execution modes and rollout controls
- Richer knowledge retrieval strategies
- External notification integrations
- Stronger deployment isolation for logs, persistence, and provider configuration

## Current Implementation Boundary

This HLD reflects the repository as implemented on 2026-07-09. It documents the current architecture and runtime behavior only. It does not prescribe redesigns or target-state architecture beyond the extension points that already exist in the codebase.
