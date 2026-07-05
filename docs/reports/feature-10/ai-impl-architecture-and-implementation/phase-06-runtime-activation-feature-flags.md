# Phase 6.8 Runtime Activation & Feature Flag Architecture

## Summary

Phase 6.8 adds a provider-neutral runtime activation seam on top of the existing inactive LLM composition graph.

The implementation keeps the current deterministic assistant as the only live production path while introducing:

- canonical runtime activation flags in `backend/app/llm/config.py`
- a standalone activation evaluator and safe activation service in `backend/app/llm/activation.py`
- composition-time activation status snapshots in `backend/app/llm/composition.py`
- focused tests for readiness, diagnostics, invalid configuration, inactive mode, and successful activation state

## What Changed

### Runtime flags

Resolved LLM configuration now carries top-level runtime flags for:

- `LLM_ENABLED`
- `LLM_SHADOW_MODE`
- `LLM_ALLOW_GENERATION`
- `LLM_ALLOW_STREAMING`
- `LLM_ALLOW_TOOL_CALLING`
- `LLM_ALLOW_REASONING`

Provider enablement continues to use existing provider-scoped `LLM_<PROVIDER>__ENABLED` settings.

### Activation seam

The new activation module adds:

- `LLMActivationDiagnostic`
- `LLMProviderActivationStatus`
- `LLMRuntimeActivationStatus`
- `LLMRuntimeActivationEvaluator`
- `LLMRuntimeActivationService`

The evaluator checks configuration-driven readiness only. It does not build prompts, route requests, call providers, or mutate state.

### Safe failure behavior

`LLMRuntimeActivationService` wraps composition and converts invalid configuration or dependency-assembly failures into structured inactive diagnostics.

This keeps future startup activation safe without changing any current runtime path.

## Validation

Focused backend coverage now verifies:

- feature-flag evaluation
- deterministic readiness decisions
- disabled-provider handling
- missing transport handling
- invalid configuration handling
- inactive mode
- successful activation state

## Compatibility

This phase does not:

- wire `ConversationManager` to the LLM seam
- change deterministic chat routing
- call any provider SDK
- change FastAPI routes
- change frontend behavior
- change database behavior

The subsystem remains inactive by default and fully backward compatible.
