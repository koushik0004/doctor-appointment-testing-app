# LLM Runtime Composition Architecture

## Purpose

This document defines the Phase 6.7 runtime composition layer for the inactive LLM subsystem, updated in Phase 6.8 to include deterministic activation-status assembly.

The goal remains architectural only:

- assemble the existing LLM seams into one explicit dependency graph
- keep configuration loading, transport creation, adapter creation, registry creation, and service/orchestrator composition in one place
- preserve zero production activation
- preserve zero API, database, workflow, retrieval, and frontend behavior changes

## Composition Root

`backend/app/llm/composition.py` is the single composition root for the inactive subsystem.

It owns:

- loading `LLMConfiguration` exactly once through `LLMConfigurationLoader`
- resolving enabled providers from immutable configuration
- creating provider transports through a dedicated transport-factory seam
- creating provider adapters through `LLMProviderAdapterFactory`
- constructing `InMemoryLLMProviderRegistry`
- resolving the configured default provider
- creating `LLMIntegrationService`
- creating `LLMGenerationOrchestrator`
- evaluating runtime activation status from the resolved graph

It does not own:

- prompt building logic
- retrieval
- workflow execution
- routing
- provider payload translation
- provider SDK initialization

## Dependency Graph

The explicit construction order is:

1. `LLMConfigurationLoader.load()`
2. `LLMProviderTransportFactory.create_transports()`
3. `LLMProviderAdapterFactory.create_adapter()` for each enabled provider
4. `LLMRuntimeActivationEvaluator.evaluate(...)`
5. `InMemoryLLMProviderRegistry(...)`
6. `LLMIntegrationService(...)`
7. `LLMGenerationOrchestrator(...)`

All dependencies are passed by constructor injection. No environment-variable reads happen outside the configuration loader.

## Transport Strategy

Transport creation stays separate from adapters.

Phase 6.7 adds:

- `LLMProviderTransportFactory`
- `InactiveLLMProviderTransportFactory`

The default inactive transport factory returns no transports, so enabled providers can still be assembled while remaining unable to call a live provider.

This preserves a clean extension point for future:

- HTTP transports
- mocked transports
- recording transports
- retry-enabled transports

## Inactive Boundary

The subsystem remains inactive because:

- no production runtime imports the composition root
- the default transport factory returns no live transports
- adapters still require explicit transport injection to invoke anything
- `LLMIntegrationService` can resolve providers, but provider generation still fails at the adapter boundary when no transport exists
- activation status can report readiness, but it does not activate routing or execute generation by itself

## Testing Scope

Focused composition tests validate:

- deterministic one-time configuration loading per composition root
- enabled-provider registration only
- disabled-provider exclusion
- transport injection into adapters
- activation-status assembly from the composed graph
- explicit service and orchestrator composition
- continued inactive behavior without transports
