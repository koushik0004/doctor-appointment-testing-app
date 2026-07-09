# AI Assistant Source Code Architecture

Date: 2026-07-09

## 1. Purpose

This repository implements a doctor appointment platform, but the source-code architecture covered here is limited to the reusable AI Assistant platform and the Chat Widget UI. The documented implementation consists of:

- a FastAPI-backed chat runtime under `backend/app/` that owns chat routing, conversation state shaping, workflow ownership, knowledge retrieval, prompt building, provider-neutral LLM composition, guarded controlled generation, and runtime tracing
- a Next.js Chat Widget under `frontend/lib/ai-widget/` mounted globally by the application shell and connected to the backend through the frontend proxy layer

This document reverse-engineers the repository as implemented. It does not describe appointment-domain modules except where the AI assistant calls them indirectly through its workflow boundary.

## 2. Repository Overview

### Backend

The backend AI surface is concentrated in four layers:

- `backend/app/api/`
  - exposes `/api/chat` and `/api/v1/chat`
- `backend/app/services/`
  - owns deterministic chat behavior, conversation orchestration, intent/entity extraction, workflow execution, and the prompt-builder seam
- `backend/app/knowledge/`
  - owns repository-local knowledge documents, loading, storage, and deterministic retrieval
- `backend/app/llm/`
  - owns the provider-neutral LLM runtime seam: configuration, activation, execution policy, orchestration, provider adapters, transport, validation, eligibility, composition, post-processing, and runtime tracing

### Frontend

The frontend AI surface is concentrated in:

- `frontend/app/layout.tsx`
  - mounts the global widget
- `frontend/app/api/[...path]/route.ts`
  - proxies widget API requests to FastAPI
- `frontend/components/layout/GlobalAiWidget.tsx`
  - binds the generic widget runtime to the live API service and booking-handoff behavior
- `frontend/lib/ai-widget/`
  - reusable widget package containing components, state, context, adapters, service contracts, mappers, styles, and chat-facing types

### Shared Modules

There is no single cross-runtime shared package. Instead, backend and frontend share a mirrored chat contract:

- backend canonical models: `backend/app/schemas/chat.py`
- frontend mirrored DTOs: `frontend/lib/ai-widget/types/chat.ts`

The frontend also depends on root shell infrastructure:

- `frontend/lib/api-client.ts`
- `frontend/stores/booking-store.ts`
- `frontend/lib/utils.ts`
- `frontend/lib/formatters.ts`

### Configuration

- backend runtime bootstrap: `backend/app/core/config.py`
- LLM runtime configuration: `backend/app/llm/config.py`
- environment reference: `.env.example`
- backend dependencies: `backend/requirements.txt`
- frontend build/runtime config: `frontend/package.json`, `frontend/next.config.ts`, `frontend/tailwind.config.ts`, `frontend/tsconfig.json`

### Runtime

The implemented runtime is request-scoped and controller-first:

`Chat API -> ConversationManager -> WorkflowEngine or KnowledgeRetrievalService or deterministic ChatService -> optional LLMRuntimeFacade controlled generation -> validation -> eligibility -> composition -> post-processing -> final ChatResponse -> widget mapper -> rendered message`

## 3. Repository Tree

```text
.
├── AGENTS.md
├── README.md
├── .env.example
├── backend
│   ├── requirements.txt
│   ├── app
│   │   ├── main.py
│   │   ├── api
│   │   │   ├── chat.py
│   │   │   └── router.py
│   │   ├── core
│   │   │   └── config.py
│   │   ├── knowledge
│   │   │   ├── __init__.py
│   │   │   ├── documents.py
│   │   │   ├── loader.py
│   │   │   ├── repository.py
│   │   │   ├── retrieval.py
│   │   │   └── sources
│   │   │       ├── README.md
│   │   │       ├── faq
│   │   │       │   ├── appointment-preparation.md
│   │   │       │   ├── booking.md
│   │   │       │   ├── cancellation.md
│   │   │       │   ├── consultation-hours.md
│   │   │       │   ├── insurance.md
│   │   │       │   ├── parking.md
│   │   │       │   ├── payment-methods.md
│   │   │       │   └── telemedicine.md
│   │   │       └── structured
│   │   │           └── assistant-capabilities.json
│   │   ├── llm
│   │   │   ├── __init__.py
│   │   │   ├── activation.py
│   │   │   ├── adapters.py
│   │   │   ├── budget.py
│   │   │   ├── composer.py
│   │   │   ├── composition.py
│   │   │   ├── config.py
│   │   │   ├── eligibility.py
│   │   │   ├── execution_policy.py
│   │   │   ├── facade.py
│   │   │   ├── interfaces.py
│   │   │   ├── models.py
│   │   │   ├── operations.py
│   │   │   ├── orchestrator.py
│   │   │   ├── post_processor.py
│   │   │   ├── providers.py
│   │   │   ├── registry.py
│   │   │   ├── runtime_trace.py
│   │   │   ├── service.py
│   │   │   ├── transport.py
│   │   │   └── validation.py
│   │   ├── schemas
│   │   │   └── chat.py
│   │   └── services
│   │       ├── chat_entity_extractor.py
│   │       ├── chat_intent_detector.py
│   │       ├── chat_service.py
│   │       ├── conversation_manager.py
│   │       ├── prompt_builder.py
│   │       └── workflow_engine.py
│   └── tests
│       ├── test_chat_api.py
│       ├── test_conversation_manager.py
│       ├── test_knowledge_repository.py
│       ├── test_llm_activation.py
│       ├── test_llm_budget.py
│       ├── test_llm_composer.py
│       ├── test_llm_composition.py
│       ├── test_llm_config.py
│       ├── test_llm_eligibility.py
│       ├── test_llm_execution_policy.py
│       ├── test_llm_facade.py
│       ├── test_llm_integration.py
│       ├── test_llm_models.py
│       ├── test_llm_operations.py
│       ├── test_llm_orchestrator.py
│       ├── test_llm_post_processor.py
│       ├── test_llm_provider_adapters.py
│       ├── test_llm_transport.py
│       ├── test_llm_validation.py
│       └── test_prompt_builder_service.py
├── frontend
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── app
│   │   ├── layout.tsx
│   │   └── api
│   │       └── [...path]
│   │           └── route.ts
│   ├── components
│   │   └── layout
│   │       └── GlobalAiWidget.tsx
│   └── lib
│       └── ai-widget
│           ├── adapters
│           │   ├── index.ts
│           │   └── noop-adapter.ts
│           ├── components
│           │   ├── AiWidgetRoot.tsx
│           │   ├── AppointmentHelpMessage.tsx
│           │   ├── AvailabilityMessage.tsx
│           │   ├── ChatLauncher.tsx
│           │   ├── ChatWindow.tsx
│           │   ├── DoctorCardMessage.tsx
│           │   ├── MessageComposer.tsx
│           │   ├── MessageContentRenderer.tsx
│           │   ├── MessageList.tsx
│           │   ├── SearchFilterSummary.tsx
│           │   └── index.ts
│           ├── core
│           │   ├── context.tsx
│           │   ├── index.ts
│           │   └── state.ts
│           ├── services
│           │   ├── api-service.ts
│           │   ├── appointment-navigation.ts
│           │   ├── chat-response-mapper.ts
│           │   ├── index.ts
│           │   ├── mock-service.ts
│           │   └── noop-service.ts
│           ├── styles
│           │   ├── index.ts
│           │   └── tokens.ts
│           ├── types
│           │   ├── adapter.ts
│           │   ├── chat.ts
│           │   ├── index.ts
│           │   ├── message.ts
│           │   ├── service.ts
│           │   └── widget.ts
│           └── index.ts
└── docs
    └── reports
        └── architecture
            └── AI-Assistant-Source-Code-Architecture.md
```

