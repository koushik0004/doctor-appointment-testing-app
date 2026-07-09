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
  - `backend/app/llm/`
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
  - Routes eligible low-risk chat requests through the existing runtime facade's controlled-generation path after the official response is chosen, while preserving workflow ownership, doctor search, availability, and other business-owned paths as deterministic.
  - When `AI_RUNTIME_TRACE=true`, emits a structured backend-only end-to-end trace for each chat request through an independent `ai.runtime.trace` rotating file logger, including routing decisions, prompt/orchestration progress, provider transport activity, deterministic `entered`/`completed`/`duration_ms`/`status` stage markers, explicit `llm_not_invoked` stop reasons, and a final raw JSON request summary written exactly once to `logs/ai-runtime-trace.log` from the `ConversationManager` `finally` block.
  - Phase 7.3 ensures every hidden shadow execution reaches the full Prompt Builder -> Prompt Renderer -> Orchestrator path, including canonical workflow context in the rendered prompt sent to provider adapters.
  - Phase 7.4 adds policy-gated controlled runtime generation through the existing facade, with generation only occurring when runtime activation and execution policy explicitly allow an LLM-capable mode.
  - Phase 7.5 adds a provider-neutral runtime-response validation gate on the facade so controlled generation is validated before any future visible LLM response and safely falls back on empty, malformed, or otherwise invalid canonical output.
  - Phase 7.6 adds a provider-neutral runtime-response eligibility gate on the facade so only explicitly approved low-risk conversational responses can be exposed to the user after validation while workflow-owned requests remain deterministic.
  - Phase 7.7 adds a provider-neutral runtime-response composer on the facade so deterministic-only, LLM-only, and hybrid final responses can preserve business truth while optionally appending validated and eligible LLM guidance.
  - Phase 7.8 adds a provider-neutral runtime-response post processor on the facade so composed responses are normalized for presentation and presentation-only metadata is sanitized before frontend visibility.
  - The July 8 runtime-trace follow-up adds a final controlled-generation diagnostic summary so every SKIPPED or FAILED run records execution mode, provider readiness, orchestration progress, stage-by-stage execution flags, fallback reason, and exception details before the trace is emitted, while the broader observability layer writes a single rotating JSON trace per request.
  - Claude provider execution now sanitizes outbound Anthropic request serialization so internal routing, execution, and trace metadata remain in backend observability only and unsupported fields are not forwarded into `messages.create(...)`.
  - Contains a provider-neutral LLM seam with canonical models, generation-budget profiles, concrete provider adapters, a single runtime composition root that assembles configuration, transports, adapters, registry, integration service, orchestrator, execution-policy service, and operational-readiness service, plus a runtime activation layer that evaluates feature-flag and provider-readiness diagnostics; Phase 8 now gives Claude a real Anthropic-backed production transport while the rest of the live chat runtime remains deterministic by default.
  - Adds an inactive runtime facade that wraps the composed LLM subsystem and captures a deterministic, save-ready integration snapshot without changing chat routing or provider execution.
  - Accepts direct booking-entry prompts that mention a doctor plus incremental follow-up fields, including explicit day-month-year dates and labeled patient details in structured messages.
  - Consults the knowledge retrieval service only when no workflow is active and uses the retrieved document before the legacy deterministic fallback for FAQ-style non-workflow turns.
  - Returns optional `knowledge_source` metadata on knowledge-backed replies so downstream UI mapping can show the retrieved document source.
  - Displays a minimal knowledge-source footer on assistant text replies in the existing chat widget while preserving workflow cards and booking navigation.
  - Redirects successful chat-driven bookings into the existing appointment confirmation page.
  - Loads curated Markdown and JSON knowledge files into an in-memory backend repository for future prompt/context work.
  - Supports deterministic top-document retrieval over repository documents with weighted title, alias, keyword, synonym, category, and body-text matching while filtering broad tokens that would otherwise interfere with doctor-search, availability, fee, or unrelated fallback flows.
  - Exposes an inactive standalone Prompt Builder seam that now normalizes caller inputs into a canonical internal `PromptContext` model, uses internal Conversation, Workflow, and Knowledge Context Collectors plus a System Instruction Builder to normalize conversation state, workflow state, already-selected documents, and system instructions deterministically, validates that context, assembles ordered prompt sections through a dedicated Prompt Assembly Pipeline, and delegates final bounded prompt rendering and truncation to a dedicated PromptRenderer without changing live chat behavior.
  - Exposes an additional inactive provider-neutral LLM Integration seam under `backend/app/llm/` that defines future message/request/response contracts plus provider translator, adapter, registry, generation-orchestration, provider-configuration, generation-budget, runtime-activation, execution-policy, and operational-readiness boundaries; the canonical contract now also supports provider-neutral structured-output, tool-calling, reasoning, streaming, citation, provider/model metadata, multimodal-intent fields, and optional reusable generation-budget profiles, while inactive configuration can represent provider selection, model, key, base URL, timeout, retry, feature-flag, and profile-override settings without integrating any SDK or changing runtime routing.
  - Resolves informational FAQ prompts such as online consultation, payment methods, appointment preparation, consultation hours, insurance, and parking through the knowledge layer before the legacy deterministic fallback when no workflow is active.
  - Includes a dedicated manual test checklist that covers positive, negative, edge, regression, workflow, and existing chatbot scenarios.
