# Current Task

## Active Work

- Status: completed
- Task: implement Phase 7.5 provider-neutral runtime response validation
- Completed on: 2026-07-05

## Outcome

- Added a provider-neutral runtime-response validation seam under `backend/app/llm/validation.py` and wired the `LLMRuntimeFacade` to validate controlled generation results before exposing any generated runtime output.
- Kept runtime behavior safe by rejecting empty, whitespace-only, malformed-structured-output, invalid-finish-reason, and invalid-metadata cases through deterministic fallback without exposing provider or validation internals.
- Added focused backend tests covering valid runtime responses, empty and whitespace rejection, malformed structured-output rejection, invalid finish reasons, diagnostics, and deterministic fallback after validation failure.
- Updated the Phase 7 architecture/report documentation plus the compact AI context files so future sessions can find the runtime-response validation seam directly.

## Prior Work

- Status: completed
- Task: implement Phase 7.2 shadow-mode integration through the runtime facade without changing user-visible chat behavior
- Completed on: 2026-07-05

## Outcome

- Extended `backend/app/llm/facade.py` so the runtime facade can evaluate the existing shadow execution policy, run the existing prompt-builder and orchestrator pipeline in the background, capture provider-neutral diagnostics, and discard all LLM output.
- Wired `ConversationManager` to trigger the facade after the normal chat response is finalized, while preserving workflow, knowledge, and deterministic ownership exactly as before and swallowing any shadow-mode failure.
- Added focused backend tests covering successful shadow execution, skipped shadow execution, failure capture, facade-trigger integration from `ConversationManager`, and the guarantee that visible responses remain unchanged.
- Updated the Phase 7 architecture/report documentation plus the compact AI context files so future sessions can discover the shadow-mode boundary and diagnostics trail directly.

## Prior Work

- Status: completed
- Task: implement Phase 7 inactive runtime facade and save-ready integration boundary for the LLM seam
- Completed on: 2026-07-05

## Outcome

- Added `backend/app/llm/facade.py` with an inactive runtime facade and deterministic save-ready snapshot model for the composed LLM boundary.
- Kept the facade architecture-only by wrapping the existing `LLMRuntimeCompositionRoot` without changing chat routing, provider execution, prompt building, or runtime activation.
- Added focused backend tests covering facade composition caching, boundary snapshot generation, and deterministic serialization of the save-ready facade view.
- Updated the LLM integration architecture reference, `backend/app/llm/__init__.py`, and the compact AI context files so later sessions can discover the new runtime facade directly.

## Prior Work

- Status: completed
- Task: implement Phase 6.9 inactive execution-policy and runtime-routing architecture for the LLM seam
- Completed on: 2026-07-05

## Outcome

- Added `backend/app/llm/execution_policy.py` with canonical execution modes, ownership and fallback models, activation snapshots, deterministic routing diagnostics, a policy evaluator, and a composition-backed policy service.
- Updated `backend/app/llm/composition.py` so each composed inactive graph now also assembles the execution-policy seam alongside the existing activation, registry, service, and orchestrator seams.
- Preserved the existing ownership hierarchy by encoding workflow-first, deterministic knowledge second, deterministic-chat default, and optional activation-aware `LLM_ONLY`, `HYBRID`, and `SHADOW` routing decisions without touching the live `ConversationManager`.
- Added focused backend tests covering workflow ownership, knowledge ownership, deterministic default routing, activation-aware shadow routing, fallback routing, execution-decision serialization, composed-policy access, and deterministic decisions.
- Updated the execution-policy architecture reference, the activation/integration/composition references, the Phase 6 report set, and the compact AI context files so later sessions can discover the routing seam directly.

## Prior Work

- Status: completed
- Task: implement Phase 6.8 inactive runtime activation and feature-flag architecture for the LLM seam
- Completed on: 2026-07-05

## Outcome

