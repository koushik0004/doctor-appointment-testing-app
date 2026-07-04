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
- `backend/scripts/seed_test_data.py`
  - Idempotent manual-test data seeding utility; now adds extra doctor demo profiles, books a small set of valid future appointments through the service layer, pins the default DB target to `backend/app.db`, and writes `docs/reports/test-data-report.md`.
- `docs/reports/test-data-health-report.md`
  - Latest zero-write data-health audit for `backend/app.db`; records schema validation, retained legacy availability issues, and explicit no-data-loss decisions.

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
- `frontend/lib/ai-widget/services/chat-response-mapper.ts`
  - Maps backend chat payloads into assistant messages and preserves optional workflow and knowledge source metadata.
- `frontend/lib/ai-widget/components/MessageContentRenderer.tsx`
  - Renders assistant chat content and the minimal knowledge-source footer for text replies.
- `frontend/lib/ai-widget/types/chat.ts`
  - Shared chat payload contract including optional `knowledge_source` metadata from backend responses.
- `frontend/lib/ai-widget/types/message.ts`
  - Widget message metadata shape used by the renderer and workflow navigation hook.

## Core Backend Feature Files

- `backend/app/api/doctors.py`
  - Doctor listing/detail API surface.
- `backend/app/api/availability.py`
  - Doctor availability endpoint used by booking UI and chat.
- `backend/app/api/appointments.py`
  - Appointment creation, appointment details, and appointment search API surface.
- `backend/app/api/chat.py`
  - Chat endpoints for `/api/chat` and `/api/v1/chat`; expected workflow/business errors should pass through while only unexpected chat failures become HTTP 500 responses.
- `backend/app/services/conversation_manager.py`
  - Single orchestration entry point for chat requests; maintains conversation context, merges extracted entities, preserves workflow-first execution, and uses knowledge retrieval before deterministic fallback for FAQ-style non-workflow turns.
- `backend/app/services/workflow_engine.py`
  - Request-scoped workflow executor for booking, cancellation, confirmation lookup, missing-field validation, and multi-turn booking draft continuation; direct doctor-reference booking entry and draft-merging regressions are validated against this file.
- `backend/app/services/prompt_builder.py`
  - Inactive standalone prompt-construction module with a canonical provider-agnostic `PromptContext` model and a deterministic renderer for caller-supplied user message, conversation state, and preselected knowledge documents; it does not do retrieval, routing, workflow execution, API calls, or database access.
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
  - Extracts specialization, gender, fee, location, date, and time preferences from messages; word-boundary matching avoids false gender inference on unrelated informational prompts, and explicit absolute date parsing now supports booking workflow turns such as `2nd July 2026` or `02/07/2026`.
- `backend/app/services/schedule_service.py`
  - Slot-generation rules that shape both booking and chat availability results.
- `backend/app/knowledge/documents.py`
  - Typed Vector-less RAG knowledge document schema and prompt hint metadata, including additive retrieval fields for `category`, `keywords`, `synonyms`, and `aliases`.
- `backend/app/knowledge/loader.py`
  - Filesystem loader for repository-local Markdown and JSON knowledge files; performs schema validation and duplicate ID checks.
- `backend/app/knowledge/repository.py`
  - In-memory cache for loaded knowledge documents with exact ID/domain/tag accessors only.
- `backend/app/knowledge/retrieval.py`
  - Deterministic Vector-less RAG retrieval service that scores title, alias, keyword, synonym, category, and body-text matches separately, filters overly broad tokens, and returns one top document.
- `backend/app/knowledge/sources/`
  - Curated passive Markdown/JSON knowledge sources for future prompt/context work, including booking, cancellation, consultation-hours, telemedicine, appointment-preparation, payment-methods, insurance, and parking FAQs.
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
  - Chat request/response contracts including optional conversation metadata, workflow state/result metadata, and knowledge source metadata.

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
  - Covers Markdown/JSON loading, repository caching, exact filters, metadata-aware deterministic retrieval matching, and bundled FAQ retrieval expectations.
- `backend/tests/test_conversation_manager.py`
  - Covers routing order guarantees: workflow-first, knowledge-before-deterministic fallback, and active-workflow exclusion from retrieval.
- `backend/tests/test_chat_entity_extractor.py`
  - Covers search-filter extraction regressions, including the payment-method wording that must not infer a doctor-gender filter.
- `backend/tests/test_prompt_builder_service.py`
  - Covers the inactive prompt-builder seam: `PromptContext` creation, optional section/default behavior, deterministic block assembly, prompt-hint constraints, and character-budget truncation without touching the live request flow.

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
- `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-04-manual-test-checklist.md`
  - Manual QA checklist for the Vector-less RAG prototype, including positive, negative, edge, regression, workflow, and existing chatbot coverage.
- `docs/reports/test-data-report.md`
  - Latest manual-test data execution report with row counts, inserted demo bookings, duplicate handling, and validation notes.