- Limitation:
  - The frontend mounts a noop adapter, so chat responses are present but automation/navigation remains limited.
  - Conversation and workflow state are not persisted beyond the request metadata loop used by the current widget.
  - Knowledge retrieval is still backend-only and deterministic; it is not used by the inactive Prompt Builder seam, the inactive LLM Integration seam or its inactive provider registry, embeddings, or a vector database, and it remains inactive while a workflow is running.
  - The runtime facade still does not alter default assistant routing or persist state; Claude transport now exists behind the facade, and low-risk user-visible chat can now enter controlled generation when execution policy explicitly allows it.
  - The `backend/app/llm/__init__.py` package initializer now lazily re-exports its public symbols so importing `app.llm.runtime_trace` from knowledge retrieval does not re-enter the orchestrator/prompt-builder chain during startup.

## Platform / Cross-Cutting Features

### API proxying

- `frontend/app/api/[...path]/route.ts` forwards all frontend API requests to FastAPI.

### Whole-repository architecture reverse engineering

- `docs/reports/architecture/reverse-engineering-report.md`
- Current capability:
  - Documents the implemented repository architecture end to end across frontend, backend, database, deterministic AI chat, knowledge retrieval, prompt builder, provider-neutral LLM runtime, Claude transport, tracing, configuration, and tests.

### Whole-repository high level design

- `docs/reports/architecture/HLD.md`
- Current capability:
  - Documents the same current implementation as an enterprise-oriented HLD covering business scope, architectural layers, deployment, runtime lifecycle, AI and LLM boundaries, security, observability, risks, assumptions, and extension points.

### Whole-repository low level design

- `docs/reports/architecture/LLD.md`
- Current capability:
  - Documents the same current implementation as a low-level design covering folder and package structure, module and class responsibilities, interfaces, data models, internal request and response flow, configuration, API contracts, runtime state flow, Mermaid diagrams, and code-backed extension seams.

### Whole-platform master architecture

- `docs/reports/architecture/architecture.md`
- Current capability:
  - Consolidates the current implementation into a single system-architecture reference focused on architectural vision, layered boundaries, AI runtime structure, conversation and workflow control, knowledge and prompt architecture, provider-neutral LLM design, controlled generation, observability, deployment shape, extension strategy, and enterprise considerations without dropping to code-level detail.

### AI runtime sequence diagram reference

- `docs/reports/architecture/AI-Runtime-Sequence-Diagrams.md`
- Current capability:
  - Documents the implemented AI runtime as scenario-specific Mermaid sequence diagrams covering greeting flow, deterministic routing, workflow ownership, vector-less knowledge retrieval, controlled generation, prompt building, provider execution, validation, post-processing, runtime tracing, provider failure, fallback, and the complete end-to-end path.

### AI Assistant API design reference

- `docs/reports/architecture/AI-Assistant-API-Design.md`
- Current capability:
  - Documents the implemented AI-only REST endpoints, conversation contracts, workflow/knowledge/prompt/LLM runtime APIs, routing decision matrix, internal DTOs, sequence mappings, error handling, and production-facing runtime behavior without including non-AI application APIs.

### AI Assistant source-code architecture reference

- `docs/reports/architecture/AI-Assistant-Source-Code-Architecture.md`
- Current capability:
  - Documents the implemented AI Assistant backend and Chat Widget source-code structure, including repository tree, backend and frontend AI folder responsibilities, startup and runtime entry points, important file responsibilities, configuration surfaces, and folder-to-runtime mapping without covering unrelated appointment-domain modules.

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
