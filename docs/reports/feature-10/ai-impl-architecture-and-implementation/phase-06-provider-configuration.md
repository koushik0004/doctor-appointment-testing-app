# Phase 6.5 Provider Configuration Architecture

## Summary

Phase 6.5 adds an inactive provider-neutral configuration layer to the existing LLM seam under `backend/app/llm/`.

This phase remains architectural only:

- no provider SDK
- no runtime wiring into chat orchestration
- no API, frontend, database, workflow, retrieval, Prompt Builder, or orchestrator behavior changes

## What Changed

### 1. Dedicated provider-neutral configuration models

Added `backend/app/llm/config.py` with:

- `LLMProviderName`
- `LLMProviderFeatureFlags`
- `LLMProviderEnvironmentSettings`
- `LLMProviderConfiguration`
- `LLMConfiguration`

These models represent configuration for OpenAI, Claude, Gemini, OpenRouter, Ollama, and future providers without exposing any provider SDK or transport client.

### 2. Deterministic configuration loader and environment mapping

Added:

- `LLMConfigurationSettings`
- `LLMConfigurationLoader`
- `get_llm_configuration()`

The settings layer maps nested environment variables such as `LLM_OPENAI__API_KEY` and `LLM_OLLAMA__FEATURE_FLAGS__STREAMING` into canonical provider-neutral models with deterministic defaults for timeout and retry behavior.

### 3. Validation rules stay inside the config seam

Validation now guarantees:

- selected providers must also be enabled
- enabled providers must declare a default model name
- enabled non-Ollama providers must declare an API key
- disabled providers remain optional and backward compatible
- provider-specific timeout and retry settings override global defaults deterministically

### 4. `.env.example` now documents the seam

Added a root `.env.example` that documents:

- app-level settings already used elsewhere in the repo
- global inactive LLM configuration defaults
- provider-specific enablement, model, key, base URL, timeout, retry, and feature-flag variables

This file documents the environment mapping only. It does not activate any runtime path.

### 5. Focused validation coverage

Added `backend/tests/test_llm_config.py` covering:

- deterministic loading
- missing optional keys
- missing required keys
- selected-provider validation
- default propagation
- nested environment mapping
- backward-compatible inactive defaults

## Boundary Confirmation

This phase does not modify:

- `backend/app/services/conversation_manager.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/services/prompt_builder.py`
- `backend/app/llm/orchestrator.py`
- `backend/app/knowledge/*`
- FastAPI routes or schemas
- frontend chat code
- database models or persistence

## Validation

Focused suite:

`backend/.venv/bin/python -m pytest backend/tests/test_llm_config.py backend/tests/test_llm_integration.py backend/tests/test_llm_models.py backend/tests/test_llm_orchestrator.py -q`

Observed result:

- `26 passed`

## Outcome

The codebase now has an implementation-ready but inactive provider-neutral configuration seam for future LLM adapters and registry setup, while preserving SDK independence, deterministic defaults, backward compatibility, and zero production runtime changes.