## 4. Backend Folder Structure

### `backend/app/api`

Purpose:
- exposes the public HTTP boundary for chat

Responsibilities:
- define chat endpoints
- inject database session dependency
- translate unhandled failures into HTTP 500

Dependencies:
- `app.db.database`
- `app.schemas.chat`
- `app.services.chat_service`

Important files:
- `chat.py`
- `router.py`

Extension points:
- additional API versions
- middleware-facing request instrumentation

### `backend/app/core`

Purpose:
- bootstrap configuration used by the backend runtime

Responsibilities:
- load app-level environment settings
- expose cached settings for startup and routes

Dependencies:
- `pydantic-settings`

Important files:
- `config.py`

Extension points:
- additional backend-wide flags such as tracing toggles or app metadata

### `backend/app/services`

Purpose:
- host the chat runtime control plane

Responsibilities:
- intent detection
- entity extraction
- deterministic fallback response generation
- conversation context reconstruction
- workflow ownership and execution
- prompt-builder normalization and rendering

Dependencies:
- `app.schemas.chat`
- `app.services` appointment and doctor modules
- `app.knowledge`
- `app.llm`

Important files:
- `chat_service.py`
- `conversation_manager.py`
- `workflow_engine.py`
- `prompt_builder.py`
- `chat_intent_detector.py`
- `chat_entity_extractor.py`

Extension points:
- new deterministic intents
- richer workflow types
- alternate conversation persistence
- prompt-shaping inputs for LLM execution

### `backend/app/knowledge`

Purpose:
- provide deterministic repository-local knowledge support for FAQ-style chat

Responsibilities:
- define knowledge document schema
- load Markdown and JSON knowledge assets from disk
- keep them in an in-memory repository
- rank and return the best matching knowledge document for a query

Dependencies:
- `pydantic`
- `pathlib`
- optional runtime-trace integration

Important files:
- `documents.py`
- `loader.py`
- `repository.py`
- `retrieval.py`
- `sources/`

Extension points:
- additional knowledge domains
- richer ranking rules
- alternate repository implementations
- future prompt-context integration

### `backend/app/llm`

Purpose:
- implement the reusable provider-neutral LLM subsystem behind the assistant

Responsibilities:
- canonical request/response modeling
- provider configuration loading
- provider registry and adapters
- transport creation and provider invocation
- runtime activation checks
- execution-policy decisions
- orchestration through prompt builder and provider service
- visible-response validation, eligibility, composition, and post-processing
- backend-only runtime tracing

Dependencies:
- `app.services.prompt_builder`
- provider SDK layer through `anthropic`
- `app.core.config` for trace flag interoperability

Important files:
- `models.py`
- `config.py`
- `service.py`
- `orchestrator.py`
- `providers.py`
- `transport.py`
- `composition.py`
- `facade.py`
- `validation.py`
- `eligibility.py`
- `composer.py`
- `post_processor.py`
- `runtime_trace.py`
- `execution_policy.py`
- `activation.py`

Extension points:
- new providers
- new transport implementations
- different rollout policies
- new response-governance stages

### `backend/tests`

Purpose:
- pin AI runtime behavior to the implementation

Responsibilities:
- verify chat API contracts
- verify conversation routing
- verify knowledge retrieval
- verify prompt builder
- verify every LLM seam independently

Dependencies:
- `pytest`
- `fastapi.testclient`
- runtime modules under test

Important files:
- `test_chat_api.py`
- `test_conversation_manager.py`
- `test_knowledge_repository.py`
- `test_prompt_builder_service.py`
- `test_llm_*.py`

Extension points:
- regression coverage for new intents, providers, transports, and widget contracts

## 5. Frontend Folder Structure

### `frontend/app`

