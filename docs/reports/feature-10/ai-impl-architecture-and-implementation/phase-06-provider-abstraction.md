# Phase 6.2 Provider Abstraction

## Summary

Phase 6.2 refines the inactive `backend/app/llm/` seam so future provider adapters can translate between canonical internal models and provider-native payloads without exposing provider details upstream.

This phase remains architectural only:

- no LLM SDK
- no OpenAI, Claude, Gemini, or any concrete provider implementation
- no runtime wiring into chat orchestration
- no API, frontend, database, workflow, retrieval, or Prompt Builder changes

## What Changed

### 1. Translator contracts

`backend/app/llm/interfaces.py` now defines:

- `LLMRequestTranslator`
- `LLMResponseTranslator`
- refined `LLMProvider`
- refined `LLMProviderRegistry`

These contracts make the provider-adapter responsibility explicit:

- upstream callers send canonical `LLMGenerationRequest`
- adapters translate that request into provider-native payloads internally
- adapters translate provider-native responses back into canonical `LLMGenerationResponse`

### 2. Shared adapter pipeline

`backend/app/llm/adapters.py` adds `BaseLLMProviderAdapter`.

This base class provides the canonical adapter flow:

1. translate canonical request
2. invoke provider privately
3. translate provider response
4. normalize canonical provider and model metadata when absent

No provider implementation was added in this phase.

### 3. Explicit inactive registry

`backend/app/llm/registry.py` adds `InMemoryLLMProviderRegistry`.

It supports:

- explicit provider registration
- deterministic listing
- provider lookup by name
- duplicate-name rejection
- optional default-provider resolution

The registry remains inactive and is not attached to production startup or request handling.

### 4. Integration-facade refinement

`backend/app/llm/service.py` now allows `LLMIntegrationService` to resolve the provider name in this order:

1. explicit `generate(..., provider_name=...)`
2. explicit service default
3. registry default provider name

The service still reports `enabled=False` and remains disconnected from production runtime.

## Validation

Focused tests in `backend/tests/test_llm_integration.py` now verify:

- inactive status with no registry
- provider listing via a registry
- canonical adapter translation flow
- inactive default-provider resolution
- duplicate registration rejection
- failure when no runtime registry is configured

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

The codebase now has a clearer inactive adapter boundary for future provider implementations while preserving the deterministic assistant as the only live execution path.
