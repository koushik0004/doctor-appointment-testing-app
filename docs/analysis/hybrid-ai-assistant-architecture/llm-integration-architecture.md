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
├── interfaces.py
├── models.py
├── orchestrator.py
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
- expose provider-native payload shapes to upstream callers
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
5. Keep `LLMGenerationOrchestrator` as the narrow caller that passes already-collected generation input through `PromptBuilderService` and then into `LLMIntegrationService`.
6. Keep deterministic post-processing and business validation outside the LLM layer.
7. Preserve existing chat response contracts unless a later migration explicitly changes them.

## Provider Abstraction Rules

Future adapter implementations should:

- accept only canonical `LLMGenerationRequest` input from upstream
- emit only canonical `LLMGenerationResponse` output upstream
- translate provider-native payloads entirely inside the adapter
- map future provider-native structured output, tool-calling, reasoning, streaming, citation, and multimodal fields back into canonical metadata models
- keep SDK clients, auth, retry policy, and transport details inside the adapter
- avoid leaking provider-specific enums, IDs, tool-call payloads, or message formats outside `backend/app/llm/`
- rely on deterministic domain validation outside the adapter after model output returns

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

## Compatibility Guarantees

Phase 6.4 preserves:

- zero production behavior changes
- zero API changes
- zero database changes
- zero frontend changes
- zero changes to chat orchestration order
- zero changes to workflow ownership
- zero changes to prompt-builder behavior
- zero runtime wiring of the new orchestrator

## Reference Files

- `backend/app/llm/__init__.py`
- `backend/app/llm/adapters.py`
- `backend/app/llm/models.py`
- `backend/app/llm/interfaces.py`
- `backend/app/llm/orchestrator.py`
- `backend/app/llm/registry.py`
- `backend/app/llm/service.py`
- `backend/tests/test_llm_integration.py`
- `backend/tests/test_llm_orchestrator.py`