Purpose:
- hosts App Router entry points relevant to the widget

Responsibilities:
- mount the widget globally in `layout.tsx`
- proxy browser requests to FastAPI through `api/[...path]/route.ts`

Dependencies:
- `next`
- layout-level shared components
- backend API base URL environment variable

### `frontend/components/layout`

Purpose:
- bind the reusable widget package to the application shell

Responsibilities:
- instantiate the live service implementation
- wire completed booking workflows into the existing booking store and confirmation-page redirect

Important file:
- `GlobalAiWidget.tsx`

### `frontend/lib/ai-widget/adapters`

Purpose:
- abstract presentation-only widget customization

Responsibilities:
- define adapter contract
- provide current noop adapter

Reusability:
- reusable, not business-specific

### `frontend/lib/ai-widget/components`

Purpose:
- render widget chrome and assistant message shapes

Responsibilities:
- launcher, window, message list, composer
- doctor cards, availability cards, appointment-help rendering
- knowledge-source footer rendering on text replies

Reusability:
- reusable widget UI package with app-specific styling assumptions

### `frontend/lib/ai-widget/core`

Purpose:
- own widget-local state and context

Responsibilities:
- reducer-based open/draft/message/error state
- provider/hook exposure for components
- welcome-message bootstrapping

Reusability:
- reusable

### `frontend/lib/ai-widget/services`

Purpose:
- translate between UI state and backend chat contracts

Responsibilities:
- live API submission
- message-to-request conversation serialization
- backend payload-to-widget content mapping
- optional mock and noop service implementations
- appointment booking URL helper

Reusability:
- mostly reusable; the API service assumes the current backend contract

### `frontend/lib/ai-widget/types`

Purpose:
- define the widget’s internal and backend-facing TypeScript contracts

Responsibilities:
- mirrored chat DTOs
- rendered message-content models
- service interfaces
- adapter interfaces
- widget state/config types

Reusability:
- reusable with the current backend schema

### `frontend/lib/ai-widget/styles`

Purpose:
- centralize widget class-name tokens

Responsibilities:
- expose style constants used by widget components

Reusability:
- reusable

### Frontend implementation notes

- Widget:
  - `AiWidgetRoot` provides the package entry point
- Components:
  - all user-visible widget rendering lives under `components/`
- Hooks:
  - there is no large hook catalog; `useAiWidget()` is the main internal hook
- Services:
  - `api-service.ts`, `chat-response-mapper.ts`, `mock-service.ts`, `noop-service.ts`
- API layer:
  - `frontend/app/api/[...path]/route.ts` plus `api-service.ts`
- Models and types:
  - `types/chat.ts`, `types/message.ts`, `types/service.ts`, `types/widget.ts`, `types/adapter.ts`
- Styles:
  - `styles/tokens.ts`
- Configuration:
  - `package.json`, `tsconfig.json`, `tailwind.config.ts`, `next.config.ts`
- Utilities:
  - uses `frontend/lib/api-client.ts`, `frontend/lib/utils.ts`, `frontend/lib/formatters.ts`
- State management:
  - widget-local reducer/context in `core/`
  - cross-feature booking handoff through `frontend/stores/booking-store.ts`

## 6. Entry Points

### Backend startup

- `backend/app/main.py`
  - builds the FastAPI app
  - initializes the database in lifespan startup
  - attaches CORS
  - mounts `api_router` under `settings.api_prefix`

### Frontend startup

- `frontend/app/layout.tsx`
  - root layout for every page
  - imports global styles and mounts `GlobalAiWidget`

### Runtime initialization

- `backend/app/services/chat_service.py`
  - creates cached knowledge and LLM runtime services
- `backend/app/services/conversation_manager.py`
  - constructs `WorkflowEngine`, consumes knowledge retrieval, and calls `LLMRuntimeFacade`
- `backend/app/llm/composition.py`
  - assembles transports, adapters, registry, integration service, orchestrator, activation, policy, and operations services

### Widget initialization

- `frontend/components/layout/GlobalAiWidget.tsx`
  - creates the live API service
  - wraps post-response booking side effects
  - passes a noop presentation adapter into `AiWidgetRoot`
- `frontend/lib/ai-widget/components/AiWidgetRoot.tsx`
  - creates provider state and renders launcher/window

### Application bootstrap

- backend route bootstrap:
  - `backend/app/api/router.py`
- frontend proxy bootstrap:
  - `frontend/app/api/[...path]/route.ts`
- contract bootstrap:
  - `backend/app/schemas/chat.py`
  - `frontend/lib/ai-widget/types/chat.ts`

## 7. Folder Responsibilities

### `backend/app/api`

Why it exists:
- to isolate HTTP concerns from orchestration logic

Who calls it:
- frontend proxy and any direct API client

Who depends on it:
- no backend folder depends inward on route code

Reusable:
- partially; route style is reusable, endpoint semantics are assistant-specific

Domain-specific:
- AI assistant-specific

### `backend/app/services`

Why it exists:
- to keep conversational logic outside routes

Who calls it:
- `api/chat.py`

Who depends on it:
- `api/`, `llm/` prompt integration, tests

Reusable:
- mixed; prompt builder is reusable, workflow behavior is assistant-specific

Domain-specific:
- mostly assistant-specific orchestration

### `backend/app/knowledge`

Why it exists:
- to separate repository-local knowledge from routing and provider logic

Who calls it:
- `chat_service.py`, `conversation_manager.py`, tests

Who depends on it:
- `schemas/chat.py` for `ChatKnowledgeSource`
- `services/`
- `llm/runtime_trace.py` integration points

Reusable:
- yes, as a deterministic local knowledge module

Domain-specific:
- document content is domain-specific; loader/retrieval infrastructure is reusable

### `backend/app/llm`

