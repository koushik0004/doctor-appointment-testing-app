# Doctor Appointment AI Assistant

Phase 6.8 — Runtime Activation & Feature Flag Architecture

Assume all previous phases are complete.

Completed

✓ Phase 1 — Hybrid AI Assistant Architecture

✓ Phase 2 — Conversation Manager

✓ Phase 3 — Workflow Engine

✓ Phase 4 — Vector-less RAG

✓ Phase 5 — Prompt Builder

✓ Phase 6.1 — LLM Integration Architecture

✓ Phase 6.2 — Provider Abstraction

✓ Phase 6.3 — Canonical Contracts

✓ Phase 6.4 — LLM Generation Orchestrator

✓ Phase 6.5 — Provider Configuration

✓ Phase 6.5.5 — Generation Budget

✓ Phase 6.6 — Concrete Provider Adapters

✓ Phase 6.7 — Runtime Composition

The project already contains:

✓ Runtime Composition Root

✓ Provider Registry

✓ Provider Configuration

✓ Generation Budget

✓ Prompt Builder

✓ Provider Adapters

✓ Transport Factory

✓ LLMIntegrationService

✓ LLMGenerationOrchestrator

Everything remains inactive.

Do NOT redesign previous phases.

--------------------------------------------------

Objective

Design the Runtime Activation layer that determines whether the LLM subsystem is enabled while preserving the deterministic chatbot as the default production path.

This phase introduces activation architecture only.

Do NOT redesign routing.

Do NOT integrate ConversationManager with the LLM.

Do NOT replace the deterministic chatbot.

--------------------------------------------------

Design Goals

Introduce a provider-neutral runtime activation policy.

The activation layer should answer:

- Is the LLM subsystem enabled?
- Is the selected provider enabled?
- Is the provider healthy?
- Is configuration valid?
- Can generation proceed?
- Should activation fail safely?
- How should inactive status be reported?

Activation should be deterministic and configuration-driven.

--------------------------------------------------

Requirements

Design an activation layer responsible for:

- validating runtime readiness
- validating provider availability
- validating required configuration
- exposing activation status
- exposing provider readiness
- exposing generation availability
- exposing activation diagnostics

The activation layer must not:

- execute prompts
- perform routing
- call providers
- build prompts
- retrieve knowledge
- execute workflows
- mutate conversation state

--------------------------------------------------

Feature Flags

Design feature flags for:

LLM_ENABLED

LLM_PROVIDER_ENABLED

LLM_SHADOW_MODE

LLM_ALLOW_GENERATION

LLM_ALLOW_STREAMING

LLM_ALLOW_TOOL_CALLING

LLM_ALLOW_REASONING

The flags should integrate cleanly with the existing configuration layer.

--------------------------------------------------

Readiness Checks

Design provider-neutral readiness checks covering:

- configuration loaded
- provider enabled
- adapter available
- transport available
- authentication configured
- generation budget resolved

The result should be represented through canonical activation models.

--------------------------------------------------

Failure Strategy

Activation failures must never:

- crash startup
- affect booking workflows
- affect deterministic chat
- affect Vector-less RAG

Instead expose structured diagnostics while leaving the deterministic runtime fully operational.

--------------------------------------------------

Testing

Add focused tests covering:

- feature flag evaluation
- readiness evaluation
- disabled provider handling
- missing API key
- missing transport
- invalid configuration
- inactive mode
- successful activation state
- deterministic activation decisions

No provider API calls.

No SDK execution.

No runtime routing.

--------------------------------------------------

Documentation

Update:

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

✓ Runtime activation isolated

✓ Feature-flag driven

✓ Provider-neutral

✓ Configuration-driven

✓ Safe startup

✓ Safe shutdown

✓ Readiness diagnostics

✓ No provider SDK changes

✓ No runtime routing

✓ No ConversationManager changes

✓ No WorkflowEngine changes

✓ No Prompt Builder changes

✓ No Vector-less RAG changes

✓ No frontend changes

✓ No backend API changes

✓ No database changes

✓ No production behavior changes

✓ Fully backward compatible

✓ Prototype-first

--------------------------------------------------

Architecture Principles

Maintain the existing layered architecture.

Keep activation independent of routing.

Keep routing independent of provider implementations.

Keep deterministic mode as the default production behavior.

Prepare the architecture for later phases involving runtime routing, shadow mode, and production rollout without introducing any behavior changes in this phase.