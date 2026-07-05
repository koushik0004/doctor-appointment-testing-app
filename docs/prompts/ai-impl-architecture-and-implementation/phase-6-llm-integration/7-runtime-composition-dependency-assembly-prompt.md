# Doctor Appointment AI Assistant

Phase 6.7 — Runtime Composition & Dependency Assembly

Assume all previous phases are complete and verified.

Completed Phases

✓ Phase 1 — Hybrid AI Assistant Architecture

✓ Phase 2 — Conversation Manager

✓ Phase 3 — Workflow Engine

✓ Phase 4 — Vector-less RAG

✓ Phase 5 — Prompt Builder

✓ Phase 6.1 — LLM Integration Architecture

✓ Phase 6.2 — Provider Abstraction

✓ Phase 6.3 — Canonical Request & Response Contract

✓ Phase 6.4 — LLM Generation Orchestrator

✓ Phase 6.5 — Provider Configuration

✓ Phase 6.5.5 — Generation Budget

✓ Phase 6.6 — Concrete Provider Adapters

The project already contains:

✓ Provider-neutral architecture

✓ Canonical Request / Response models

✓ Provider Registry

✓ Adapter Factory

✓ Provider Adapters

✓ Configuration Loader

✓ Generation Budget

✓ Prompt Builder

✓ LLM Generation Orchestrator

✓ LLM Integration Service

All of the above remain inactive.

Do NOT redesign any previous phase.

--------------------------------------------------

Objective

Design the Runtime Composition layer that assembles all LLM components into a single dependency graph while keeping the entire LLM subsystem inactive.

This phase is architecture only.

No runtime activation.

No chatbot integration.

No provider SDK changes.

No API changes.

No production behavior changes.

--------------------------------------------------

The Runtime Composition layer must answer the following questions.

1.

How is the LLM configuration loaded exactly once during application startup?

2.

How is the provider configuration validated?

3.

How is the Generation Budget configuration initialized?

4.

How is the Provider Adapter Factory created?

5.

How are provider transports created?

6.

How are provider adapters instantiated?

7.

How is the Provider Registry constructed?

8.

How is the default provider selected?

9.

How is the LLM Integration Service created?

10.

How is the LLM Generation Orchestrator composed?

11.

How are all dependencies passed explicitly?

12.

How can the whole subsystem remain inactive until a later runtime activation phase?

--------------------------------------------------

Requirements

Design a Composition Root responsible for assembling the entire LLM subsystem.

The composition layer should own:

- configuration loading
- provider configuration validation
- provider transport creation
- provider adapter creation
- registry construction
- default provider resolution
- LLMIntegrationService creation
- LLMGenerationOrchestrator creation

The composition layer must NOT own:

- business logic
- prompt building
- workflow execution
- retrieval
- appointment validation
- routing
- provider payload translation

--------------------------------------------------

Dependency Rules

All dependencies must be created explicitly.

Avoid:

- global singletons
- hidden initialization
- runtime auto-discovery
- reflection
- dynamic imports
- implicit service locators

Prefer:

explicit construction

↓

constructor injection

↓

immutable configuration

↓

clear ownership

--------------------------------------------------

Configuration Rules

Configuration should be loaded exactly once.

Configuration objects should be immutable after creation.

No component should read environment variables directly except the configuration loader.

Adapters should receive already-resolved configuration.

--------------------------------------------------

Transport Rules

Transport creation must remain separate from adapters.

Adapters should receive transports through dependency injection.

Future transports may include:

- HTTP transport
- Mock transport
- Test transport
- Recording transport
- Retry-enabled transport

Adapters must never instantiate transports themselves.

--------------------------------------------------

Registry Rules

The registry should be constructed from the configuration.

Only enabled providers should be registered.

Disabled providers should never be instantiated.

The default provider should come from configuration.

Registry ownership belongs to the composition layer.

--------------------------------------------------

Orchestrator Rules

The orchestrator should receive:

- PromptBuilderService
- LLMIntegrationService

through constructor injection only.

It should not construct dependencies internally.

--------------------------------------------------

Service Rules

LLMIntegrationService should receive:

- Provider Registry

through constructor injection only.

No lazy initialization.

No hidden configuration loading.

--------------------------------------------------

Factory Rules

The Adapter Factory should receive:

- provider configuration
- generation budget defaults
- transport instances

and return fully initialized provider adapters.

The factory should not register adapters.

Registry construction remains the responsibility of the composition layer.

--------------------------------------------------

Testing

Add focused tests validating:

- deterministic composition
- dependency graph correctness
- registry construction
- provider enablement
- disabled-provider exclusion
- configuration loaded once
- transport injection
- adapter creation
- orchestrator composition
- service composition

No provider network calls.

No SDK calls.

No runtime activation.

--------------------------------------------------

Documentation

Update:

- Runtime Composition Architecture
- LLM Integration Architecture
- Phase 6 Report
- AI Context
- Feature Map
- Important Files
- Report Index
- Current Task

--------------------------------------------------

Success Criteria

✓ Single Composition Root

✓ Explicit dependency graph

✓ Configuration loaded once

✓ Immutable configuration

✓ Explicit transport injection

✓ Explicit adapter creation

✓ Explicit registry construction

✓ Explicit service construction

✓ Explicit orchestrator construction

✓ No global state

✓ No hidden initialization

✓ No runtime wiring

✓ No provider SDK changes

✓ No ConversationManager changes

✓ No WorkflowEngine changes

✓ No Prompt Builder changes

✓ No Vector-less RAG changes

✓ No frontend changes

✓ No backend API changes

✓ No database changes

✓ No production behavior changes

✓ Fully backward compatible

✓ Prototype-first

--------------------------------------------------

Architecture Principles

Preserve the layered architecture established in previous phases.

Maintain provider neutrality.

Keep all construction centralized.

Keep runtime activation for a later phase.

Design for future support of:

- OpenAI
- Claude
- Gemini
- OpenRouter
- Ollama
- Azure OpenAI
- AWS Bedrock
- Vertex AI
- future providers

without requiring changes to upstream modules.

The Runtime Composition layer should become the single location responsible for assembling the entire LLM subsystem while keeping it completely disconnected from the production request path.