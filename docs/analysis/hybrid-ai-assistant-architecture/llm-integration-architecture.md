# LLM Integration Architecture

## Purpose

This document defines the Phase 6 provider-neutral LLM Integration layer for the Doctor Appointment AI Assistant.

The goal of this phase is architectural only:

- define a clean backend boundary for future LLM providers
- keep the current deterministic assistant as the live production path
- avoid any provider SDK, model selection logic, or runtime wiring
- preserve zero API, database, workflow, retrieval, and frontend behavior changes

## Current Status

Phase 6.1 introduced an inactive package at `backend/app/llm/`.

Phase 6.2 refines that seam with:

- canonical request and response translator contracts
- a shared base adapter pipeline for future provider adapters
- an explicit in-memory registry implementation for inactive provider resolution

Phase 6.3 refines the canonical internal contract with:

- explicit model-selection fields on canonical requests
- provider-neutral structured-output, tool, reasoning, and streaming request metadata
- provider-neutral structured-output, tool-call, reasoning, citation, and model/provider result metadata
- capability flags for future reasoning, citation, and audio support

Phase 6.4 adds an inactive orchestration layer with:

- a thin coordinator between `PromptBuilderService` and `LLMIntegrationService`
- a provider-neutral orchestration request contract for already-collected generation input
- deterministic transformation from `PromptBuildResult` into `LLMGenerationRequest`
- deterministic normalization from `LLMGenerationResponse` into a simple orchestration result

Phase 6.5 adds an inactive configuration layer with:

- canonical provider-neutral configuration models for OpenAI, Claude, Gemini, OpenRouter, Ollama, and future providers
- deterministic nested environment mapping into canonical configuration
- explicit validation for provider selection, provider enablement, model requirements, and API-key requirements
- `.env.example` documentation without any runtime instantiation or SDK wiring

Phase 6.5.5 adds an inactive generation budget layer with:

- canonical provider-neutral generation-budget profiles for reasoning effort, output budget, context budget, latency preference, quality preference, and cost preference
- deterministic reusable default profiles plus override support through configuration
- adapter-facing translation contracts that keep provider-native budget parameters private to future adapters
- optional canonical request-level budget metadata without changing orchestration or runtime wiring

Phase 6.6 adds explicit inactive concrete provider adapters with:

- config-backed adapter classes for OpenAI, Claude, Gemini, OpenRouter, and Ollama
- provider-private request and response translation inside each adapter
- explicit transport injection so adapters remain testable without any SDK or live API
- an inactive adapter factory that builds concrete adapters and optional registries from canonical configuration

It is intentionally disconnected from:

- `ConversationManager`
- `WorkflowEngine`
- Vector-less RAG retrieval
- `PromptBuilderService`
- FastAPI routes
- frontend chat contracts

No production request path imports or invokes this package.

## Package Structure

```txt
backend/app/llm/
├── __init__.py
├── adapters.py
├── budget.py
├── config.py
├── interfaces.py
├── models.py
├── orchestrator.py
├── providers.py
├── registry.py
└── service.py
```

## Responsibilities

### `models.py`

Provider-neutral data contracts for future LLM calls:

- `LLMMessage`
- `LLMGenerationRequest`
- `LLMGenerationResponse`
- `LLMGenerationConstraints`
- `LLMProviderDescriptor`
- `LLMProviderCapabilities`
- token-usage and finish-reason models

These models define an internal integration contract only. They are not API schemas and are not tied to any provider payload format.

Phase 6.3 keeps the contract provider-neutral while making room for future:

- structured JSON output requests and results
- tool definitions, tool choice, and tool-call results
- reasoning controls and reasoning metadata
- streaming request intent and streaming result metadata
- multimodal intent metadata
- citations plus separated provider/model metadata

Phase 6.5.5 adds an optional canonical `generation_budget` field on `LLMGenerationRequest` so future callers can pass reusable provider-neutral budget intent into adapters without exposing provider-native token or reasoning parameters upstream.

### `providers.py`

Inactive concrete provider adapters:

- `OpenAIProviderAdapter`
- `ClaudeProviderAdapter`
- `GeminiProviderAdapter`
- `OpenRouterProviderAdapter`
- `OllamaProviderAdapter`
- `LLMProviderAdapterFactory`