Why it exists:
- to isolate all provider-neutral and provider-bound AI generation logic from the deterministic assistant runtime

Who calls it:
- `chat_service.py`
- `conversation_manager.py`
- tests

Who depends on it:
- `services/prompt_builder.py`
- any future provider-backed assistant logic

Reusable:
- strongly reusable

Domain-specific:
- infrastructure is reusable; policy inputs and some fallback rules are assistant-shaped

### `backend/tests`

Why it exists:
- to lock runtime behavior and architecture seams against regression

Who calls it:
- developers and CI

Who depends on it:
- architecture confidence, not runtime code

Reusable:
- no

Domain-specific:
- implementation-specific

### `frontend/app`

Why it exists:
- to host global shell and proxy entry points

Who calls it:
- Next.js runtime

Who depends on it:
- the widget package and browser clients

Reusable:
- shell pattern reusable, implementation app-specific

Domain-specific:
- application-specific

### `frontend/components/layout`

Why it exists:
- to bridge the reusable widget package into the current application

Who calls it:
- `frontend/app/layout.tsx`

Who depends on it:
- widget mount lifecycle and booking redirect flow

Reusable:
- low; glue layer is app-specific

Domain-specific:
- application-specific

### `frontend/lib/ai-widget`

Why it exists:
- to keep the chat widget as a coherent reusable UI subsystem

Who calls it:
- `GlobalAiWidget.tsx`

Who depends on it:
- layout mount, service integrations, tests when added

Reusable:
- high

Domain-specific:
- mostly generic, but message shapes mirror the current backend contract

## 8. File Responsibilities

### Backend startup and routing

`backend/app/main.py`
- Purpose: FastAPI application entry point.
- Primary responsibility: build the app, load settings, run startup DB initialization, register CORS and routers.
- Major classes: none.
- Major functions: `create_app`.
- Public interfaces: exported `app`.
- Dependencies: `api_router`, `get_settings`, `init_db`.
- Used by: Uvicorn and tests.
- Calls: settings loader, database init, router include.
- Extension points: middleware, startup hooks, app-level instrumentation.

`backend/app/api/router.py`
- Purpose: central route registration.
- Primary responsibility: aggregate health, chat, and unrelated business routers under one `APIRouter`.
- Major functions: none beyond module wiring.
- Public interfaces: `api_router`.
- Dependencies: route modules.
- Used by: `main.py`.
- Calls: `include_router`.
- Extension points: route versioning and endpoint grouping.

`backend/app/api/chat.py`
- Purpose: public assistant HTTP boundary.
- Primary responsibility: expose `POST /api/chat` and `POST /api/v1/chat` over the shared handler.
- Major functions: `_handle_chat`, `create_chat_reply`, `create_chat_reply_v1`.
- Public interfaces: both routers.
- Dependencies: DB session provider, `ChatRequest`, `ChatResponse`, `create_chat_response`.
- Used by: frontend proxy and direct API callers.
- Calls: service-layer chat creation.
- Extension points: auth, rate limits, additional chat endpoint versions.

`backend/app/core/config.py`
- Purpose: backend app configuration loader.
- Primary responsibility: load app name, API prefix, database URL, CORS origins, and `AI_RUNTIME_TRACE`.
- Major classes: `Settings`.
- Major functions: `get_settings`.
- Public interfaces: settings object and cached loader.
- Dependencies: `pydantic-settings`.
- Used by: `main.py`, chat-service bootstrap, runtime tracing.
- Calls: environment parsing only.
- Extension points: more app-level operational flags.

### Backend chat contract and orchestration

`backend/app/schemas/chat.py`
- Purpose: canonical backend chat DTO set.
- Primary responsibility: define intents, routing targets, workflow state, conversation state, knowledge-source metadata, request payload, and response payload.
- Major classes: `ChatRequest`, `ChatResponse`, `ChatConversationContext`, `ChatWorkflowResult`, `ChatKnowledgeSource`.
- Major functions: response validator `_sync_legacy_response`.
- Public interfaces: all chat-facing models.
- Dependencies: knowledge document enums.
- Used by: routes, services, tests, frontend mirrored types.
- Calls: none beyond Pydantic validation.
- Extension points: new intents, metadata fields, workflow result shapes.

`backend/app/services/chat_intent_detector.py`
- Purpose: coarse intent classification for user prompts.
- Primary responsibility: convert free text into `ChatIntentMatch`.
- Major classes: `ChatIntentMatch`.
- Major functions: `detect_chat_intent`.
- Public interfaces: intent detection function and result model.
- Dependencies: `ChatIntent`, text normalization helpers.
- Used by: deterministic chat and conversation orchestration.
- Calls: keyword and pattern checks.
- Extension points: richer NLP heuristics or intent priorities.

`backend/app/services/chat_entity_extractor.py`
- Purpose: deterministic entity extraction for search and workflow hints.
- Primary responsibility: parse specialization, gender, fee, date, time, and location filters.
- Major functions: `normalize_text`, `extract_chat_search_filters`, `extract_target_date`, `extract_time_preference`.
- Public interfaces: extractor helpers.
- Dependencies: `ChatSearchFilters`.
- Used by: `chat_service.py`, `workflow_engine.py`, `conversation_manager.py`.
- Calls: regex/date parsing logic.
- Extension points: richer temporal parsing, more filter types.

`backend/app/services/chat_service.py`
- Purpose: deterministic assistant engine and service bootstrap.
- Primary responsibility: generate non-workflow chat responses, build doctor/availability cards, bootstrap cached knowledge and LLM facade instances, and expose `create_chat_response`.
- Major classes: `ChatService` is not a class; primary type is `ChatResponder` protocol.
- Major functions: `create_chat_response`, deterministic card/filter helpers, knowledge bootstrap helpers.
- Public interfaces: `create_chat_response`.
- Dependencies: doctor and availability services, knowledge services, prompt builder, LLM composition root, conversation manager.
- Used by: `api/chat.py`.
- Calls: intent detection, entity extraction, data shaping, `ConversationManager`.
- Extension points: deterministic response templates, bootstrap composition overrides.