- Added `backend/app/llm/activation.py` with canonical runtime activation diagnostics, provider-readiness status, overall activation status, a deterministic evaluator, and a safe activation service.
- Extended `backend/app/llm/config.py` with top-level runtime feature flags for `LLM_ENABLED`, `LLM_SHADOW_MODE`, `LLM_ALLOW_GENERATION`, `LLM_ALLOW_STREAMING`, `LLM_ALLOW_TOOL_CALLING`, and `LLM_ALLOW_REASONING` while keeping provider enablement in the existing provider-scoped settings.
- Updated `backend/app/llm/composition.py` so each composed inactive graph now carries a deterministic activation-status snapshot derived from resolved configuration, adapters, and transports.
- Added focused backend tests covering feature-flag evaluation, readiness evaluation, disabled providers, missing transports, invalid configuration, inactive mode, successful activation state, and deterministic activation decisions.
- Updated the runtime activation architecture reference, the LLM integration and runtime composition references, the Phase 6 report set, `.env.example`, and the compact AI context files so later sessions can discover the activation seam directly.

## Prior Work

- Status: completed
- Task: implement Phase 6.7 inactive runtime composition and dependency assembly for the LLM seam
- Completed on: 2026-07-05

## Outcome

- Added `backend/app/llm/composition.py` with a single inactive `LLMRuntimeCompositionRoot` that loads canonical configuration once, creates provider transports separately, instantiates enabled adapters, builds the registry, resolves the default provider, and composes `LLMIntegrationService` plus `LLMGenerationOrchestrator`.
- Added a dedicated `LLMProviderTransportFactory` seam with an `InactiveLLMProviderTransportFactory` default so the assembled subsystem stays disconnected from any live provider runtime.
- Tightened the inactive dependency rules by making `LLMIntegrationService` and `LLMGenerationOrchestrator` constructor-composed only and moving registry construction out of `LLMProviderAdapterFactory`.
- Added focused backend tests covering deterministic composition-root caching, one-time configuration loading, enabled-provider-only registration, disabled-provider exclusion, transport injection, explicit orchestrator/service composition, and continued inactive behavior without transports.
- Updated the LLM runtime composition architecture reference, LLM integration architecture reference, Phase 6 report set, and compact AI context files so future sessions can discover the composed inactive dependency graph directly.

## Prior Work

- Status: completed
- Task: implement Phase 6.5.5 inactive provider-neutral generation budget architecture for the LLM seam
- Completed on: 2026-07-05

## Outcome

- Added an inactive `backend/app/llm/budget.py` seam with canonical generation-budget enums, reusable default profiles, deterministic profile catalogs, override support, and an adapter-facing translation protocol for future provider-private budget mapping.
- Extended the canonical `LLMGenerationRequest` contract with an optional provider-neutral `generation_budget` field while preserving full backward compatibility and keeping `LLMGenerationOrchestrator` unchanged.
- Extended `backend/app/llm/config.py` plus `.env.example` so global and per-provider configuration can declare default generation profiles and canonical profile overrides without wiring any provider runtime.
- Added focused backend tests covering budget validation, profile resolution, serialization, provider neutrality, config integration, and backward-compatible request defaults.
- Updated the LLM integration architecture reference, Phase 6 report set, and compact AI context files so future sessions can discover the new inactive generation-budget seam directly.

## Prior Work

- Status: completed
- Task: implement Phase 6.5 inactive provider configuration architecture for the provider-neutral LLM seam
- Completed on: 2026-07-05

## Outcome

- Added an inactive `backend/app/llm/config.py` layer with canonical provider-neutral configuration models, provider enums, feature-flag models, explicit validation rules, and a deterministic loader over nested environment-backed settings.
- Added root `.env.example` documentation for global and provider-specific LLM configuration variables covering OpenAI, Claude, Gemini, OpenRouter, and Ollama without wiring any SDK or runtime execution path.
- Added focused backend tests covering deterministic config loading, missing optional keys, missing required keys, selected-provider validation, default propagation, nested environment mapping, and backward-compatible inactive defaults.
- Updated the LLM integration architecture reference, Phase 6 report set, and compact AI context files so future sessions can discover the new inactive configuration seam directly.

## Prior Work

- Status: completed
- Task: implement Phase 6.4 inactive LLM generation orchestrator for the provider-neutral LLM seam
- Completed on: 2026-07-04

