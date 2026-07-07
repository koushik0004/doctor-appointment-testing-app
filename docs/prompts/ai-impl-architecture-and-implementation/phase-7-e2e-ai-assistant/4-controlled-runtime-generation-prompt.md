# Phase 7.4 — Controlled Runtime Generation

## IMPORTANT

Read this entire prompt before making any changes.

Implement ONLY Phase 7.4.

Assume Phases 1 through 7.3 are fully implemented, tested and frozen.

Do NOT redesign any existing architecture.

Do NOT simplify previous layers.

Reuse all existing services.

Keep the implementation small, incremental and production-safe.

Backward compatibility is mandatory.

------------------------------------------------------------

## Existing Architecture (Already Implemented)

Production Runtime

Chat Widget
→ Conversation Manager
→ Workflow Engine
→ AI Runtime Facade

Existing AI Runtime

Prompt Builder
→ Prompt Renderer
→ LLM Generation Orchestrator
→ LLM Integration Service
→ Provider Registry
→ Provider Adapter

Supporting Runtime

Runtime Activation
Execution Policy
Operational Readiness
Composition Root

Shadow Mode already exists.

Prompt Builder is already fully integrated.

------------------------------------------------------------

## Objective

Move from:

Hidden LLM execution only

to

Controlled runtime generation.

This DOES NOT mean enabling AI for everyone.

It means the runtime becomes capable of returning an LLM response ONLY when explicitly allowed by the existing Runtime Activation and Execution Policy.

------------------------------------------------------------

## Fundamental Rules

Workflow Engine always owns workflows.

Vector-less RAG always owns knowledge retrieval.

Business APIs remain the source of truth.

Prompt Builder remains the only prompt creator.

AIRuntimeFacade remains the only runtime boundary.

Execution Policy remains the only routing decision maker.

Never bypass any of these layers.

------------------------------------------------------------

## Required Runtime Behaviour

Reuse the existing Runtime Activation.

Reuse the existing Execution Policy.

Extend AIRuntimeFacade so it supports two execution paths:

1.

Default

Return the existing deterministic response.

(Current production behaviour.)

2.

Controlled Runtime Generation

If ALL existing runtime conditions allow generation:

- Execute the existing Prompt Builder pipeline.
- Generate through the existing Orchestrator.
- Return the generated runtime result to the facade.

Do not duplicate orchestration logic.

Reuse the existing implementation.

------------------------------------------------------------

## Feature Flag Behaviour

Reuse the existing runtime activation flags.

Do NOT introduce new feature flags unless absolutely required.

Generation must remain disabled by default.

Existing deployments must continue behaving exactly as before.

------------------------------------------------------------

## Execution Policy

Reuse the existing policy service.

Generation should only occur when the policy explicitly selects an LLM-capable mode.

If the policy selects:

- WORKFLOW
- KNOWLEDGE
- DETERMINISTIC
- SHADOW

behaviour must remain unchanged.

Only LLM-capable execution modes may invoke visible runtime generation.

------------------------------------------------------------

## Safety

If generation fails:

- Never fail the request.
- Never expose provider errors.
- Fall back using the existing execution policy.
- Preserve current user experience.

No database changes.

No API contract changes.

No frontend changes.

------------------------------------------------------------

## Testing

Verify:

✓ Existing workflows unchanged.

✓ Existing RAG unchanged.

✓ Existing deterministic routing unchanged.

✓ Existing shadow mode still works.

✓ Runtime generation works only when explicitly enabled.

✓ Runtime generation disabled by default.

✓ Existing regression tests pass.

Add focused tests for:

- policy-controlled generation

- disabled generation

- fallback on generation failure

- deterministic compatibility

------------------------------------------------------------

## Documentation

Update:

- architecture report

- AI context

- feature map

- current task

Include:

- controlled runtime generation

- execution flow

- feature flag behaviour

- fallback behaviour

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

- AIRuntimeFacade is the only runtime entry point.

- Prompt Builder remains the only prompt owner.

- Execution Policy remains the routing authority.

- Runtime generation is feature-flag controlled.

- Default production behaviour is unchanged.

- Phase 7.4 is complete.