`backend/app/services/conversation_manager.py`
- Purpose: single request-scoped assistant orchestrator.
- Primary responsibility: rebuild conversation context, preserve workflow ownership, consult knowledge retrieval, invoke deterministic fallback, optionally invoke shadow or controlled generation, enrich final conversation metadata, and emit the final runtime trace exactly once.
- Major classes: `ConversationManager`.
- Major functions: `_build_context_from_request`, `_retrieve_knowledge_match`, `_run_shadow_mode`, `_run_controlled_generation`, `handle`.
- Public interfaces: `ConversationManager.handle`.
- Dependencies: `WorkflowEngine`, knowledge retrieval, `LLMRuntimeFacade`, chat DTOs, runtime trace registry.
- Used by: `chat_service.py`, tests.
- Calls: workflow engine, retrieval, deterministic engine, runtime facade.
- Extension points: persisted conversation storage, alternate routing policy, richer trace payloads.

`backend/app/services/workflow_engine.py`
- Purpose: structured workflow owner for transactional chat turns.
- Primary responsibility: detect workflow ownership, merge incremental draft fields, validate required inputs, execute booking/cancellation/confirmation service calls, and translate workflow outcomes into `ChatResponse`.
- Major classes: `WorkflowEngine`.
- Major functions: `_build_draft`, `_resolve_workflow_type`, `_missing_fields_for_workflow`, `handle`.
- Public interfaces: `WorkflowEngine.handle`.
- Dependencies: appointment services, doctor listing, chat DTOs, trace session.
- Used by: `ConversationManager`.
- Calls: appointment booking and lookup services.
- Extension points: new workflow types, different field prompts, persisted draft state.

### Backend knowledge subsystem

`backend/app/knowledge/documents.py`
- Purpose: typed knowledge document schema.
- Primary responsibility: define source types, domains, audiences, status, prompt hints, and the `KnowledgeDocument` model.
- Public interfaces: all knowledge enums and models.
- Used by: loader, retrieval, chat schema, tests.
- Extension points: new metadata fields and content safety hints.

`backend/app/knowledge/loader.py`
- Purpose: filesystem knowledge ingestion.
- Primary responsibility: read Markdown/JSON assets, parse front matter, validate payloads, and emit `KnowledgeDocument` instances.
- Major classes: `FileSystemKnowledgeLoader`, `KnowledgeValidationError`.
- Used by: service bootstrap and tests.
- Extension points: additional file formats and validation rules.

`backend/app/knowledge/repository.py`
- Purpose: in-memory storage boundary for loaded knowledge.
- Primary responsibility: add, list, and retrieve documents by id.
- Major classes: `InMemoryKnowledgeRepository`.
- Used by: retrieval service, bootstrap, tests.
- Extension points: persistent or remote repositories.

`backend/app/knowledge/retrieval.py`
- Purpose: deterministic top-match retrieval engine.
- Primary responsibility: rank knowledge documents using title, alias, keyword, synonym, category, and body-text matching, then return `KnowledgeRetrievalMatch`.
- Major classes: `KnowledgeRetrievalService`, `KnowledgeRetrievalMatch`.
- Used by: `ConversationManager`, tests.
- Calls: tokenization and scoring helpers.
- Extension points: alternate rankers, multi-document retrieval, embeddings.

### Backend prompt-builder and LLM subsystem

`backend/app/services/prompt_builder.py`
- Purpose: canonical prompt construction seam.
- Primary responsibility: normalize conversation, workflow, and knowledge context into `PromptContext`, validate it, assemble ordered sections, and render a bounded prompt string.
- Major classes: `PromptBuilderService`, `PromptContextConversationCollector`, `PromptContextWorkflowCollector`, `PromptContextKnowledgeCollector`, `PromptContextSystemInstructionBuilder`, `PromptContextAssemblyPipeline`, `PromptRenderer`, `PromptBuildRequest`, `PromptBuildResult`.
- Used by: `LLMGenerationOrchestrator`, tests.
- Calls: internal deterministic collectors and renderer.
- Extension points: new prompt sections, constraints, truncation policies.

`backend/app/llm/models.py`
- Purpose: canonical provider-neutral LLM contract.
- Primary responsibility: define messages, generation requests, responses, citations, tools, reasoning, streaming, provider descriptors, and token usage.
- Used by: nearly every LLM module.
- Extension points: future provider-neutral capabilities.

`backend/app/llm/interfaces.py`
- Purpose: abstract translator and provider protocols.
- Primary responsibility: formalize adapter-facing request/response translator and provider interfaces.
- Used by: adapters, providers, registry, service.
- Extension points: new adapter contracts.

`backend/app/llm/adapters.py`
- Purpose: shared adapter base.
- Primary responsibility: provide reusable adapter scaffolding via `BaseLLMProviderAdapter`.
- Used by: provider adapters.
- Extension points: cross-provider common behavior.

`backend/app/llm/config.py`
- Purpose: LLM runtime configuration system.
- Primary responsibility: load provider choice, runtime feature flags, provider-specific credentials, model defaults, feature declarations, and generation-budget overrides from nested environment variables.
- Major classes: `LLMConfiguration`, `LLMConfigurationLoader`, `LLMConfigurationSettings`.
- Used by: composition root, tests.
- Extension points: new providers and flags.

`backend/app/llm/budget.py`
- Purpose: provider-neutral budget profiles.
- Primary responsibility: define reusable budget catalogs and profile resolution.
- Used by: config, orchestration, providers, tests.
- Extension points: additional performance/cost profiles.

