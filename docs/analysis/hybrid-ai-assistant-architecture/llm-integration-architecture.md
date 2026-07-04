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

## Boundary Rules

This layer must not:

- import or initialize any external LLM SDK
- expose provider-native payload shapes to upstream callers
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

The Prompt Builder remains an inactive formatting seam that produces provider-neutral prompt context and rendered prompt text. It does not invoke the LLM layer in this phase.

## Future Integration Path

Later phases may connect this layer in a guarded way:

1. Add one or more provider adapters that subclass `BaseLLMProviderAdapter` and satisfy `LLMProvider`.
2. Keep provider-native request and response payloads private to those adapters.
3. Register them behind an explicit `LLMProviderRegistry`.
4. Optionally declare a default provider through configuration-owned registry setup.
5. Introduce a narrow caller that passes already-assembled prompt input into `LLMIntegrationService`.
6. Keep deterministic post-processing and business validation outside the LLM layer.
7. Preserve existing chat response contracts unless a later migration explicitly changes them.

## Provider Abstraction Rules

Future adapter implementations should:

- accept only canonical `LLMGenerationRequest` input from upstream
- emit only canonical `LLMGenerationResponse` output upstream
- translate provider-native payloads entirely inside the adapter
- keep SDK clients, auth, retry policy, and transport details inside the adapter
- avoid leaking provider-specific enums, IDs, tool-call payloads, or message formats outside `backend/app/llm/`
- rely on deterministic domain validation outside the adapter after model output returns

## Focused Validation

Focused tests now validate:

- disconnected status remains the default
- explicit provider listing and default-provider resolution remain inactive-only
- the shared adapter pipeline translates canonical requests and responses without exposing provider-native payloads upstream
- duplicate provider registration is rejected deterministically

## Compatibility Guarantees

Phase 6.2 preserves:

- zero production behavior changes
- zero API changes
- zero database changes
- zero frontend changes
- zero changes to chat orchestration order
- zero changes to workflow ownership
- zero changes to prompt-builder behavior

## Reference Files

- `backend/app/llm/__init__.py`
- `backend/app/llm/adapters.py`
- `backend/app/llm/models.py`
- `backend/app/llm/interfaces.py`
- `backend/app/llm/registry.py`
- `backend/app/llm/service.py`
- `backend/tests/test_llm_integration.py`
