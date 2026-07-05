# Phase 7.8 — Runtime Response Post Processing

Read this entire prompt before making changes.

Implement ONLY Phase 7.8.

Assume Phases 1–7.7 are complete, tested, and frozen.

Do NOT redesign previous phases.

Maintain full backward compatibility.

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

↓

Runtime Response Composer

↓

Final Runtime Response

------------------------------------------------------------

## Objective

Introduce a provider-neutral Runtime Response Post Processor.

The Post Processor is the final backend stage before a runtime response becomes visible to the frontend.

It must normalize presentation while preserving deterministic business truth.

------------------------------------------------------------

## Introduce

Create a new provider-neutral Runtime Response Post Processor.

Suggested responsibilities:

- normalize response formatting
- normalize whitespace
- normalize line breaks
- normalize markdown
- remove duplicate formatting
- trim leading/trailing whitespace
- sanitize presentation-only metadata
- preserve deterministic business data
- preserve runtime diagnostics separately
- emit deterministic post-processing diagnostics

------------------------------------------------------------

## Runtime Flow

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

↓

Runtime Response Composer

↓

Runtime Response Post Processor

↓

Final Runtime Response

------------------------------------------------------------

## Requirements

The Post Processor MUST NOT

- modify booking IDs
- modify appointment IDs
- modify doctor names
- modify consultation fees
- modify workflow state
- modify business APIs
- modify orchestration metadata
- modify validation results
- modify eligibility results

It MAY

- normalize formatting
- normalize whitespace
- normalize markdown
- remove duplicate blank lines
- remove trailing spaces
- remove presentation-only metadata
- normalize user-visible output

------------------------------------------------------------

## Design Rules

Do NOT modify

- Conversation Manager
- Workflow Engine
- Prompt Builder
- Prompt Renderer
- Provider Adapters
- Vector-less RAG

Reuse

- Runtime Facade
- Runtime Validator
- Runtime Eligibility
- Runtime Response Composer

------------------------------------------------------------

## Testing

Add tests covering

✓ whitespace normalization

✓ duplicate newline removal

✓ markdown normalization

✓ metadata sanitization

✓ deterministic business preservation

✓ hybrid response compatibility

✓ LLM-only compatibility

✓ deterministic-only compatibility

✓ serialization determinism

Run all existing regression tests.

------------------------------------------------------------

## Documentation

Update architecture documentation.

Document

- Runtime Response Post Processor

- processing pipeline

- normalization responsibilities

- presentation guarantees

- modified files

- validation summary

------------------------------------------------------------

## Deliverables

Provide

1. Implementation summary

2. Modified files

3. Architecture decisions

4. Validation results

5. Confirmation that

- Runtime Facade remains the runtime boundary.

- Workflow Engine remains authoritative.

- Response Composer ownership is unchanged.

- Post Processor executes after composition.

- Business truth remains unchanged.

- Presentation normalization is provider-neutral.

- Existing regression tests continue to pass.

- Phase 7.8 is complete.