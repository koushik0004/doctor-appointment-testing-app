# Doctor Appointment AI Assistant

Phase 6.9 — AI Execution Policy & Runtime Routing

Assume all previous phases are complete and verified.

Completed

✓ Phase 1 — Hybrid AI Assistant Architecture

✓ Phase 2 — Conversation Manager

✓ Phase 3 — Workflow Engine

✓ Phase 4 — Vector-less RAG

✓ Phase 5 — Prompt Builder

✓ Phase 6.1 — LLM Integration Architecture

✓ Phase 6.2 — Provider Abstraction

✓ Phase 6.3 — Canonical Request / Response Contracts

✓ Phase 6.4 — LLM Generation Orchestrator

✓ Phase 6.5 — Provider Configuration

✓ Phase 6.5.5 — Generation Budget

✓ Phase 6.6 — Concrete Provider Adapters

✓ Phase 6.7 — Runtime Composition

✓ Phase 6.8 — Runtime Activation

The project already contains:

✓ Deterministic Chatbot

✓ ConversationManager

✓ WorkflowEngine

✓ Vector-less RAG

✓ Prompt Builder

✓ Runtime Composition

✓ Runtime Activation

✓ Provider Registry

✓ Generation Budget

✓ LLMGenerationOrchestrator

✓ LLMIntegrationService

Everything remains backward compatible.

Do NOT redesign previous phases.

--------------------------------------------------

Objective

Design the AI Execution Policy responsible for deciding which AI execution path should be used for every incoming request.

This phase introduces routing architecture only.

Do NOT redesign existing runtime.

Do NOT replace deterministic routing.

Do NOT activate LLM by default.

--------------------------------------------------

Execution Modes

Design provider-neutral execution modes.

Examples include:

- DETERMINISTIC_ONLY
- KNOWLEDGE_ONLY
- LLM_ONLY
- HYBRID
- SHADOW

The architecture may refine or extend these modes if a better design exists.

--------------------------------------------------

Responsibilities

Design an AI Execution Policy component responsible for determining:

- whether WorkflowEngine owns the request
- whether Vector-less RAG owns the request
- whether deterministic chat owns the request
- whether the LLM may participate
- whether shadow execution should occur
- whether execution should fall back

The execution policy should produce a provider-neutral execution decision.

--------------------------------------------------

Execution Decision

Design a canonical execution decision model.

It should contain concepts such as:

- selected execution mode
- selected provider (if applicable)
- activation state
- routing reason
- fallback strategy
- execution diagnostics

without exposing provider-specific implementation details.

--------------------------------------------------

Routing Rules

Preserve the existing ownership hierarchy.

Workflow Engine must always remain the source of truth for:

- booking
- cancellation
- appointment confirmation
- workflow continuation
- workflow validation

Vector-less RAG must remain responsible for deterministic knowledge retrieval.

The deterministic chatbot remains the default production execution path.

LLM participation must be optional and policy-driven.

--------------------------------------------------

Shadow Mode

Design architecture for future shadow execution.

In shadow mode:

- deterministic response remains the official response
- LLM executes independently
- user never sees LLM output
- execution metrics can be collected
- comparison becomes possible

Do NOT implement runtime comparison logic.

Design the architecture only.

--------------------------------------------------

Fallback Strategy

Design provider-neutral fallback decisions.

Examples:

- activation unavailable
- provider unavailable
- transport unavailable
- timeout
- generation failure
- invalid response

Fallback should always preserve existing deterministic behavior.

--------------------------------------------------

Boundaries

The Execution Policy must NOT:

- call provider SDKs
- build prompts
- retrieve knowledge
- execute workflows
- mutate conversation state
- validate appointments
- translate provider payloads

It should only make routing decisions.

--------------------------------------------------

Testing

Add focused tests covering:

- workflow ownership
- knowledge ownership
- deterministic ownership
- activation-aware routing
- shadow mode routing
- disabled provider routing
- fallback routing
- execution decision serialization
- deterministic execution decisions

No provider API calls.

No SDK execution.

No production runtime activation.

--------------------------------------------------

Documentation

Update:

- AI Execution Policy Architecture
- Runtime Activation Architecture
- LLM Integration Architecture
- Runtime Composition Architecture
- Phase 6 Report
- AI Context
- Feature Map
- Important Files
- Report Index
- Current Task

--------------------------------------------------

Success Criteria

✓ Provider-neutral execution policy

✓ Canonical execution decision

✓ Workflow ownership preserved

✓ Vector-less RAG ownership preserved

✓ Deterministic chatbot remains default

✓ Optional LLM participation

✓ Shadow-mode architecture

✓ Provider-neutral fallback

✓ Runtime activation respected

✓ No provider SDK changes

✓ No ConversationManager redesign

✓ No WorkflowEngine redesign

✓ No Prompt Builder redesign

✓ No Vector-less RAG redesign

✓ No frontend changes

✓ No backend API changes

✓ No database changes

✓ No production behavior changes

✓ Fully backward compatible

✓ Prototype-first

--------------------------------------------------

Architecture Principles

The AI Execution Policy should become the single authority responsible for deciding how an AI request is executed.

Execution Policy determines WHAT should execute.

ConversationManager coordinates the request lifecycle.

WorkflowEngine owns business workflows.

Vector-less RAG owns deterministic knowledge retrieval.

Prompt Builder constructs prompts.

LLMGenerationOrchestrator coordinates generation.

Provider adapters communicate with external providers.

No component should duplicate another component's responsibility.

Maintain strict separation of concerns.

Prepare the architecture for future phases involving production rollout, A/B testing, provider selection strategies, adaptive routing, and multi-provider orchestration without introducing production behavior changes in this phase.