`backend/app/llm/registry.py`
- Purpose: runtime provider registry.
- Primary responsibility: store enabled providers and prevent duplicate registration.
- Major classes: `InMemoryLLMProviderRegistry`.
- Used by: integration service and composition.
- Extension points: dynamic provider discovery.

`backend/app/llm/providers.py`
- Purpose: concrete provider adapters.
- Primary responsibility: translate canonical requests to provider-private payloads and normalize provider responses back to canonical form.
- Major classes: `OpenAIProviderAdapter`, `OpenRouterProviderAdapter`, `ClaudeProviderAdapter`, `GeminiProviderAdapter`, `OllamaProviderAdapter`, `LLMProviderAdapterFactory`.
- Used by: composition root and integration service.
- Calls: injected transports.
- Extension points: new providers or provider-specific request shaping.

`backend/app/llm/transport.py`
- Purpose: live SDK/network execution boundary.
- Primary responsibility: own `ClaudeTransport`, normalize transport errors, serialize Anthropic-compatible requests, and capture transport diagnostics.
- Major classes: `LLMTransportError`, `ClaudeTransport`.
- Used by: provider adapters through the production transport factory.
- Extension points: OpenAI/Gemini/OpenRouter/Ollama production transports.

`backend/app/llm/service.py`
- Purpose: provider-neutral execution service.
- Primary responsibility: dispatch canonical generation requests through the selected provider registry entry and report runtime status.
- Major classes: `LLMIntegrationService`, `LLMIntegrationStatus`.
- Used by: orchestrator and facade.
- Extension points: selection strategy, richer health reporting.

`backend/app/llm/orchestrator.py`
- Purpose: prompt-to-provider orchestration layer.
- Primary responsibility: call `PromptBuilderService`, construct `LLMGenerationRequest`, delegate to `LLMIntegrationService`, and normalize orchestration results.
- Major classes: `LLMGenerationOrchestrator`, `LLMGenerationOrchestrationRequest`, `LLMGenerationOrchestrationResult`.
- Used by: facade.
- Extension points: alternate prompt sources, orchestration policies.

`backend/app/llm/activation.py`
- Purpose: runtime readiness evaluator.
- Primary responsibility: determine whether LLM execution is enabled, healthy, and permitted by configuration.
- Major classes: `LLMRuntimeActivationEvaluator`, `LLMRuntimeActivationService`.
- Used by: composition and execution policy.
- Extension points: richer dependency checks.

`backend/app/llm/execution_policy.py`
- Purpose: routing-policy engine.
- Primary responsibility: turn preferred mode, ownership hints, and activation status into an `AIExecutionDecision`.
- Major classes: `AIExecutionPolicyEvaluator`, `AIExecutionPolicyService`, `AIExecutionDecision`.
- Used by: facade and tests.
- Extension points: additional routing modes and approval rules.

`backend/app/llm/validation.py`
- Purpose: output validation gate.
- Primary responsibility: reject empty or malformed visible runtime responses before user exposure.
- Major classes: `LLMRuntimeResponseValidator`.
- Used by: facade.
- Extension points: stronger schema/content policies.

`backend/app/llm/eligibility.py`
- Purpose: visible-response safety gate.
- Primary responsibility: allow only approved low-risk conversational responses to become user-visible.
- Major classes: `LLMRuntimeResponseEligibilityEvaluator`.
- Used by: facade.
- Extension points: richer risk policy.

`backend/app/llm/composer.py`
- Purpose: final-response assembly layer.
- Primary responsibility: combine deterministic business truth with optional validated and eligible LLM guidance into `LLMRuntimeResponse`.
- Major classes: `LLMRuntimeResponseComposer`.
- Used by: facade.
- Extension points: alternate hybrid composition strategies.

`backend/app/llm/post_processor.py`
- Purpose: presentation-normalization layer.
- Primary responsibility: normalize whitespace, markdown, and visible metadata on final runtime responses.
- Major classes: `LLMRuntimeResponsePostProcessor`.
- Used by: facade.
- Extension points: richer output cleanup.

`backend/app/llm/operations.py`
- Purpose: operational-readiness modeling.
- Primary responsibility: define observability, cost, retry, timeout, audit, rollout, and performance models for the LLM subsystem.
- Major classes: `LLMOperationalReadinessService` and supporting models.
- Used by: composition and tests.
- Extension points: production operations policies.

`backend/app/llm/runtime_trace.py`
- Purpose: backend-only tracing infrastructure.
- Primary responsibility: capture per-request stage data, redact common PII patterns, hold request-scoped trace sessions, and write a final JSON log line.
- Major classes: `AIRuntimeTraceSession`, `AIRuntimeTraceRegistry`.
- Used by: `ConversationManager`, retrieval, facade, service, adapters, transport.
- Extension points: additional stage instrumentation and sinks.

`backend/app/llm/composition.py`
- Purpose: dependency assembly root.
- Primary responsibility: load configuration once, create transports, instantiate enabled adapters, register providers, compose activation/policy/operations services, and expose a cached `LLMRuntimeComposition`.
- Major classes: `LLMRuntimeCompositionRoot`, `ProductionLLMProviderTransportFactory`.
- Used by: `chat_service.py`, `LLMRuntimeFacade`, tests.
- Extension points: alternate transport factories and composition policies.

`backend/app/llm/facade.py`
- Purpose: public runtime boundary for the LLM subsystem.
- Primary responsibility: cache composition, expose snapshot state, run shadow execution, run controlled generation, and apply validation, eligibility, composition, and post-processing before visible output.
- Major classes: `LLMRuntimeFacade`, `LLMControlledGenerationRequest`, `LLMControlledGenerationResult`, `LLMShadowModeRequest`.
- Used by: `ConversationManager`, tests.
- Extension points: async runners, rollout behavior, fallback strategies.

