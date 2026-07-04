# Feature Map

## Active Product Features

### 1. Home / foundation shell

- Status: implemented
- Frontend routes:
  - `frontend/app/page.tsx`
  - `frontend/app/layout.tsx`
- Key behavior:
  - Provides the top-level app shell, navigation entry points, and mounts the global AI widget.

### 2. Doctor listing and filtering

- Status: implemented against live backend data
- Frontend ownership:
  - `frontend/app/doctors/page.tsx`
  - `frontend/components/doctors/DoctorsPageClient.tsx`
  - `frontend/components/doctors/DoctorFilters.tsx`
  - `frontend/components/doctors/DoctorCard.tsx`
  - `frontend/features/doctors/api.ts`
  - `frontend/features/doctors/types.ts`
- Backend ownership:
  - `backend/app/api/doctors.py`
  - `backend/app/services/doctor_service.py`
  - `backend/app/repositories/doctor_repository.py`
  - `backend/app/schemas/doctor.py`
- Current capability:
  - Lists doctors and supports specialty, appointment type, gender, location, and fee filtering at the API level.
  - Frontend currently uses specialty and appointment type filtering plus local sorting/pagination.

### 3. Appointment booking flow

- Status: implemented
- Frontend ownership:
  - `frontend/app/appointments/page.tsx`
  - `frontend/features/appointments/components/AppointmentCalendar.tsx`
  - `frontend/features/appointments/components/AppointmentAvailability.tsx`
  - `frontend/features/appointments/components/PatientDetailsForm.tsx`
  - `frontend/features/appointments/components/DoctorSummaryCard.tsx`
  - `frontend/features/appointments/api.ts`
  - `frontend/features/appointments/schema.ts`
  - `frontend/features/appointments/utils.ts`
  - `frontend/stores/booking-store.ts`
- Backend ownership:
  - `backend/app/api/appointments.py`
  - `backend/app/api/availability.py`
  - `backend/app/services/appointment_service.py`
  - `backend/app/services/availability_service.py`
  - `backend/app/services/schedule_service.py`
  - `backend/app/repositories/appointment_repository.py`
  - `backend/app/repositories/patient_repository.py`
- Current capability:
  - Loads doctor details and date-based availability.
  - Prevents elapsed or already-booked slot selection.
  - Creates appointments and persists patient details.
  - Stores cross-route booking state in Zustand.

### 4. Booking confirmation

- Status: implemented
- Frontend ownership:
  - `frontend/app/appointments/confirmation/page.tsx`
  - `frontend/features/appointments/components/AppointmentSummary.tsx`
- Backend ownership:
  - `backend/app/api/appointments.py`
  - `backend/app/services/appointment_service.py`
- Current capability:
  - Loads confirmation details from the backend by appointment id.
  - Falls back to stored booking state when available.

### 5. Appointment search / retrieval

- Status: implemented
- Frontend ownership:
  - `frontend/app/appointments/search/page.tsx`
  - `frontend/features/appointments/hooks/use-appointment-search.ts`
  - `frontend/features/appointments/components/AppointmentResultCard.tsx`
  - `frontend/features/appointments/components/AppointmentDetailsPanel.tsx`
  - `frontend/features/appointments/api.ts`
- Backend ownership:
  - `backend/app/api/appointments.py`
  - `backend/app/services/appointment_search_service.py`
  - `backend/app/schemas/appointment_search.py`
- Current capability:
  - Searches appointments by patient name, email, or phone.
  - Returns ordered result cards and detailed appointment records.

### 6. AI chat assistant

- Status: implemented as a rule-based assistant with a live backend API; Vector-less RAG backend knowledge repository and deterministic retrieval service are now integrated into `ConversationManager` as a read-only fallback when no workflow is active
- Frontend ownership:
  - `frontend/components/layout/GlobalAiWidget.tsx`
  - `frontend/lib/ai-widget/components/*`
  - `frontend/lib/ai-widget/services/api-service.ts`
  - `frontend/lib/ai-widget/services/chat-response-mapper.ts`
  - `frontend/lib/ai-widget/services/appointment-navigation.ts`
