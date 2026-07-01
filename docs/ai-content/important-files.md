# Important Files

## Highest Priority Runtime Files

- `frontend/app/layout.tsx`
  - Root shell for every page; mounts header, footer, and the global AI widget.
- `frontend/app/api/[...path]/route.ts`
  - Central frontend-to-backend proxy. Changes here affect every API call.
- `frontend/lib/api-client.ts`
  - Shared fetch wrapper and error normalization used across frontend features.
- `backend/app/main.py`
  - FastAPI app entry point and startup lifecycle.
- `backend/app/api/router.py`
  - Registers all API domains in one place.
- `backend/app/db/database.py`
  - Engine/session creation, schema initialization, and startup seeding.

## Core Frontend Feature Files

- `frontend/components/doctors/DoctorsPageClient.tsx`
  - Main doctor listing UI and filter/sort/pagination orchestration.
- `frontend/features/doctors/api.ts`
  - Maps backend doctor records to frontend doctor view models.
- `frontend/app/appointments/page.tsx`
  - Main booking flow container and orchestration layer.
- `frontend/features/appointments/api.ts`
  - Frontend contract for availability, booking, confirmation, and search endpoints.
- `frontend/features/appointments/schema.ts`
  - Booking form validation and appointment-type labels.
- `frontend/features/appointments/utils.ts`
  - Slot/date helpers used throughout the booking flow.
- `frontend/stores/booking-store.ts`
  - Shared cross-route booking state for doctor, slot, patient, and confirmation data.
- `frontend/app/appointments/search/page.tsx`
  - Appointment retrieval/search UI.
- `frontend/app/appointments/confirmation/page.tsx`
  - Confirmation page fed by backend appointment details.
- `frontend/components/layout/GlobalAiWidget.tsx`
  - Single mount point for the AI assistant UI and the chat-booking confirmation redirect hook.
- `frontend/lib/ai-widget/services/api-service.ts`
  - Bridges widget requests to the backend chat API.

## Core Backend Feature Files

- `backend/app/api/doctors.py`
  - Doctor listing/detail API surface.
- `backend/app/api/availability.py`
  - Doctor availability endpoint used by booking UI and chat.
- `backend/app/api/appointments.py`
  - Appointment creation, appointment details, and appointment search API surface.
- `backend/app/api/chat.py`
  - Chat endpoints for `/api/chat` and `/api/v1/chat`.
- `backend/app/services/conversation_manager.py`
  - Single orchestration entry point for chat requests; maintains conversation context, merges extracted entities, routes between workflow execution and deterministic fallback, and consults knowledge retrieval only when no workflow is active.
- `backend/app/services/workflow_engine.py`
  - Request-scoped workflow executor for booking, cancellation, confirmation lookup, missing-field validation, and multi-turn booking draft continuation.
- `backend/app/services/doctor_service.py`
  - Doctor-domain response shaping and filter delegation.
- `backend/app/services/availability_service.py`
  - Computes bookable slots from schedule rules plus booked appointments.
- `backend/app/services/appointment_service.py`
  - Main booking rules plus cancellation and confirmation lookup business APIs reused by chat workflows.
- `backend/app/services/appointment_search_service.py`
  - Appointment search behavior across patient and doctor joins.
- `backend/app/services/chat_service.py`
  - Deterministic execution engine for the AI assistant and structured chat responses, including doctor-details matching and the knowledge-backed fallback composer.
- `backend/app/services/chat_intent_detector.py`
  - Intent classification entry point for chat behavior, including doctor-profile/detail query routing.
- `backend/app/services/chat_entity_extractor.py`
  - Extracts specialization, gender, fee, location, date, and time preferences from messages.
- `backend/app/services/schedule_service.py`
  - Slot-generation rules that shape both booking and chat availability results.
- `backend/app/knowledge/documents.py`
  - Typed Vector-less RAG knowledge document schema and prompt hint metadata.
- `backend/app/knowledge/loader.py`
  - Filesystem loader for repository-local Markdown and JSON knowledge files; performs schema validation and duplicate ID checks.
- `backend/app/knowledge/repository.py`
  - In-memory cache for loaded knowledge documents with exact ID/domain/tag accessors only.
- `backend/app/knowledge/retrieval.py`
  - Deterministic Vector-less RAG retrieval service that scores title matches above summary/content/tag keyword matches and returns one top document.
- `backend/app/knowledge/sources/`
  - Curated passive Markdown/JSON knowledge sources for future prompt/context work.
- `backend/pyproject.toml`
  - Backend package/test configuration, including package-data entries for bundled knowledge Markdown/JSON sources.

## Data Model And Contract Files

- `backend/app/models/doctor.py`
- `backend/app/models/appointment.py`
- `backend/app/models/patient.py`
- `backend/app/schemas/doctor.py`
- `backend/app/schemas/availability.py`
- `backend/app/schemas/appointment.py`
- `backend/app/schemas/appointment_search.py`
- `backend/app/schemas/chat.py`
  - Chat request/response contracts including optional conversation metadata and workflow state/result metadata.

These files define the persistence and API contracts. Any API change should be checked against both the frontend feature API files and these backend schemas/models.

## High-Value Tests

- `backend/tests/test_doctors_api.py`
- `backend/tests/test_availability_service.py`
- `backend/tests/test_appointments_api.py`
- `backend/tests/test_appointment_search_service.py`
- `backend/tests/test_chat_api.py`
- `backend/tests/test_chat_intent_detector.py`
- `backend/tests/test_chat_entity_extractor.py`
- `backend/tests/test_knowledge_repository.py`
  - Covers Markdown/JSON loading, repository caching, exact filters, and deterministic retrieval matching.

## High-Value Docs

- `docs/architecture.md`
- `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md`
- `docs/analysis/hybrid-ai-assistant-architecture/adr-001-deterministic-ai-engine-primary.md`
- `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`
- `docs/project-context.md`
- `docs/frontend-spec.md`
- `docs/backend-spec.md`
- `docs/feature-02-doctor-listing.md`
- `docs/feature-03-appointment-booking.md`
- `docs/feature-04-confirmation-email.md`
