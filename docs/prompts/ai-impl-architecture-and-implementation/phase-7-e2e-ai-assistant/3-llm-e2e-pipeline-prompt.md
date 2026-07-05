# Phase 7.3 — Prompt Builder → LLM End-to-End Pipeline

## Read Carefully

Implement ONLY Phase 7.3.

Assume Phases 1–7.2 are complete, tested and frozen.

Do NOT redesign any existing architecture.

Reuse all existing services.

Do NOT change production behaviour.

Do NOT change API contracts.

Do NOT modify Workflow Engine logic.

Do NOT modify Vector-less RAG logic.

Do NOT modify Conversation Manager logic.

Do NOT bypass the Prompt Builder.

Keep the implementation simple.

Prototype-first.

Backward compatible.

--------------------------------------------------

## Current Architecture

Production Runtime

Chat Widget
→ Conversation Manager
→ Workflow Engine
→ AI Runtime Facade

Existing AI Components

Conversation Collector
Workflow Collector
Knowledge Collector
Canonical PromptContext
Prompt Builder
Prompt Renderer
LLM Generation Orchestrator
Provider Registry
Provider Adapter
Runtime Activation
Execution Policy

Shadow Mode already exists from Phase 7.2.

Currently the user still receives ONLY deterministic responses.

--------------------------------------------------

## Objective

Connect the existing Prompt Builder into the runtime so that every shadow LLM execution uses the complete prompt pipeline.

The LLM must NO LONGER receive manually assembled prompt strings.

Instead it must always receive the rendered output produced by the Prompt Builder.

The Prompt Builder becomes the ONLY prompt creation mechanism.

--------------------------------------------------

## Required Runtime Flow

Implement the following runtime flow.

Conversation

↓

Conversation Collector

↓

Workflow Collector

↓

Knowledge Collector

↓

Canonical PromptContext

↓

Prompt Builder

↓

Prompt Renderer

↓

Rendered Prompt

↓

LLM Generation Orchestrator

↓

Provider Registry

↓

Provider Adapter

↓

Shadow Response

↓

Diagnostics

↓

Discard Response

The deterministic chatbot response must still be returned to the user.

--------------------------------------------------

## Functional Requirements

1.

Reuse the existing Conversation Collector.

Do not duplicate conversation extraction.

--------------------------------------------------

2.

Reuse the existing Workflow Collector.

Do not duplicate workflow information.

--------------------------------------------------

3.

Reuse the existing Knowledge Collector.

Knowledge must continue to originate from the existing Vector-less RAG.

--------------------------------------------------

4.

Construct the Canonical PromptContext.

Reuse the existing PromptContext model.

Do not introduce another prompt model.

--------------------------------------------------

5.

Invoke the existing Prompt Builder.

It becomes the only place responsible for prompt creation.

--------------------------------------------------

6.

Invoke the existing Prompt Renderer.

The renderer should produce the final prompt supplied to the LLM.

--------------------------------------------------

7.

Pass ONLY the rendered prompt to the existing LLM Generation Orchestrator.

No manual prompt strings.

No inline prompt concatenation.

No duplicated prompt logic.

--------------------------------------------------

8.

Continue using the existing Runtime Activation and Execution Policy.

Do not introduce another runtime decision layer.

--------------------------------------------------

9.

Continue running in Shadow Mode.

The generated LLM response must be discarded after diagnostics.

The user must continue receiving only deterministic responses.

--------------------------------------------------

10.

Reuse existing dependency injection.

Reuse existing Composition Root.

Do not introduce service locators.

--------------------------------------------------

## Safety Requirements

Do not change:

- Workflow routing
- Business APIs
- Deterministic chatbot
- Vector-less RAG
- Existing request contracts
- Existing response contracts
- Existing frontend behaviour

No database migration.

No schema changes.

--------------------------------------------------

## Validation Checklist

Verify that:

✓ Prompt Builder is invoked for every shadow execution.

✓ Conversation Collector executes correctly.

✓ Workflow Collector executes correctly.

✓ Knowledge Collector executes correctly.

✓ Canonical PromptContext is created.

✓ Prompt Renderer produces the final prompt.

✓ LLM Orchestrator receives only rendered prompts.

✓ Provider Adapters remain unchanged.

✓ Shadow Mode still functions.

✓ User responses remain identical.

✓ Existing tests continue passing.

--------------------------------------------------

## Documentation

Update the implementation report.

Include:

- Runtime flow
- Prompt generation flow
- Prompt ownership
- Integration point
- Architectural decisions
- Modified files
- Validation results
- Remaining work before user-visible AI responses

--------------------------------------------------

## Deliverables

Provide:

1. Summary of implementation.

2. List of modified files.

3. Architecture decisions.

4. Validation results.

5. Confirmation that:

- Prompt Builder is now fully integrated.
- PromptContext is the only prompt model.
- Prompt Builder is the single source of prompt generation.
- Production behaviour remains unchanged.
- Phase 7.3 is complete.