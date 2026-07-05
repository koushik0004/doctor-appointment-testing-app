# Phase 6.5.5 Provider-Neutral Generation Budget Architecture

## Summary

Added an inactive provider-neutral generation-budget seam under `backend/app/llm/` so future LLM adapters can translate canonical reasoning, token, latency, quality, and cost intent into provider-private request parameters without changing runtime behavior today.

## What Changed

- Added `backend/app/llm/budget.py` with canonical budget enums, reusable budget models, deterministic profile catalogs, profile override support, and an adapter-facing translation protocol.
- Extended `backend/app/llm/models.py` so `LLMGenerationRequest` can optionally carry a canonical `generation_budget` object while preserving backward-compatible defaults.
- Extended `backend/app/llm/config.py` so global and per-provider settings can declare a default generation profile plus canonical profile overrides without wiring any provider runtime.
- Updated `backend/app/llm/__init__.py` exports and `.env.example` documentation for the new inactive generation-budget configuration surface.
- Added focused tests for budget validation, default-profile resolution, serialization determinism, provider neutrality, request backward compatibility, and config-driven global/provider overrides.

## Architecture Notes

- The new budget seam remains fully inactive and is not imported by `ConversationManager`, `WorkflowEngine`, `PromptBuilderService`, `LLMGenerationOrchestrator`, API routes, or frontend code.
- Canonical profiles are currently `FAST`, `BALANCED`, `WORKFLOW`, `QUALITY`, and `MAXIMUM`.
- Budget controls stay provider-neutral by using canonical concepts such as reasoning effort, output budget, context budget, latency preference, quality preference, and cost preference.
- Translation from canonical budget intent to provider-native request fields remains the responsibility of future adapters.

## Validation

Focused tests now cover:

- invalid token-budget relationships
- deterministic default-profile resolution
- profile overrides without caller mutation
- deterministic serialization
- provider-neutral canonical shape
- configuration-driven global and per-provider budget profile overrides
- backward-compatible `LLMGenerationRequest` defaults
