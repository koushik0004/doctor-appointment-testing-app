# Phase 6.7 Runtime Composition & Dependency Assembly

## Summary

Phase 6.7 adds a single inactive runtime composition root under `backend/app/llm/composition.py`.

This phase remains architecture only:

- no provider SDK integration
- no live API calls
- no chatbot/runtime activation
- no API, frontend, database, workflow, retrieval, or business-logic changes

## What Changed

### 1. Single composition root

`LLMRuntimeCompositionRoot` now assembles the full inactive LLM dependency graph explicitly:

- `LLMConfigurationLoader`
- provider transports
- concrete provider adapters
- `InMemoryLLMProviderRegistry`
- `LLMIntegrationService`
- `LLMGenerationOrchestrator`

The root caches the assembled graph so configuration is loaded exactly once per composition root instance.

### 2. Explicit transport-factory seam

Phase 6.7 adds:

- `LLMProviderTransportFactory`
- `InactiveLLMProviderTransportFactory`

Transport creation remains separate from adapters, and the default inactive factory returns no transports so the subsystem stays disconnected.

### 3. Clear ownership boundaries

This phase moves registry construction responsibility out of `LLMProviderAdapterFactory` and into the composition root.

That keeps ownership aligned with the intended dependency rules:

- adapter factory creates adapters only
- registry owns provider registration only
- composition root owns graph assembly only

### 4. Constructor-only composition

`LLMGenerationOrchestrator` now requires explicit constructor injection for:

- `PromptBuilderService`
- `LLMIntegrationService`

`LLMIntegrationService` now requires explicit constructor injection for:

- `LLMProviderRegistry`

This removes hidden fallback construction from the inactive seam.

### 5. Immutable resolved configuration

Resolved LLM configuration and generation-budget models are now frozen after construction, reinforcing the rule that the configuration loader is the only place allowed to read environment-backed settings.

## Validation

Focused tests in `backend/tests/test_llm_composition.py` verify:

- deterministic composition-root caching
- configuration loading exactly once
- enabled-provider-only registry construction
- disabled-provider exclusion
- transport injection into adapters
- explicit service and orchestrator composition
- continued inactive behavior without transports

The focused LLM suite passed:

`backend/.venv/bin/python -m pytest backend/tests/test_llm_composition.py backend/tests/test_llm_provider_adapters.py backend/tests/test_llm_integration.py backend/tests/test_llm_config.py backend/tests/test_llm_budget.py backend/tests/test_llm_models.py backend/tests/test_llm_orchestrator.py -q`

Result: `43 passed`

## Boundary Confirmation

This phase does not modify:

- `backend/app/services/conversation_manager.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/services/prompt_builder.py`
- `backend/app/knowledge/*`
- FastAPI routes or schemas
- frontend chat code
- database models or persistence

## Outcome

The codebase now has a single inactive composition root that assembles the future LLM subsystem with explicit dependency ownership while preserving the current deterministic assistant as the only live path.
