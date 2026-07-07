# Phase 7.6 — Controlled User-visible LLM Responses

Read this entire prompt before making any changes.

Implement ONLY Phase 7.6.

Assume Phases 1–7.5 are complete, tested and frozen.

Do NOT redesign any previous architecture.

Reuse every existing component.

Backward compatibility is mandatory.

Keep the implementation incremental and production-safe.

------------------------------------------------------------

## Existing Runtime

Conversation Manager

↓

Workflow Engine

↓

LLMRuntimeFacade

↓

Execution Policy

↓

LLMGenerationOrchestrator

↓

Prompt Builder

↓

LLM Provider

↓

Runtime Response Validator

------------------------------------------------------------

## Objective

Allow the runtime to return validated LLM responses ONLY for explicitly approved low-risk scenarios.

This is NOT a routing redesign.

The existing Workflow Engine remains the primary routing authority.

The Runtime Facade becomes responsible for deciding whether a validated LLM response may be exposed to the user.

------------------------------------------------------------

## Introduce

Create a provider-neutral Runtime Response Eligibility layer.

Suggested responsibilities:

- determine whether a validated LLM response is eligible for user visibility
- evaluate only canonical runtime information
- remain independent from provider implementations
- produce deterministic eligibility decisions and diagnostics

Do NOT place eligibility logic inside:

- Conversation Manager
- Workflow Engine
- Prompt Builder
- Prompt Renderer
- Provider Adapters
- Orchestrator
- Vector-less RAG

The Runtime Facade should invoke this layer only after successful runtime validation.

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

Runtime Response Validator

↓

Runtime Response Eligibility

↓

Eligible ?

      │

 ┌────┴─────┐

 │          │

Yes         No

 │          │

LLM Reply   Deterministic Reply

------------------------------------------------------------

## Eligibility Rules

Initially allow ONLY low-risk conversational scenarios.

Examples:

- greetings

- thanks

- conversational acknowledgements

- simple informational conversation

- FAQ-style responses already allowed by policy

Continue using deterministic responses for:

- booking

- cancellation

- rescheduling

- appointment confirmation

- workflow execution

- doctor search

- appointment availability

- payments

- business APIs

- any workflow-owned request

Reuse the existing Execution Policy wherever possible.

Do NOT duplicate routing logic.

------------------------------------------------------------

## Safety

Only validated responses may reach the eligibility layer.

If eligibility fails:

- preserve deterministic response

- never expose provider errors

- never expose validator errors

- never bypass Workflow Engine

- never bypass Vector-less RAG

------------------------------------------------------------

## Design Rules

Reuse:

- Runtime Facade

- Execution Policy

- Runtime Validator

- Prompt Builder

- Orchestrator

- Runtime Activation

Avoid duplicate routing or policy services.

Keep provider neutrality.

------------------------------------------------------------

## Testing

Add tests covering:

✓ eligible conversational response

✓ non-eligible workflow request

✓ booking request remains deterministic

✓ cancellation remains deterministic

✓ validation + eligibility interaction

✓ deterministic fallback

✓ backward compatibility

All existing regression tests must continue passing.

------------------------------------------------------------

## Documentation

Update:

- architecture documentation

- current task

- feature map

- report index

- AI context

Include:

- runtime response eligibility

- user-visible response flow

- eligibility rules

- deterministic preservation

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

- Runtime Facade remains the single runtime boundary.

- Workflow Engine remains the routing authority.

- Vector-less RAG ownership is unchanged.

- Runtime Validator executes before eligibility.

- Eligibility is provider-neutral.

- Only approved scenarios may return LLM responses.

- Workflow scenarios remain deterministic.

- Phase 7.6 is complete.