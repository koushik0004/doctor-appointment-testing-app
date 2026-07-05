# LLM Operational Readiness Architecture

## Purpose

This document defines the Phase 6.10 production-readiness and operational-excellence architecture for the inactive LLM subsystem.

The goal remains architectural only:

- prepare the provider-neutral LLM seam for production-grade operations
- keep deterministic chat as the current production execution path
- preserve zero runtime activation and zero rollout
- keep provider-neutral operational concerns outside live chat routing

## Scope

`backend/app/llm/operations.py` introduces a standalone operational-readiness seam.

It is responsible for:

- canonical observability and trace models
- provider-neutral token accounting and cost accounting models
- canonical health reporting derived from runtime activation state
- retry-policy and timeout-policy models for future runtime transport layers
- audit-trail and privacy/redaction models
- rollout-policy and performance-metric models
- a safe composed service that describes operational readiness without enabling runtime behavior

It is not responsible for:

- provider SDK calls
- live retries
- transport execution
- prompt building
- workflow execution
- knowledge retrieval
- runtime routing changes
- frontend or API behavior changes

## Canonical Models

The operational-readiness layer exposes:

- `LLMTraceContext`
- `LLMTimingBreakdown`
- `LLMObservabilityRecord`
- `LLMObservabilityPolicy`
- `LLMTokenAccounting`
- `LLMCostBreakdown`
- `LLMCostRollup`
- `LLMOperationalHealthStatus`
- `LLMHealthDiagnostic`
- `LLMProviderHealthReport`
- `LLMOperationalHealthReport`
- `LLMRetryPolicy`
- `LLMTimeoutPolicy`
- `LLMAuditTrailRecord`
- `LLMSecurityPrivacyPolicy`
- `LLMRolloutPolicy`
- `LLMPerformanceMetrics`
- `LLMOperationalReadinessProfile`

These models answer the Phase 6.10 production-readiness questions directly without changing runtime ownership or activation.

## Observability

Phase 6.10 adds provider-neutral observability models for:

- structured logging
- request IDs
- execution IDs
- correlation IDs
- provider latency timing
- orchestration timing
- prompt-builder timing
- execution-policy timing

The seam records the architecture required for those signals but does not emit logs or traces by itself.

## Accounting

Phase 6.10 separates accounting into two canonical layers:

- token accounting
- cost accounting

Token accounting supports:

- prompt tokens
- completion tokens
- cached tokens
- reasoning tokens
- total tokens
- provider/model attribution

Cost accounting supports:

- per-request cost totals
- daily rollups
- monthly rollups
- provider/model attribution

Both layers stay provider-neutral and deterministic.

## Health, Retry, And Timeout Policy

Health reporting is derived from the Phase 6.8 activation seam.

This keeps health ownership split cleanly:

- `activation.py` decides readiness and emits diagnostics
- `operations.py` translates that readiness into operational health reporting

Retry and timeout policy remain architecture-only:

- no retries are executed
- no backoff scheduler is implemented
- no transport timeout behavior is changed

The new models simply define the canonical contracts future runtime code can consume.

## Audit, Security, And Rollout

Phase 6.10 adds provider-neutral models for:

- request and execution audit identifiers
- provider/model attribution
- execution mode and routing ownership snapshots
- generation-profile tracking
- audit visibility levels
- prompt/response redaction policy
- PII-safe logging expectations
- disabled, shadow, gradual, targeted, and general rollout states

No rollout is activated in this phase. The rollout model exists only as an explicit future boundary.

## Composition Boundary

Phase 6.10 extends the inactive composition root so the assembled graph now includes:

- `LLMOperationalReadinessEvaluator`
- `LLMOperationalReadinessService`

This keeps production-readiness evaluation discoverable from the composed LLM seam while remaining disconnected from `ConversationManager`, FastAPI routes, frontend chat behavior, and any live provider runtime.
