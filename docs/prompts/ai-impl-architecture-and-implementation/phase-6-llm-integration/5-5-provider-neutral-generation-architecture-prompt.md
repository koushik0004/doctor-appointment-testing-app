# Doctor Appointment AI Assistant

Phase 6.5.5 — Provider-Neutral Generation Budget Architecture

Assume Phases 1–6.5 are complete.

The project already contains:

✓ Prompt Builder
✓ Canonical PromptContext
✓ Prompt Assembly Pipeline
✓ PromptRenderer
✓ Provider-neutral LLM Integration
✓ Provider Registry
✓ Canonical Request/Response Contracts
✓ LLM Generation Orchestrator
✓ Provider Configuration Layer

Do NOT redesign any existing module.

--------------------------------------------------

Objective

Introduce a provider-neutral Generation Budget architecture that allows future LLM providers to control reasoning effort, token usage, latency, and generation quality through a single canonical abstraction.

This phase remains architecture only.

No runtime wiring.

No provider SDK integration.

No API calls.

No production behavior changes.

--------------------------------------------------

Must NOT

- Do NOT integrate OpenAI SDK.
- Do NOT integrate Claude SDK.
- Do NOT integrate Gemini SDK.
- Do NOT integrate OpenRouter SDK.
- Do NOT modify ConversationManager.
- Do NOT modify WorkflowEngine.
- Do NOT modify PromptBuilder.
- Do NOT modify LLMGenerationOrchestrator.
- Do NOT modify runtime routing.
- Do NOT expose provider-specific reasoning or token parameters outside adapters.

--------------------------------------------------

Design Goals

Create a provider-neutral Generation Budget model that represents how much reasoning, token budget, latency, and quality should be allocated for an LLM request.

The Generation Budget must be independent of any provider-specific terminology.

Adapters will later translate this canonical budget into provider-native parameters.

--------------------------------------------------

The canonical budget should support concepts such as:

- generation profile
- reasoning effort
- maximum output token budget
- context token budget
- latency preference
- quality preference
- cost preference

without exposing provider-specific field names.

--------------------------------------------------

Support future providers including:

- OpenAI
- Claude
- Gemini
- OpenRouter
- Ollama
- Azure OpenAI
- AWS Bedrock
- Vertex AI
- future providers

--------------------------------------------------

Add

- provider-neutral generation budget models
- deterministic validation
- configuration integration
- sensible default profiles
- profile override capability
- translation contracts (architecture only)
- focused tests
- documentation updates

--------------------------------------------------

Suggested default profiles

FAST

BALANCED

WORKFLOW

QUALITY

MAXIMUM

The implementation may refine these names if a better provider-neutral design exists.

--------------------------------------------------

Testing

Add focused tests covering

- deterministic budget validation
- default profile selection
- profile overrides
- serialization
- backward compatibility
- provider neutrality

--------------------------------------------------

Documentation

Update

- LLM Integration Architecture
- Generation Budget Architecture
- Phase 6 report
- AI Context
- Feature Map
- Important Files
- Report Index
- Current Task

--------------------------------------------------

Success Criteria

✓ Provider-neutral generation budget

✓ Supports reasoning effort

✓ Supports token budget

✓ Supports latency preference

✓ Supports quality preference

✓ Supports cost preference

✓ Supports reusable generation profiles

✓ Adapter translation remains future responsibility

✓ No runtime wiring

✓ No provider SDK

✓ No API changes

✓ No frontend changes

✓ No database changes

✓ No workflow changes

✓ Fully backward compatible

✓ Prototype-first