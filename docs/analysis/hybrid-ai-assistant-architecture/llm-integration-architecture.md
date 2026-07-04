# LLM Integration Architecture

## Purpose

This document defines the Phase 6.1 provider-neutral LLM Integration layer for the Doctor Appointment AI Assistant.

The goal of this phase is architectural only:

- define a clean backend boundary for future LLM providers
- keep the current deterministic assistant as the live production path
- avoid any provider SDK, model selection logic, or runtime wiring
- preserve zero API, database, workflow, retrieval, and frontend behavior changes

## Current Status

Phase 6.1 adds an inactive package at `backend/app/llm/`.

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
├── interfaces.py
├── models.py
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

- `LLMProvider`
- `LLMProviderRegistry`

These contracts allow later phases to add provider-specific adapters without changing upstream callers.

### `service.py`

Inactive integration facade:

- `LLMIntegrationService`
- `LLMIntegrationStatus`

The facade exposes three narrow responsibilities:

- report whether the layer is connected
- list registered provider descriptors
- delegate generation only when an explicit provider registry is supplied

The service does not self-configure, auto-discover providers, or attach itself to runtime execution.

## Boundary Rules

This layer must not:

- import or initialize any external LLM SDK
- contain provider-specific request or response mapping
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

1. Add one or more provider adapters that implement `LLMProvider`.
2. Register them behind an explicit `LLMProviderRegistry`.
3. Introduce a narrow caller that passes already-assembled prompt input into `LLMIntegrationService`.
4. Keep deterministic post-processing and business validation outside the LLM layer.
5. Preserve existing chat response contracts unless a later migration explicitly changes them.

## Compatibility Guarantees

Phase 6.1 preserves:

- zero production behavior changes
- zero API changes
- zero database changes
- zero frontend changes
- zero changes to chat orchestration order
- zero changes to workflow ownership
- zero changes to prompt-builder behavior

## Reference Files

- `backend/app/llm/__init__.py`
- `backend/app/llm/models.py`
- `backend/app/llm/interfaces.py`
- `backend/app/llm/service.py`
- `backend/tests/test_llm_integration.py`