## Outcome

- Added an inactive `LLMGenerationOrchestrator` under `backend/app/llm/` that only coordinates `PromptBuilderService`, canonical `LLMGenerationRequest` construction, `LLMIntegrationService` delegation, and normalized provider-neutral result shaping.
- Introduced dedicated orchestration request/result models for already-collected generation input while preserving the existing Prompt Builder contract and the Phase 6.3 canonical LLM request/response models unchanged.
- Added focused backend tests covering orchestration order, deterministic canonical transformation, delegation behavior, inactive-by-default runtime status, and no caller-input mutation.
- Updated the Phase 6 architecture/report/context documentation so future sessions can discover the orchestration seam directly from the compact AI context files.

## Prior Work

- Status: completed
- Task: implement Phase 6.3 canonical LLM request/response contract refinement for the inactive LLM integration seam
- Completed on: 2026-07-04

## Outcome

- Refined `backend/app/llm/models.py` so the canonical internal LLM contract can represent future provider-neutral model selection, structured output, tool definitions and tool calls, reasoning controls and metadata, streaming intent and streaming metadata, citations, provider/model metadata, and multimodal request intent without exposing any provider-specific payload shape.
- Preserved full backward compatibility by keeping all new request and response fields optional and leaving the inactive adapter, registry, and integration-service boundaries unchanged.
- Added focused backend model tests covering canonical validation, deterministic serialization, backward-compatible defaults, optional field handling, and future extensibility while keeping provider tests and runtime wiring out of scope.
- Updated the Phase 6 architecture/report/context documentation so future sessions can discover the refined canonical contract directly from the compact AI context files.

## Prior Work

- Status: completed
- Task: implement Phase 6.2 provider abstraction for the inactive LLM integration seam
- Completed on: 2026-07-04

## Outcome

- Refined the inactive `backend/app/llm/` seam with explicit request-translation and response-translation contracts so future provider adapters can keep provider-native payloads private.
- Added a shared `BaseLLMProviderAdapter` pipeline that turns canonical `LLMGenerationRequest` input into provider-native payloads, invokes a future provider privately, and translates the result back into canonical `LLMGenerationResponse` output.
- Added an inactive `InMemoryLLMProviderRegistry` implementation with deterministic listing, lookup, duplicate-name rejection, and optional default-provider resolution, and updated `LLMIntegrationService` to honor an explicit registry default when present.
- Kept `ConversationManager`, `WorkflowEngine`, Vector-less RAG retrieval, Prompt Builder, frontend contracts, APIs, and the database unchanged and still fully disconnected from any provider runtime.
- Expanded focused tests and architecture/context documentation so later phases can build concrete provider adapters without changing upstream canonical contracts.

## Prior Work

- Status: completed
- Task: implement Phase 6.1 provider-neutral LLM integration architecture seam
- Completed on: 2026-07-04

## Outcome

- Added a new inactive backend `app.llm` package that defines provider-neutral LLM integration contracts without wiring any part of the production runtime to an external model.
- Introduced implementation-ready internal models for messages, generation requests/responses, constraints, token usage, finish reasons, provider capabilities, and provider descriptors.
- Added protocol boundaries for future provider adapters and provider registries plus an inactive `LLMIntegrationService` facade that reports disconnected status by default and only delegates generation when an explicit registry is supplied.
- Kept `ConversationManager`, `WorkflowEngine`, Vector-less RAG retrieval, Prompt Builder, frontend contracts, APIs, and the database unchanged.
- Added focused backend tests plus Phase 6 architecture/report documentation and refreshed the compact AI context files so future sessions can discover the new seam directly.

## Prior Work

- Status: completed
- Task: implement Phase 5.8 dedicated prompt renderer
- Completed on: 2026-07-04

## Outcome

