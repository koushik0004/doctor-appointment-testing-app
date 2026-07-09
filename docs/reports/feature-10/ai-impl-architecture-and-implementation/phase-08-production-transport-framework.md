# Phase 08 Production Transport Framework

Date: 2026-07-07

## Summary

Phase 08 completes the first live provider boundary in the provider-neutral runtime by adding a production Claude transport backed by the official Anthropic Python SDK.

The existing architecture was preserved:

- Prompt Builder unchanged
- Conversation Manager unchanged
- Workflow Engine unchanged
- Runtime validation unchanged
- Runtime eligibility unchanged
- Runtime composer unchanged
- Runtime post processor unchanged

The work only fills the missing transport/framework gap identified by `docs/reports/feature-10/llm-runtime-investigation.md`.

## Implemented

### 1. Claude transport

Added `backend/app/llm/transport.py` with:

- `ClaudeTransport`
- `LLMTransportError`
- `LLMTransportActivationSnapshot`

`ClaudeTransport` now owns:

- Anthropic client construction
- timeout configuration
- SDK retry configuration
- request translation from the existing Claude adapter payload
- raw response parsing when available
- request-id extraction
- response-id extraction
- usage extraction
- structured transport logging
- normalized provider error mapping
- runtime activation diagnostics

### 2. Production transport factory

Added `ProductionLLMProviderTransportFactory` in `backend/app/llm/composition.py`.

Behavior:

- inspects resolved provider configuration
- creates transports only for enabled providers
- currently composes only Claude
- leaves unsupported providers transport-inactive without redesigning the adapter or registry architecture

### 3. Default composition path updated

`LLMRuntimeCompositionRoot` now defaults to `ProductionLLMProviderTransportFactory` instead of `InactiveLLMProviderTransportFactory`.

That means the production runtime path is now:

Configuration
-> Production transport factory
-> Claude transport
-> Claude adapter
-> Registry
-> Integration service
-> Orchestrator

The public facade and orchestration layers were not redesigned.

### 4. Claude adapter response enrichment

Updated `backend/app/llm/providers.py` so Claude canonical response translation now also maps normalized citation data carried by the transport metadata.

## Runtime Behavior

What is live now:

- If Claude is enabled and selected, the default composition root creates a real Claude transport.
- Hidden shadow execution can now reach the Anthropic SDK instead of failing at a missing transport boundary.
- Controlled generation can also reach Claude when runtime activation and execution policy allow it.

What is still unchanged:

- Visible chat remains deterministic and knowledge-backed by default.
- OpenAI, Gemini, OpenRouter, and Ollama still do not have production transports.
- No Prompt Builder or workflow ownership rules changed.

## Error Handling

Claude transport normalizes these cases into `LLMTransportError`:

- 401 -> `authentication_error`
- 403 -> `permission_denied`
- 404 -> `not_found`
- 408 / timeout exceptions -> `timeout`
- 429 -> `rate_limited`
- 500 -> `server_error`
- 503 -> `service_unavailable`
- connection failures -> `network_error`
- any other SDK exception -> `sdk_exception`

Each normalized error carries provider name, optional status code, optional request id, retryability, and metadata.

## Logging

Structured transport logs now emit these fields without exposing secrets:

- provider
- model
- request_id
- response_id
- latency_ms
- input_tokens
- output_tokens
- finish_reason
- status_code

## Diagnostics

Claude transport now exposes an activation snapshot used by `LLMRuntimeActivationEvaluator`.

That snapshot reports:

- whether the transport is operationally available
- SDK availability issues
- missing-auth issues
- timeout/retry/base-url metadata for activation diagnostics

## Tests

Added `backend/tests/test_llm_transport.py` covering:

- Anthropic request invocation through a mocked client
- response normalization
- generation-budget-derived max token resolution
- SDK status error mapping
- timeout mapping
- activation snapshot diagnostics
- production factory behavior
- default composition behavior
- optional live Claude integration

Broader regression run:

```bash
pytest backend/tests/test_llm_*.py -q
```

Observed result during implementation:

- `112 passed`
- `1 skipped` optional live integration test

## Dependency Updates

Added backend dependency metadata for the official Anthropic SDK in:

- `backend/pyproject.toml`
- `backend/requirements.txt`

## Files Changed

- `backend/app/llm/transport.py`
- `backend/app/llm/composition.py`
- `backend/app/llm/activation.py`
- `backend/app/llm/providers.py`
- `backend/app/llm/__init__.py`
- `backend/tests/test_llm_transport.py`
- `backend/pyproject.toml`
- `backend/requirements.txt`
- `README.md`
- `.env.example`

## Validation

Commands run:

```bash
pytest backend/tests/test_llm_transport.py backend/tests/test_llm_provider_adapters.py backend/tests/test_llm_composition.py backend/tests/test_llm_activation.py -q
pytest backend/tests/test_llm_*.py -q
```