These adapters stay inside the inactive boundary. They accept canonical requests, translate them into provider-private payload dictionaries, require an explicit injected transport for invocation, and map provider-private responses back into canonical response models.

### `budget.py`

Inactive provider-neutral generation-budget seam:

- `LLMGenerationBudget`
- `LLMGenerationBudgetOverrides`
- `LLMGenerationBudgetProfile`
- `LLMGenerationBudgetProfileCatalog`
- `LLMGenerationBudgetTranslator`

This module defines reusable canonical profiles such as `FAST`, `BALANCED`, `WORKFLOW`, `QUALITY`, and `MAXIMUM`, along with deterministic validation for token budgets and adapter-facing translation contracts that keep provider-private generation knobs out of upstream code.

### `interfaces.py`

Protocol boundaries for future adapter implementations:

- `LLMRequestTranslator`
- `LLMResponseTranslator`
- `LLMProvider`
- `LLMProviderRegistry`

These contracts keep the upstream integration contract canonical while allowing each future adapter to translate to and from provider-native payloads internally.

### `adapters.py`

Shared translation pipeline:

- `BaseLLMProviderAdapter`

Future provider adapters can subclass this base to:

- translate canonical requests into provider-native payloads
- invoke the provider privately
- translate provider-native responses back into canonical models

This keeps provider-specific payload handling inside the adapter boundary instead of exposing it to callers.

### `config.py`

Inactive provider-neutral configuration layer:

- `LLMProviderName`
- `LLMProviderFeatureFlags`
- `LLMProviderEnvironmentSettings`
- `LLMProviderConfiguration`
- `LLMConfiguration`
- `LLMConfigurationSettings`
- `LLMConfigurationLoader`

This module keeps future provider selection, default-model selection, API keys, base URLs, timeout settings, retry settings, and descriptive feature flags inside a declarative configuration seam that remains disconnected from runtime execution in this phase.

Phase 6.5.5 extends this module with canonical generation-budget settings so global and per-provider profile defaults and profile overrides can be declared declaratively, resolved deterministically, and remain inactive until a later runtime phase.

Phase 6.6 keeps configuration ownership here and lets the adapter factory consume canonical provider configuration without teaching `LLMIntegrationService` how to self-configure.

### `registry.py`

Inactive explicit registry implementation:

- `InMemoryLLMProviderRegistry`

The registry provides deterministic provider listing, lookup, duplicate-name protection, and optional default-provider resolution without auto-wiring anything into production runtime.

### `service.py`

Inactive integration facade:

- `LLMIntegrationService`
- `LLMIntegrationStatus`

The facade exposes three narrow responsibilities:

- report whether the layer is connected
- list registered provider descriptors
- resolve the explicit or registry-default provider name
- delegate generation only when an explicit provider registry is supplied

The service does not self-configure, auto-discover providers, or attach itself to runtime execution.

### `orchestrator.py`

Inactive coordination layer:

- `LLMGenerationOrchestrationRequest`
- `LLMGenerationOrchestrationResult`
- `LLMGenerationOrchestrator`

The orchestrator accepts already-collected generation input, invokes the existing `PromptBuilderService`, converts `PromptBuildResult` into the canonical `LLMGenerationRequest`, delegates generation through `LLMIntegrationService`, and normalizes the canonical response into a simpler provider-neutral result.

It does not:

- construct prompts directly
- know provider-native payloads
- retrieve knowledge
- route workflows
- validate domain business rules
- mutate conversation state

## Boundary Rules

This layer must not:

- import or initialize any external LLM SDK
- instantiate provider clients from configuration in this phase
- expose provider-native payload shapes to upstream callers
- expose provider-native reasoning, latency, token, or quality parameter names outside adapters
- encode OpenAI, Claude, Gemini, Bedrock, Vertex, Ollama, or other provider request/response schemas into canonical models
- load prompt context directly from files or repositories
- perform retrieval, ranking, workflow execution, booking, or domain validation
- mutate conversation state
- change chat API contracts
- bypass deterministic backend services for domain truth

## Relationship To Existing AI Layers

### Deterministic assistant

The current deterministic chat stack remains the primary execution engine.

### Vector-less RAG

Knowledge retrieval continues to select repository documents deterministically and independently. It does not call the LLM layer.

### Prompt Builder