- Added an internal deterministic `PromptRenderer` beneath the Prompt Assembly Pipeline so ordered `PromptAssemblySection` instances are rendered through a dedicated final stage instead of inside `PromptBuilderService`.
- Moved section rendering, optional section-header handling, prompt joining, total prompt truncation, and truncation-marker application out of `PromptBuilderService` while preserving the exact rendered prompt output and the existing `PromptBuildRequest` and `PromptBuildResult` contracts.
- Refactored `PromptBuilderService` into a thinner orchestrator that now builds context, validates it, assembles sections, delegates final rendering to `PromptRenderer`, and then returns the backward-compatible build result.
- Expanded focused backend tests to cover deterministic renderer behavior, header-enabled and header-disabled rendering, empty section rendering, truncation handling, repeated rendering determinism, read-only behavior, and PromptBuilderService integration with the renderer.
- Updated the architecture reference and AI context files so later sessions can treat `PromptRenderer` as the final deterministic stage of the inactive Prompt Builder pipeline.

## Prior Work

- Status: completed
- Task: implement Phase 5.7 deterministic prompt assembly pipeline
- Completed on: 2026-07-04

## Outcome

- Added an internal deterministic Prompt Assembly Pipeline beneath the inactive backend Prompt Builder so validated `PromptContext` instances are converted into ordered renderable prompt sections before rendering.
- Introduced an intermediate assembly-section model that preserves section kind, label, content, and metadata while automatically omitting empty sections and keeping section assembly separate from rendering.
- Refactored `PromptBuilderService` to delegate ordered section assembly to the pipeline, then derive the legacy `blocks` result contract from assembled sections while preserving the existing rendered prompt output exactly.
- Expanded focused backend tests to cover section ordering, omission of empty sections, repeated-build determinism, renderer compatibility, read-only behavior, and backward-compatible prompt building.
- Updated the architecture reference and AI context files so later sessions can treat the Prompt Assembly Pipeline as the dedicated deterministic component responsible for ordered section construction before rendering.

## Prior Work

- Status: completed
- Task: implement Phase 5.6 internal system instruction builder
- Completed on: 2026-07-04

## Outcome

- Added an internal deterministic System Instruction Builder beneath the inactive backend Prompt Builder so application rules and caller-supplied instructions are normalized into the canonical `PromptContextSystemInstructions` section before validation and rendering.
- The builder preserves deterministic instruction order, removes duplicates while keeping the first occurrence, trims empty instruction values, and keeps the resulting system-instruction section provider-agnostic without mutating caller input.
- Refactored `PromptBuilderService` to delegate system-instruction construction to the builder while preserving the existing external request and result contract plus the previously rendered prompt behavior when no application rules are configured.
- Expanded focused backend tests to cover empty instruction sets, application defaults, caller-only instructions, merged instructions, deterministic duplicate elimination, read-only behavior, and backward-compatible prompt building.
- Updated the architecture reference and AI context files so later sessions can treat the System Instruction Builder as the dedicated read-only Prompt Builder component responsible for deterministic system-instruction construction before validation and rendering.

## Prior Work

- Status: completed
- Task: implement Phase 5.5 internal knowledge context collector
- Completed on: 2026-07-04

## Outcome

- Added an internal deterministic Knowledge Context Collector beneath the inactive backend Prompt Builder so caller-supplied `KnowledgeDocument` objects are normalized before `PromptContext` validation and rendering.
- The canonical `PromptContext` knowledge section now preserves deterministic document order, included and excluded document tracking, prompt-hint include and exclude metadata, safe-to-quote flags, domain-validation flags, context limits, and per-document metadata without mutating caller input or changing runtime chat behavior.
- Refactored `PromptBuilderService` to delegate knowledge normalization to the collector while preserving the existing external request and result contract plus the previously rendered prompt output behavior.
- Expanded focused backend tests to cover empty knowledge sets, single and multiple document normalization, deterministic ordering, include and exclude behavior, prompt-hint preservation, read-only handling, and backward-compatible prompt building.
- Updated the architecture reference and AI context files so later sessions can treat the Knowledge Context Collector as the dedicated read-only Prompt Builder component responsible for deterministic knowledge normalization before validation and rendering.

## Prior Work

- Status: completed
- Task: implement Phase 5.4 internal workflow context collector
- Completed on: 2026-07-04

