# Phase 6.6 Concrete Provider Adapters

## Summary

Phase 6.6 extends the inactive `backend/app/llm/` seam with explicit concrete provider adapters for OpenAI, Claude, Gemini, OpenRouter, and Ollama.

This phase remains architecture only:

- no provider SDK integration
- no live API calls
- no runtime wiring into chat orchestration
- no API, frontend, database, workflow, retrieval, or Prompt Builder changes

## What Changed

### 1. Concrete inactive adapters

`backend/app/llm/providers.py` now defines:

- `OpenAIProviderAdapter`
- `ClaudeProviderAdapter`
- `GeminiProviderAdapter`
- `OpenRouterProviderAdapter`
- `OllamaProviderAdapter`

Each adapter:

- accepts canonical `LLMGenerationRequest` input
- translates it into a provider-private payload dictionary
- keeps provider-private budget translation inside the adapter
- translates provider-private responses back into canonical `LLMGenerationResponse`

### 2. Explicit transport seam

The new `LLMProviderTransport` protocol keeps provider invocation explicit and inactive.

Concrete adapters require an injected transport. Without one they raise an inactive-boundary runtime error instead of silently creating clients or making network calls.

### 3. Config-backed adapter factory

`LLMProviderAdapterFactory` can now:

- create the correct concrete adapter for a canonical `LLMProviderConfiguration`
- optionally attach an explicit transport per provider
- build an `InMemoryLLMProviderRegistry` from enabled providers in `LLMConfiguration`
- preserve a configured selected provider as the inactive registry default

This keeps configuration ownership inside `config.py` while avoiding any hidden runtime auto-wiring.

## Validation

Focused tests in `backend/tests/test_llm_provider_adapters.py` verify:

- OpenAI request translation from canonical fields into provider-private payload fields
- Claude response normalization back into canonical response models
- inactive transport enforcement for concrete adapters
- config-backed registry construction from enabled providers
- explicit transport-backed generation delegation through a factory-built adapter

The focused LLM suite passed:

`backend/.venv/bin/python -m pytest backend/tests/test_llm_provider_adapters.py backend/tests/test_llm_integration.py backend/tests/test_llm_config.py backend/tests/test_llm_budget.py backend/tests/test_llm_models.py backend/tests/test_llm_orchestrator.py -q`

Result: `38 passed`

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

The codebase now has implementation-ready inactive concrete provider adapters that preserve the provider-neutral upstream contract, keep provider-private request/response translation contained, and remain disconnected from runtime execution until a later guarded integration phase.
