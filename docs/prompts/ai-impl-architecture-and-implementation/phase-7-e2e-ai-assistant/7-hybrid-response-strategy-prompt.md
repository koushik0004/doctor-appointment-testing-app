# Phase 7.7 — Hybrid Response Strategy

Read this entire prompt before making changes.

Implement ONLY Phase 7.7.

Assume Phases 1–7.6 are complete, tested, and frozen.

Do NOT redesign previous phases.

Maintain backward compatibility.

Reuse all existing runtime components.

------------------------------------------------------------

## Current Runtime

Conversation Manager

↓

Workflow Engine

↓

LLMRuntimeFacade

↓

Execution Policy

↓

Prompt Builder

↓

LLMGenerationOrchestrator

↓

Provider

↓

Runtime Validator

↓

Runtime Eligibility

------------------------------------------------------------

## Objective

Introduce a provider-neutral Hybrid Response Strategy.

The runtime must now support three response modes:

- Deterministic only
- LLM only
- Hybrid (Deterministic + LLM augmentation)

The Runtime Facade remains the single runtime boundary.

------------------------------------------------------------

## Introduce

Create a provider-neutral Runtime Response Composer.

Suggested responsibilities:

- compose the final runtime response
- preserve deterministic business truth
- optionally augment deterministic responses with validated and eligible LLM content
- produce deterministic composition diagnostics
- remain provider-neutral

The composer must execute only after runtime validation and eligibility.

------------------------------------------------------------

## Runtime Flow

Execution Policy

↓

Prompt Builder

↓

Prompt Renderer

↓

LLMGenerationOrchestrator

↓

Provider

↓

Runtime Validator

↓

Runtime Eligibility

↓

Runtime Response Composer

↓

Final Runtime Response

------------------------------------------------------------

## Composition Modes

Support:

1. Deterministic Only

Return only deterministic response.

2. LLM Only

Return validated eligible LLM response.

3. Hybrid

Compose:

Deterministic Business Response

+

Optional LLM enhancement

Examples of enhancement:

- additional explanation

- friendly guidance

- healthcare preparation tips

- follow-up suggestions

The LLM must never replace business truth.

------------------------------------------------------------

## Safety Rules

The composer must NEVER modify:

- booking IDs

- appointment IDs

- workflow decisions

- doctor names

- dates

- times

- consultation fees

- payment status

- API results

- workflow ownership

The composer may only augment.

------------------------------------------------------------

## Design Rules

Do NOT modify:

- Conversation Manager

- Workflow Engine

- Prompt Builder

- Prompt Renderer

- Provider Adapters

- Vector-less RAG

- Business APIs

Reuse:

- Runtime Facade

- Execution Policy

- Runtime Validator

- Runtime Eligibility

------------------------------------------------------------

## Testing

Add tests covering:

✓ deterministic composition

✓ LLM-only composition

✓ hybrid composition

✓ business fields preserved

✓ augmentation appended correctly

✓ validation compatibility

✓ eligibility compatibility

✓ deterministic fallback

✓ serialization determinism

Run existing regression tests.

------------------------------------------------------------

## Documentation

Update:

- architecture documentation

- feature map

- current task

- report index

- AI context

Include:

- Runtime Response Composer

- composition modes

- hybrid response flow

- deterministic preservation

- augmentation rules

- modified files

- validation summary

------------------------------------------------------------

## Deliverables

Provide:

1. Implementation summary

2. Modified files

3. Architecture decisions

4. Validation results

5. Confirmation that:

- Runtime Facade remains the runtime boundary.

- Workflow Engine remains authoritative.

- Vector-less RAG ownership is unchanged.

- Validation executes before eligibility.

- Eligibility executes before composition.

- Response Composer is provider-neutral.

- Business truth remains deterministic.

- LLM only augments approved responses.

- Phase 7.7 is complete.