The Prompt Builder remains an inactive formatting seam that produces provider-neutral prompt context and rendered prompt text. In Phase 6.4 it is still independent; the new inactive orchestrator may call it explicitly, but the Prompt Builder itself still does not invoke the LLM layer.

### LLM Generation Orchestrator

The new orchestrator remains inactive and is not imported by `ConversationManager`, `WorkflowEngine`, Vector-less RAG retrieval, FastAPI routes, or frontend chat code.

Its only role is to demonstrate the intended future composition order:

1. already-collected generation input
2. `PromptBuilderService`
3. canonical `LLMGenerationRequest`
4. `LLMIntegrationService`
5. canonical `LLMGenerationResponse`
6. normalized provider-neutral generation result

## Future Integration Path

Later phases may connect this layer in a guarded way:

1. Add one or more provider adapters that subclass `BaseLLMProviderAdapter` and satisfy `LLMProvider`.
2. Keep provider-native request and response payloads private to those adapters.
3. Register them behind an explicit `LLMProviderRegistry`.
4. Optionally declare a default provider through configuration-owned registry setup.
5. Use explicit adapter-factory setup and explicit transport injection instead of hidden runtime auto-discovery.
6. Keep generation-budget translation inside adapters by mapping canonical profile and budget intent into provider-private request parameters.
7. Keep `LLMGenerationOrchestrator` as the narrow caller that passes already-collected generation input through `PromptBuilderService` and then into `LLMIntegrationService`.
8. Keep deterministic post-processing and business validation outside the LLM layer.
9. Preserve existing chat response contracts unless a later migration explicitly changes them.

## Provider Abstraction Rules

Future adapter implementations should:

- accept only canonical `LLMGenerationRequest` input from upstream
- emit only canonical `LLMGenerationResponse` output upstream
- translate provider-native payloads entirely inside the adapter
- map future provider-native structured output, tool-calling, reasoning, streaming, citation, and multimodal fields back into canonical metadata models
- keep SDK clients, auth, retry policy, and transport details inside the adapter
- translate canonical generation budgets into provider-native reasoning, token, latency, or quality controls privately
- avoid leaking provider-specific enums, IDs, tool-call payloads, or message formats outside `backend/app/llm/`
- rely on deterministic domain validation outside the adapter after model output returns
- require explicit transport injection or future provider clients rather than silently performing network setup

## Focused Validation

Focused tests now validate:

- disconnected status remains the default
- explicit provider listing and default-provider resolution remain inactive-only
- the shared adapter pipeline translates canonical requests and responses without exposing provider-native payloads upstream
- duplicate provider registration is rejected deterministically
- canonical request and response validation remains backward compatible
- deterministic serialization of equivalent canonical model instances
- optional structured-output, tool, reasoning, streaming, citation, and modality fields remain provider-neutral and optional
- orchestration order stays deterministic across Prompt Builder, canonical request mapping, LLM service delegation, and normalized result shaping
- the default orchestrator remains inactive without explicit registry-backed LLM service setup
- deterministic configuration loading, nested environment mapping, default propagation, provider validation, and backward-compatible inactive defaults
- deterministic generation-budget profile validation, reusable default-profile resolution, configuration-driven overrides, serialization, and provider-neutral request compatibility
- concrete provider-adapter request translation, response normalization, config-backed registry construction, and inactive transport enforcement

## Compatibility Guarantees

Phase 6.6 preserves:

- zero production behavior changes
- zero API changes
- zero database changes
- zero frontend changes
- zero changes to chat orchestration order
- zero changes to workflow ownership
- zero changes to prompt-builder behavior
- zero runtime wiring of the new orchestrator
- zero runtime wiring of the new configuration layer

## Reference Files

- `backend/app/llm/__init__.py`
- `backend/app/llm/adapters.py`
- `backend/app/llm/config.py`
- `backend/app/llm/models.py`
- `backend/app/llm/interfaces.py`
- `backend/app/llm/orchestrator.py`
- `backend/app/llm/providers.py`
- `backend/app/llm/registry.py`
- `backend/app/llm/service.py`
- `.env.example`
- `backend/tests/test_llm_config.py`
- `backend/tests/test_llm_integration.py`
- `backend/tests/test_llm_orchestrator.py`
- `backend/tests/test_llm_provider_adapters.py`