`backend/app/llm/__init__.py`
- Purpose: lazy-export package boundary.
- Primary responsibility: re-export public LLM symbols without eagerly importing the whole prompt-builder/orchestrator chain.
- Used by: application imports and tests.
- Extension points: public API curation.

### Frontend widget and integration files

`frontend/app/layout.tsx`
- Purpose: root Next.js shell.
- Primary responsibility: mount `GlobalAiWidget` once for the entire app.
- Used by: Next.js runtime.
- Calls: layout components plus widget mount.
- Extension points: shell-wide widget placement or gating.

`frontend/app/api/[...path]/route.ts`
- Purpose: frontend-to-backend proxy boundary.
- Primary responsibility: forward widget HTTP requests to the FastAPI backend, preserve method/query/body, and strip hop-by-hop headers.
- Major functions: `buildBackendUrl`, `buildHeaders`, `proxyRequest`, `OPTIONS`.
- Used by: `apiClient` calls from the widget service.
- Extension points: auth propagation, response normalization, retry.

`frontend/components/layout/GlobalAiWidget.tsx`
- Purpose: app-specific widget wiring layer.
- Primary responsibility: create the live API widget service, inspect workflow metadata on replies, sync successful booking data into Zustand, and navigate to the confirmation page.
- Major functions: `getWorkflowMetadata`, `GlobalAiWidget`.
- Used by: `layout.tsx`.
- Calls: widget root, API service, booking-store setters, Next router.
- Extension points: alternate adapters, analytics, workflow-aware side effects.

`frontend/lib/ai-widget/types/chat.ts`
- Purpose: mirrored backend chat DTOs.
- Primary responsibility: preserve exact frontend understanding of intents, workflow state, conversation context, structured cards, and knowledge-source metadata.
- Used by: API service, mappers, message metadata typing.
- Extension points: aligned backend contract changes.

`frontend/lib/ai-widget/types/message.ts`
- Purpose: rendered widget message model.
- Primary responsibility: distinguish text, doctor-list, availability, and appointment-help content while carrying backend metadata.
- Used by: reducer, components, API mapper.
- Extension points: new message renderers.

`frontend/lib/ai-widget/types/service.ts`
- Purpose: service boundary contract.
- Primary responsibility: define `AiWidgetService` request/response interface.
- Used by: `AiWidgetRoot`, API/mock/noop services.
- Extension points: streaming or tool-call-aware services.

`frontend/lib/ai-widget/types/widget.ts`
- Purpose: widget state/config contract.
- Primary responsibility: define `AiWidgetState`, `AiWidgetConfig`, and provider props.
- Used by: reducer and context.
- Extension points: richer widget config.

`frontend/lib/ai-widget/types/adapter.ts`
- Purpose: presentation adapter contract.
- Primary responsibility: define the adapter surface for labels and quick actions.
- Used by: adapter implementations and root component.
- Extension points: richer theming/presentation injection.

`frontend/lib/ai-widget/core/state.ts`
- Purpose: widget reducer.
- Primary responsibility: own open state, send lifecycle, draft text, message list, errors, and welcome-message bootstrapping.
- Major functions: `createInitialAiWidgetState`, `aiWidgetReducer`.
- Used by: context provider.
- Extension points: streaming state, retry state.

`frontend/lib/ai-widget/core/context.tsx`
- Purpose: state container and hook boundary.
- Primary responsibility: expose reducer state through React context and `useAiWidget()`.
- Used by: widget components.
- Extension points: replacing reducer implementation or adding selectors.

`frontend/lib/ai-widget/components/AiWidgetRoot.tsx`
- Purpose: widget package entry component.
- Primary responsibility: create provider scope, select service implementation, submit messages, append replies, and coordinate launcher/window rendering.
- Major functions: `AiWidgetFrame`, `AiWidgetRoot`.
- Used by: `GlobalAiWidget.tsx`.
- Calls: context, service, mapper helper, child components.
- Extension points: different launcher/window composition or alternate send flow.

`frontend/lib/ai-widget/components/ChatWindow.tsx`
- Purpose: main widget surface.
- Primary responsibility: render header, message list, quick actions, composer, and status/error states.
- Used by: `AiWidgetRoot`.
- Extension points: richer window layout or streaming affordances.

`frontend/lib/ai-widget/components/ChatLauncher.tsx`
- Purpose: open/close entry point.
- Primary responsibility: render the floating launcher button.
- Used by: `AiWidgetRoot`.

`frontend/lib/ai-widget/components/MessageList.tsx`
- Purpose: message collection renderer.
- Primary responsibility: iterate through messages and delegate to content renderers.
- Used by: `ChatWindow`.

`frontend/lib/ai-widget/components/MessageComposer.tsx`
- Purpose: user input capture.
- Primary responsibility: control the draft input and submission trigger.
- Used by: `ChatWindow`.

`frontend/lib/ai-widget/components/MessageContentRenderer.tsx`
- Purpose: assistant message renderer.
- Primary responsibility: switch on content type, render doctor/availability/help/text blocks, and show the knowledge-source footer for text replies.
- Used by: `MessageList`.
- Extension points: new content types or richer source citation UI.

`frontend/lib/ai-widget/components/DoctorCardMessage.tsx`
- Purpose: doctor card renderer.
- Primary responsibility: display doctor details for structured doctor-search replies.

`frontend/lib/ai-widget/components/AvailabilityMessage.tsx`
- Purpose: availability renderer.
- Primary responsibility: display slot cards for structured availability replies.

`frontend/lib/ai-widget/components/AppointmentHelpMessage.tsx`
- Purpose: workflow-help renderer.
- Primary responsibility: display step lists for appointment and cancellation help.