## Outcome

- Added an internal deterministic Workflow Context Collector beneath the inactive backend Prompt Builder so caller-supplied workflow state is normalized before PromptContext validation and rendering.
- The canonical `PromptContext` workflow section now preserves active workflow identity, workflow status, collected fields, missing fields, workflow metadata, and the original workflow state without mutating caller input or changing runtime chat behavior.
- Refactored `PromptBuilderService` to delegate workflow normalization to the collector while preserving the existing external request/result contract and backward-compatible prompt output behavior.
- Expanded focused backend tests to cover no-workflow, booking, cancellation, partial, and completed workflow normalization plus deterministic collector behavior, metadata preservation, read-only handling, and backward compatibility.
- Updated the architecture reference and AI context files so later sessions can treat the Workflow Context Collector as an internal read-only Prompt Builder component that runs before validation and rendering.

## Prior Work

- Status: completed
- Task: implement Phase 5.3 internal conversation context collector
- Completed on: 2026-07-04

## Outcome

- Added an internal deterministic Conversation Context Collector beneath the inactive backend Prompt Builder so caller-supplied conversation state is normalized before PromptContext validation and rendering.
- The canonical `PromptContext` conversation section now preserves the current user message, chronological previous turns, assistant-only turns, preserved conversation metadata, and the original caller state without mutating input data or changing runtime chat behavior.
- Refactored `PromptBuilderService` to delegate conversation normalization to the collector while preserving the existing external request/result contract and existing prompt output for legacy conversation-state inputs.
- Expanded focused backend tests to cover empty, single-turn, and multi-turn conversation normalization, deterministic collector behavior, metadata preservation, and backward-compatible prompt building.
- Updated the architecture reference and AI context files so later sessions can treat the collector as an internal read-only Prompt Builder component that runs before validation and rendering.

## Prior Work

- Status: completed
- Task: implement Phase 5.2.5 PromptContext validation
- Completed on: 2026-07-04

## Outcome

- Added a dedicated deterministic validation layer to the inactive backend Prompt Builder so assembled `PromptContext` instances are checked before block generation and prompt rendering.
- Validation now verifies section structure, non-empty user messages, supported constraint values, rendering-option consistency, duplicate knowledge-document IDs, included/excluded document metadata consistency, and workflow metadata consistency.
- Validation failures return deterministic debug-friendly error payloads through the existing service path without changing any production chat, API, frontend, workflow, retrieval, or database behavior.
- Expanded focused backend tests to cover valid contexts, validation failures, duplicate documents, invalid constraints, invalid rendering options, workflow metadata mismatches, and backward-compatible prompt rendering for valid requests.
- Updated the architecture reference and AI context files so later sessions can treat validation as the final deterministic gate before prompt rendering.

## Prior Work

- Status: completed
- Task: implement Phase 5.2 deterministic Prompt Context model
- Completed on: 2026-07-04

## Outcome

- Added a canonical internal `PromptContext` model beneath the inactive backend Prompt Builder, with structured sections for metadata, user context, conversation context, workflow context, knowledge context, system instructions, constraints, and rendering options.
- Refactored `PromptBuilderService` to build and validate `PromptContext` first, then deterministically render the same external `PromptBuildResult` contract and prompt text behavior as Phase 5.1.
- Kept the new model provider-agnostic and fully outside live `ConversationManager`, retrieval, workflow, API, frontend, and database paths.
- Expanded focused backend tests to cover `PromptContext` creation, optional section omission, deterministic defaults, and backward compatibility of the existing prompt builder output.
- Updated the architecture reference and AI context files so future sessions can continue Prompt Builder work without re-deriving the internal contract.

## Prior Work

- Status: completed
- Task: implement Phase 5.1 standalone prompt builder module
- Completed on: 2026-07-04

## Outcome

