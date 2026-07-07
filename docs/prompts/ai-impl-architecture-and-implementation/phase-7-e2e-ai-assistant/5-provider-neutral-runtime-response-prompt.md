# Phase 7.5 — Provider-Neutral Runtime Response Validation

Read this entire prompt before making any changes.

Implement ONLY Phase 7.5.

Assume Phases 1–7.4 are complete, stable, tested, and frozen.

Do NOT redesign any previous architecture.

Do NOT simplify existing layers.

Reuse every existing component whenever possible.

Backward compatibility is mandatory.

------------------------------------------------------------

## Existing Runtime

ConversationManager

↓

Workflow Engine

↓

LLMRuntimeFacade

↓

Execution Policy

↓

LLMGenerationOrchestrator

↓

PromptBuilderService

↓

PromptRenderer

↓

LLMIntegrationService

↓

Provider Adapter

↓

Generated Runtime Result

------------------------------------------------------------

## Objective

Introduce a provider-neutral Runtime Response Validation layer.

The validator becomes the mandatory quality gate between runtime generation and any future visible LLM response.

The validator MUST remain provider-neutral.

Do NOT place validation logic inside:

- provider adapters
- Prompt Builder
- Prompt Renderer
- Orchestrator
- ConversationManager
- Workflow Engine

The Runtime Facade should own invocation of the validator.

------------------------------------------------------------

## Required Architecture

Introduce a new backend LLM validation seam.

Suggested responsibilities:

- canonical response validation
- response completeness validation
- empty output detection
- malformed structured-output detection
- finish-reason validation
- optional metadata validation
- provider-neutral diagnostics
- deterministic validation result

The validator must operate only on canonical LLM models.

It must never inspect provider-native payloads.

------------------------------------------------------------

## Runtime Flow

Controlled Generation

↓

Prompt Builder

↓

Prompt Renderer

↓

LLMGenerationOrchestrator

↓

LLMIntegrationService

↓

Canonical Response

↓

NEW Runtime Response Validator

↓

Validation Result

↓

Return validated runtime result

or

deterministic fallback

------------------------------------------------------------

## Validation Behaviour

The validator should reject cases such as:

- empty generated content
- whitespace-only content
- malformed structured output
- invalid finish reason
- invalid canonical metadata
- missing required canonical fields

The validator must NOT:

- perform business validation
- validate medical correctness
- inspect appointment workflows
- inspect Vector-less RAG retrieval
- inspect provider payloads

------------------------------------------------------------

## Runtime Behaviour

If validation succeeds:

Return a validated runtime result.

If validation fails:

Return deterministic fallback.

Never expose validation exceptions.

Never expose provider internals.

Never change current APIs.

------------------------------------------------------------

## Design Rules

Reuse existing canonical models.

Reuse existing runtime diagnostics.

Keep Prompt Builder unchanged.

Keep Prompt Renderer unchanged.

Keep Orchestrator unchanged.

Keep Provider Adapters unchanged.

Keep Execution Policy unchanged.

Keep Runtime Activation unchanged.

Keep ConversationManager unchanged.

------------------------------------------------------------

## Testing

Add focused tests covering:

✓ valid runtime response

✓ empty response rejection

✓ whitespace response rejection

✓ malformed structured-output rejection

✓ invalid finish reason

✓ validator diagnostics

✓ deterministic fallback after validation failure

✓ backward compatibility

Existing regression suites must continue passing.

------------------------------------------------------------

## Documentation

Update:

- architecture documentation

- AI context

- feature map

- current task

- report index

Include:

- validation pipeline

- validator responsibilities

- fallback behaviour

- architectural decisions

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

- Runtime Facade remains the only runtime entry point.

- Prompt Builder remains the only prompt owner.

- Provider adapters remain provider-private.

- Response validation is provider-neutral.

- Deterministic fallback still exists.

- No production behaviour changed by default.

- Phase 7.5 is complete.