- Backend ownership:
  - `backend/app/api/chat.py`
  - `backend/app/services/conversation_manager.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/services/prompt_builder.py`
  - `backend/app/services/chat_service.py`
  - `backend/app/services/chat_intent_detector.py`
  - `backend/app/services/chat_entity_extractor.py`
  - `backend/app/schemas/chat.py`
  - `backend/app/knowledge/documents.py`
  - `backend/app/knowledge/loader.py`
  - `backend/app/knowledge/repository.py`
  - `backend/app/knowledge/retrieval.py`
  - `backend/app/knowledge/sources/`
- Current capability:
  - Answers greetings and help flows.
  - Returns structured doctor lists, doctor details, and availability cards.
  - Resolves doctor-details/profile prompts for partial `Dr. <first-name>` mentions when the name uniquely matches a seeded doctor.
  - Understands specialization, gender, fee, location, date, and time preference cues.
  - Maintains request-scoped multi-turn conversation context through a single orchestration entry point.
  - Keeps the booking workflow active across incremental chat turns, merges collected draft fields, and auto-books through the existing backend appointment service once the mandatory booking fields are complete.
  - Accepts direct booking-entry prompts that mention a doctor plus incremental follow-up fields, including explicit day-month-year dates and labeled patient details in structured messages.
  - Consults the knowledge retrieval service only when no workflow is active and uses the retrieved document before the legacy deterministic fallback for FAQ-style non-workflow turns.
  - Returns optional `knowledge_source` metadata on knowledge-backed replies so downstream UI mapping can show the retrieved document source.
  - Displays a minimal knowledge-source footer on assistant text replies in the existing chat widget while preserving workflow cards and booking navigation.
  - Redirects successful chat-driven bookings into the existing appointment confirmation page.
  - Loads curated Markdown and JSON knowledge files into an in-memory backend repository for future prompt/context work.
  - Supports deterministic top-document retrieval over repository documents with weighted title, alias, keyword, synonym, category, and body-text matching while filtering broad tokens that would otherwise interfere with doctor-search, availability, fee, or unrelated fallback flows.
  - Exposes an inactive standalone Prompt Builder seam that can be instantiated independently to format already-selected context into bounded prompt text without changing live chat behavior.
  - Resolves informational FAQ prompts such as online consultation, payment methods, appointment preparation, consultation hours, insurance, and parking through the knowledge layer before the legacy deterministic fallback when no workflow is active.
  - Includes a dedicated manual test checklist that covers positive, negative, edge, regression, workflow, and existing chatbot scenarios.
- Limitation:
  - The frontend mounts a noop adapter, so chat responses are present but automation/navigation remains limited.
  - Conversation and workflow state are not persisted beyond the request metadata loop used by the current widget.
  - Knowledge retrieval is still backend-only and deterministic; it is not used by prompt building, LLM calls, embeddings, or a vector database, and it remains inactive while a workflow is running.

## Platform / Cross-Cutting Features

### API proxying

- `frontend/app/api/[...path]/route.ts` forwards all frontend API requests to FastAPI.

### AI architecture reference documentation

- `docs/analysis/hybrid-ai-assistant-architecture/hybrid-ai-assistant-master-architecture.md`
- `docs/analysis/hybrid-ai-assistant-architecture/adr-001-deterministic-ai-engine-primary.md`
- `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`
- These documents define the current layered architecture, boundaries, request flow, and incremental migration path for the AI assistant without changing runtime behavior.

### Database initialization and seed data

- `backend/app/db/database.py` initializes schema and runs seeding on app startup.
- `backend/app/db/seed.py` owns seed doctor data.

### Test coverage

- Backend tests cover appointment creation, appointment search, availability behavior, doctor filtering, chat API behavior, and chat parsing services.

## Not Yet Implemented Or Not Evident In Current App

- Confirmation email sending is still documented as a feature area but no active SMTP/email service is evident in the current backend route/service flow.
- AI-driven browser automation is not wired into the current frontend adapter or backend service layer.