- Added an inactive backend `PromptBuilderService` with a deterministic internal contract for composing prompt text from caller-supplied user message, conversation state, and preselected knowledge documents.
- Kept the new module fully outside the live `ConversationManager`, `WorkflowEngine`, Vector-less RAG retrieval, business-service, API, and frontend widget request paths.
- Applied prompt-hint constraints only as bounded formatting rules during prompt construction, including intent-based document inclusion, safe-to-quote handling, and optional per-document context clipping.
- Added focused backend tests covering deterministic prompt assembly, prompt-hint constraint handling, and character-budget truncation behavior.
- Updated the compact AI context and architecture reference so future sessions can find the new prompt-builder seam without re-scanning the repository.

## Prior Work

- Status: completed
- Task: refresh test data health without causing data loss
- Completed on: 2026-07-03

## Outcome

- Inspected the live `backend/app.db` schema and data against the current models and booking/search services with an explicit no-data-loss policy.
- Verified the current doctor, patient, and appointment rows remain valid for implemented workflows; no orphaned relationships, duplicate appointment-slot conflicts, or broken demo appointments were found.
- Confirmed the three future `@example.com` demo bookings still behave correctly under generated availability for July 7, July 8, and July 9, 2026.
- Detected one retained legacy inconsistency in `doctor_availability` where Dr. Sarah Jenkins has a historical `TELEMEDICINE` row despite the live profile supporting only `IN_PERSON`, but intentionally did not mutate it because the table is historical and the current flow no longer depends on it.
- Generated `docs/reports/test-data-health-report.md` documenting schema checks, skipped legacy repair candidates, and the fact that zero rows were inserted, updated, or deleted.

## Prior Work

- Status: completed
- Task: fix Phase 4 booking workflow business-validation failures returning HTTP 500/503
- Completed on: 2026-07-03

## Prior Outcome

- Booking workflow execution now converts expected booking validation failures into structured chat workflow responses instead of surfacing them as transport errors from `/api/chat`.
- Covered business validation scenarios include past appointment date, invalid or unavailable appointment time, already-booked slot / duplicate booking, invalid doctor context, and invalid patient email data.
- Validation responses keep the booking workflow active by preserving valid draft fields, clearing only the invalid field when possible, and returning `INPUT_REQUIRED` workflow state with deterministic next-step guidance.
- Chat API error handling now re-raises expected `HTTPException` values and reserves HTTP 500 for unexpected system failures instead of wrapping everything as HTTP 503.
- Added chat endpoint regression coverage for all validation scenarios plus an explicit unexpected-error test, and revalidated the focused Phase 4 backend suite (`65 passed`).

## Prior Work

- Status: completed
- Task: fix Phase 4 booking-workflow entity extraction and continuation regressions
- Completed on: 2026-07-02

## Outcome

- Deterministic booking extraction now recognizes explicit absolute dates in both textual (`2nd July 2026`) and numeric day-month-year (`02/07/2026`) formats, restoring single-message booking prompts that include doctor, date, and time.
- Booking workflow entry now accepts direct doctor-reference prompts such as `Book appointment with Dr. Sarah Jenkins`, so one-field-per-turn booking conversations can start without a prior doctor-search turn.
- Labeled patient-name lines such as `Patient name: John Doe` and `Full name: John Doe` now parse correctly without swallowing the following email label from multi-line structured booking messages.
- Multi-turn booking continuation now progresses deterministically as newly supplied date, time, patient name, and email values are merged into the active workflow draft before missing-field validation.
- Added focused regression coverage for explicit-date extraction plus three booking workflow scenarios: complete single-message structured booking, one-field-per-turn continuation, and partial structured booking followed by incremental replies.
- Revalidated Phase 4 chat coverage with `backend/.venv/bin/python -m pytest backend/tests/test_chat_entity_extractor.py backend/tests/test_knowledge_repository.py backend/tests/test_conversation_manager.py backend/tests/test_chat_api.py -q` (`58 passed`).

## Prior Work

- Status: completed
- Task: improve Phase 4 Vector-less RAG retrieval quality and informational routing
- Completed on: 2026-07-02

## Outcome

