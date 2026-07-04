# Doctor Appointment AI Assistant

Phase 6.4 — LLM Generation Orchestrator

Assume all previous phases are complete.

Completed:

✓ Phase 1 — Hybrid AI Assistant Architecture
✓ Phase 2 — Conversation Manager
✓ Phase 3 — Workflow Engine
✓ Phase 4 — Vector-less RAG
✓ Phase 5 — Prompt Builder
✓ Phase 6.1 — LLM Integration Architecture
✓ Phase 6.2 — Provider Abstraction
✓ Phase 6.3 — Canonical Request & Response Contract Refinement

The project already contains:

- Prompt Builder
- Canonical PromptContext
- Prompt Assembly Pipeline
- PromptRenderer
- LLM Integration Layer
- Provider Registry
- Base Provider Adapter
- Canonical LLM Request/Response Contracts
- Inactive LLMIntegrationService

Do NOT redesign any existing module.

--------------------------------------------------

Objective

Introduce an inactive **LLM Generation Orchestrator** that coordinates prompt generation and LLM invocation through existing abstractions while remaining completely disconnected from the production runtime.

This phase is architecture only.

No runtime integration.

No provider SDKs.

No production behavior changes.

--------------------------------------------------

Must NOT

- Do NOT integrate OpenAI.
- Do NOT integrate Claude.
- Do NOT integrate Gemini.
- Do NOT integrate OpenRouter.
- Do NOT integrate any SDK.
- Do NOT modify ConversationManager.
- Do NOT modify WorkflowEngine.
- Do NOT modify Vector-less RAG.
- Do NOT modify Prompt Builder.
- Do NOT modify backend APIs.
- Do NOT modify frontend.
- Do NOT modify database.
- Do NOT modify runtime routing.
- Do NOT add dependency injection.
- Do NOT add configuration.
- Do NOT add feature flags.
- Do NOT implement retries.
- Do NOT implement streaming.
- Do NOT implement tool calling.

--------------------------------------------------

Goal

Design a thin orchestration layer that coordinates:

Prompt Builder
→ Canonical Prompt
→ Canonical LLM Request
→ LLM Integration Service
→ Canonical LLM Response
→ Normalized Generation Result

The orchestrator should only coordinate existing components.

It must not contain business logic.

It must not construct prompts directly.

It must not know provider payloads.

It must not perform workflow routing.

It must not retrieve knowledge.

It must not validate appointments.

It must not mutate conversation state.

--------------------------------------------------

Responsibilities

The orchestrator should:

- accept already collected generation input
- invoke Prompt Builder
- transform PromptBuildResult into the canonical LLM request
- delegate generation to LLMIntegrationService
- normalize the returned canonical response
- expose a simple provider-neutral result
- remain completely provider-neutral
- remain completely inactive until a future runtime integration phase

--------------------------------------------------

Testing

Add focused tests validating:

- orchestration order
- delegation behavior
- Prompt Builder invocation
- LLMIntegrationService invocation
- canonical transformation
- deterministic behavior
- no provider dependency
- no runtime wiring

--------------------------------------------------

Documentation

Update:

- LLM Integration Architecture
- Phase 6 report
- AI Context files
- Feature Map
- Report Index
- Important Files
- Current Task

--------------------------------------------------

Success Criteria

✓ Thin orchestration layer

✓ Prompt Builder remains independent

✓ Provider abstraction preserved

✓ Canonical request preserved

✓ Canonical response preserved

✓ Zero SDK integration

✓ Zero provider implementation

✓ Zero runtime wiring

✓ Zero production behavior changes

✓ Zero API changes

✓ Zero frontend changes

✓ Zero database changes

✓ Zero workflow changes

✓ Zero Prompt Builder changes

✓ Full backward compatibility

✓ Prototype-first

✓ Simple architecture