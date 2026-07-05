# AI Execution Policy Architecture

## Purpose

This document defines the Phase 6.9 execution-policy and runtime-routing architecture for the inactive LLM subsystem.

The goal remains architectural only:

- preserve workflow-first ownership
- preserve Vector-less RAG ownership for deterministic knowledge retrieval
- keep deterministic chat as the default production path
- allow future LLM participation only through explicit policy decisions
- keep routing decisions provider-neutral and disconnected from live runtime wiring

## Scope

`backend/app/llm/execution_policy.py` introduces a standalone execution-policy seam.

It is responsible for:

- evaluating provider-neutral execution-mode requests
- preserving mandatory workflow ownership
- selecting deterministic knowledge routing when knowledge ownership applies
- keeping deterministic chat as the baseline fallback path
- allowing future `LLM_ONLY`, `HYBRID`, and `SHADOW` decisions only when runtime activation is ready
- producing canonical fallback decisions and diagnostics

It is not responsible for:

- provider SDK calls
- prompt construction
- retrieval
- workflow execution
- provider payload translation
- conversation mutation
- appointment validation

## Canonical Models

The execution-policy layer exposes:

- `AIExecutionMode`
- `AIExecutionOwner`
- `AIExecutionFallbackStrategy`
- `AIExecutionPolicyRequest`
- `AIExecutionDecision`
- `AIExecutionActivationSnapshot`
- `AIExecutionDiagnostic`
- `AIExecutionPolicyResult`

These models answer the Phase 6.9 routing questions directly:

- which execution mode was requested
- which execution mode was selected
- who owns the official response
- whether LLM execution may participate
- whether shadow execution may occur
- which fallback path was chosen
- why the decision was made

## Ownership Rules

The execution policy preserves the existing hierarchy:

1. workflow ownership always wins for booking, cancellation, appointment confirmation, and active workflow continuation
2. deterministic knowledge ownership wins when knowledge routing is eligible and a knowledge match is available
3. deterministic chat remains the default production path for all remaining requests
4. LLM participation is optional and activation-aware

This keeps Phase 6.9 aligned with the live `ConversationManager` ownership order without changing the current runtime.

## Execution Modes

The canonical policy currently supports:

- `WORKFLOW_ONLY`
- `DETERMINISTIC_ONLY`
- `KNOWLEDGE_ONLY`
- `LLM_ONLY`
- `HYBRID`
- `SHADOW`

`HYBRID` and `SHADOW` both preserve the baseline deterministic owner as the official response path.

`SHADOW` additionally marks LLM execution as hidden and non-user-visible.

## Activation Dependency

The policy consumes `LLMRuntimeActivationStatus` from Phase 6.8 through a reduced `AIExecutionActivationSnapshot`.

This means routing decisions can respect:

- top-level enablement
- shadow-mode enablement
- selected-provider readiness
- provider health
- generation availability

The execution policy does not evaluate transports, adapters, or authentication on its own. That remains the responsibility of the activation layer.

## Fallback Strategy

Fallback stays provider-neutral and deterministic-safe.

When LLM execution is unavailable, the policy falls back to:

- `USE_WORKFLOW` when workflow ownership is mandatory
- `USE_KNOWLEDGE` when deterministic knowledge ownership applies
- `USE_DETERMINISTIC` for all other requests

Phase 6.9 does not implement comparison logic, response merging, or runtime LLM retries.

## Composition Boundary

Phase 6.9 extends the inactive composition root so the assembled graph now includes:

- `AIExecutionPolicyEvaluator`
- `AIExecutionPolicyService`

This keeps policy evaluation discoverable from the composed LLM seam while remaining disconnected from `ConversationManager`, FastAPI routes, and frontend chat behavior.