- Knowledge documents now support additive retrieval metadata fields: `category`, `keywords`, `synonyms`, and `aliases`, while remaining backward compatible with existing Markdown and JSON sources.
- Deterministic retrieval scoring now weights title, alias, keyword, synonym, category, and body-text matches separately, and exact phrase matches now outrank weak incidental token overlap so targeted FAQ metadata beats unrelated partial matches.
- Added bundled FAQ knowledge for payment methods, insurance, and parking, and enriched the existing telemedicine, booking, cancellation, consultation-hours, and appointment-preparation documents with retrieval metadata.
- Fixed a narrow entity-extraction bug where substring matching inside words such as `methods` incorrectly produced `gender=Male`, which previously diverted payment-method questions into doctor search.
- Verified informational prompts now return knowledge-backed responses for online consultation, payment methods, appointment preparation, and consultation hours while booking workflows still route through the workflow engine unchanged.
- A focused manual API pass also confirmed casing, punctuation, pluralization, and multi-sentence online-consultation prompts resolve correctly, while unrelated `prescription refill online` prompts now fall back cleanly instead of misrouting to telemedicine.

## Prior Work

- Status: completed
- Task: fix Phase 4 Vector-less RAG routing so knowledge answers win before deterministic fallback
- Completed on: 2026-07-02

## Outcome

- `ConversationManager` now keeps workflow responses first, but returns a knowledge-backed response before the legacy deterministic chatbot for FAQ-style non-workflow turns.
- Knowledge-backed replies now route consistently with populated `knowledge_source` metadata instead of depending on the generic unknown fallback text.
- Retrieval token filtering was tightened so broad words such as `appointment`, `consultation`, `available`, and `support` do not hijack doctor search, availability, fee, or unrelated fallback flows.
- Added bundled FAQ knowledge documents for consultation hours, telemedicine, and appointment preparation so the documented manual-test examples resolve to real repository content.
- Added focused regression coverage for conversation-manager ordering plus repository and API verification of knowledge-hit, no-match fallback, and workflow-first behavior.

## Prior Work

- Status: completed
- Task: implement Phase 4.7 Manual Test Support for Vector-less RAG prototype
- Completed on: 2026-07-01

## Outcome

- A dedicated manual QA checklist now covers positive, negative, edge, regression, workflow, and existing chatbot scenarios for the Vector-less RAG prototype.
- The checklist is stored in `docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-04-manual-test-checklist.md`.
- The phase-4 context files now point to the new manual test artifact for future validation work.

## Prior Work

- Status: completed
- Task: implement Phase 4.6 Frontend Mapping for Vector-less RAG chat metadata
- Completed on: 2026-07-01

## Prior Outcome

- The global AI widget now renders optional `knowledge_source` metadata on assistant text replies when the backend returns a knowledge-backed response.
- The existing workflow cards, appointment booking redirect, and structured response rendering remain unchanged.
- The chat response contract now stays backward compatible while exposing knowledge source identity, path, and matched-term context to the UI.

## Earlier Work

- Status: completed
- Task: implement Phase 4.5 Chat API Enhancement for Vector-less RAG
- Completed on: 2026-07-01

## Earlier Outcome

- Added optional `knowledge_source` metadata to `ChatResponse` so knowledge-backed replies can expose their source without breaking existing fields.
- Wired the deterministic knowledge retrieval service into `ConversationManager` as a read-only fallback when no workflow is active.
- Existing workflow-first routing still wins whenever a workflow is active or the workflow engine returns a response.
- The deterministic fallback remains intact and still handles queries that do not produce a knowledge match.
- Extended focused backend tests to cover knowledge-backed fallback routing, workflow exclusion, title ranking, content keyword matching, response metadata serialization, and default exclusion of deprecated documents.

## Required Files for This Task

- `backend/app/services/prompt_builder.py`
- `backend/tests/test_prompt_builder_service.py`
- `backend/app/services/__init__.py`
- `docs/analysis/hybrid-ai-assistant-architecture/vectorless-rag-architecture.md`
- `docs/ai-content/feature-map.md`

## Notes

- The prompt builder, its canonical `PromptContext` model, and the new validation gate are intentionally inactive in production and currently have no callers in the request path.
- No API, UI, workflow, retrieval, or database behavior changed in this phase.