`frontend/lib/ai-widget/components/SearchFilterSummary.tsx`
- Purpose: structured search-summary renderer.
- Primary responsibility: show matched filters and result-count context for list responses.

`frontend/lib/ai-widget/services/api-service.ts`
- Purpose: live backend integration layer.
- Primary responsibility: serialize widget conversation history into backend request format, call `/chat` through the shared API client, and map backend payloads into widget messages.
- Major functions: `serializeConversation`, `createApiAiWidgetService`.
- Dependencies: `apiClient`, mirrored chat types, response mapper.
- Used by: `GlobalAiWidget`.
- Extension points: streaming, auth headers, retry policies.

`frontend/lib/ai-widget/services/chat-response-mapper.ts`
- Purpose: backend-to-widget content translation layer.
- Primary responsibility: convert `ChatResponse` payloads into widget message content and metadata, including doctor cards, availability cards, help blocks, search summaries, and knowledge-source carry-through.
- Major functions: `mapChatResponseToContent`, `createAssistantMessageFromChatResponse`, `createTextMessageContent`.
- Used by: API service and reducer welcome-message creation.
- Extension points: new backend intents or presentation shapes.

`frontend/lib/ai-widget/services/appointment-navigation.ts`
- Purpose: booking-navigation helper.
- Primary responsibility: build booking URLs from doctor ids.
- Used by: widget UX integration paths.

`frontend/lib/ai-widget/services/mock-service.ts`
- Purpose: local non-backend demo service.
- Primary responsibility: provide delayed mocked assistant replies for widget development.

`frontend/lib/ai-widget/services/noop-service.ts`
- Purpose: inert service implementation.
- Primary responsibility: provide a do-nothing service when needed by integration code.

`frontend/lib/ai-widget/adapters/noop-adapter.ts`
- Purpose: default presentation adapter.
- Primary responsibility: provide base labels and no-op quick-action customization.

`frontend/lib/ai-widget/styles/tokens.ts`
- Purpose: widget style-token registry.
- Primary responsibility: expose shared class names used across widget components.

`frontend/lib/ai-widget/index.ts`
- Purpose: package barrel export.
- Primary responsibility: re-export adapters, components, core, services, styles, and types for a single import surface.

### Tests as architecture evidence

`backend/tests/test_chat_api.py`
- proves the external chat contract, both chat routes, deterministic routing targets, structured doctor/availability cards, doctor-detail handling, knowledge-source responses, and workflow payload shapes

`backend/tests/test_conversation_manager.py`
- proves workflow-first ownership, knowledge-before-deterministic fallback, and controlled-generation interaction with the runtime facade

`backend/tests/test_prompt_builder_service.py`
- proves prompt-context normalization and rendering behavior

`backend/tests/test_llm_facade.py`
- proves composition caching, shadow execution, controlled generation, validation, eligibility, composition, post-processing, and trace-aware failure behavior

`backend/tests/test_llm_transport.py`
- proves Claude transport request/response normalization and metadata sanitization

`backend/tests/test_runtime_trace.py`
- proves final trace emission behavior

## 9. Runtime Flow Mapping

### Folder-to-runtime mapping

`frontend/app/layout.tsx`
↓ mounts
`frontend/components/layout/GlobalAiWidget.tsx`
↓ initializes
`frontend/lib/ai-widget/components/`
`frontend/lib/ai-widget/core/`
`frontend/lib/ai-widget/services/`
↓ sends HTTP via
`frontend/app/api/[...path]/route.ts`
↓ reaches
`backend/app/api/chat.py`
↓ enters orchestration in
`backend/app/services/conversation_manager.py`
↓ may delegate workflow ownership to
`backend/app/services/workflow_engine.py`
↓ or FAQ retrieval to
`backend/app/knowledge/retrieval.py`
↓ or deterministic reply generation in
`backend/app/services/chat_service.py`
↓ optional prompt construction through
`backend/app/services/prompt_builder.py`
↓ optional provider-neutral generation through
`backend/app/llm/orchestrator.py`
`backend/app/llm/service.py`
`backend/app/llm/providers.py`
`backend/app/llm/transport.py`
↓ response governance through
`backend/app/llm/validation.py`
`backend/app/llm/eligibility.py`
`backend/app/llm/composer.py`
`backend/app/llm/post_processor.py`
↓ observability through
`backend/app/llm/runtime_trace.py`
↓ final chat payload in
`backend/app/schemas/chat.py`
↓ remapped for UI by
`frontend/lib/ai-widget/services/chat-response-mapper.ts`
↓ rendered by
`frontend/lib/ai-widget/components/MessageContentRenderer.tsx`

### Runtime participation by folder

- `backend/app/api`
  - external REST entry
- `backend/app/services`
  - conversation, workflow, deterministic engine, prompt builder
- `backend/app/knowledge`
  - deterministic FAQ retrieval
- `backend/app/llm`
  - optional generated-response path and tracing
- `frontend/app`
  - shell mount and proxy boundary
- `frontend/components/layout`
  - application-specific widget binding
- `frontend/lib/ai-widget/core`
  - client-side widget state lifecycle
- `frontend/lib/ai-widget/services`
  - request/response translation
- `frontend/lib/ai-widget/components`
  - user-visible rendering
- `frontend/lib/ai-widget/types`
  - client contract consistency

### Current architectural characteristics

- The visible assistant remains deterministic-first.
- Workflow ownership prevents generated output from taking over transactional flows.
- Knowledge retrieval is local and deterministic.
- Prompt Builder and LLM runtime are explicit subsystem seams, not implicit logic inside the route or widget.
- Controlled generation is gated behind activation, policy, validation, eligibility, composition, and post-processing.
- The widget carries request-scoped conversation state; there is no persisted conversation store in the current implementation.
