# ADR 001: Keep The Deterministic AI Engine As The Primary Execution Layer

## Status

Accepted

## Date

2026-06-28

## Context

The current Doctor Appointment AI Assistant already delivers production-relevant behavior through deterministic chat intent detection, entity extraction, doctor search, availability lookup, and manual booking handoff.

The system currently serves a bounded set of use cases:

- doctor discovery
- appointment availability lookup
- consultation fee lookup
- booking help
- cancellation guidance

These use cases depend on structured, testable outputs and on the same backend domain services that power the manual booking flow.

At the same time, the codebase has explicit future ambitions around richer orchestration, assistant-led workflows, and possible LLM-assisted interpretation. Introducing those mechanisms as the primary engine now would add operational complexity and increase behavioral variance before the manual booking system has been expanded into automation-safe flows.

## Decision

The deterministic backend assistant remains the primary execution layer.

This means:

- `backend/app/services/chat_service.py` remains the canonical assistant entry point.
- intent routing remains rule-based first
- entity extraction remains deterministic first
- doctor and availability answers remain grounded in existing backend services
- chat remains informational and navigational, not execution-oriented

Future AI capabilities may be added only as optional layers around this core, not as a replacement for domain validation and domain response assembly.

## Rationale

- Predictability: appointment guidance is easier to validate when routing is deterministic.
- Contract stability: the frontend widget already expects structured response payloads.
- Data grounding: the assistant reuses authoritative doctor and availability services instead of maintaining parallel knowledge paths.
- Safety: the current system avoids autonomous state changes during chat.
- Delivery speed: the existing architecture already works and can evolve incrementally.

## Consequences

Positive:

- Regression testing remains straightforward.
- Existing API and widget contracts remain intact.
- AI evolution can happen behind stable service boundaries.
- The assistant can improve without destabilizing booking behavior.

Negative:

- Language understanding remains narrower than an LLM-driven assistant.
- New intents require deterministic implementation work.
- The workflow layer remains intentionally limited until explicitly expanded.

## Alternatives Considered

### 1. Replace The Deterministic Engine With An LLM-First Assistant

Rejected because:

- it would increase variance in intent routing and structured output generation
- it would require stronger guardrails before handling booking-related flows
- it would create unnecessary risk without solving a current blocking product need

### 2. Introduce A Workflow Agent As The Primary Booking Executor

Rejected because:

- the current frontend adapter is intentionally noop for operational actions
- chat does not yet own the user-consent and execution model needed for safe automation
- the existing manual booking flow is the validated mutation path today

### 3. Split AI Logic Across Frontend And Backend

Rejected because:

- it would duplicate business interpretation logic
- it would weaken the single source of truth for assistant behavior
- it would make compatibility harder across frontend surfaces

## Guardrails For Future Changes

- Keep state-changing actions outside chat unless explicitly redesigned.
- Keep final domain validation inside backend services.
- Preserve the current chat schema or version it deliberately.
- Add new AI layers as adapters or coordinators, not as replacements for domain truth.

## Related Document

- `docs/hybrid-ai-assistant-master-architecture.md`
