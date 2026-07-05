# Doctor Appointment AI Assistant

Phase 6.5 — Provider Configuration Architecture

Assume Phases 1–6.4 are complete.

The project already contains:

✓ Prompt Builder
✓ Canonical PromptContext
✓ Prompt Assembly Pipeline
✓ PromptRenderer
✓ Provider-neutral LLM Integration
✓ Provider Registry
✓ Canonical Request/Response Contracts
✓ LLM Generation Orchestrator

Do NOT redesign any existing module.

--------------------------------------------------

Objective

Introduce a provider-neutral configuration layer for future LLM integrations.

This phase remains architecture only.

No runtime wiring.

No provider SDK.

No API changes.

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
- Do NOT call any provider.
- Do NOT perform API requests.

--------------------------------------------------

Design a dedicated configuration layer.

The configuration layer should expose provider-neutral settings while supporting multiple providers.

Support configuration for:

- OpenAI
- Claude
- Gemini
- OpenRouter
- Ollama
- Future providers

Configuration should include:

- provider selection
- default model
- API keys
- optional base URLs
- timeout
- retry settings
- feature flags
- provider enable/disable

--------------------------------------------------

Add:

- configuration models
- configuration loader
- environment mapping
- validation
- deterministic defaults
- `.env.example`
- provider-neutral configuration documentation

--------------------------------------------------

Testing

Add focused tests covering:

- deterministic configuration loading
- missing optional keys
- missing required keys
- provider validation
- default values
- environment mapping
- backward compatibility

--------------------------------------------------

Documentation

Update:

- LLM Integration Architecture
- Phase 6 report
- AI Context
- Feature Map
- Important Files
- Report Index
- Current Task

--------------------------------------------------

Success Criteria

✓ Configuration isolated

✓ SDK-independent

✓ Provider-neutral

✓ Supports OpenAI

✓ Supports Claude

✓ Supports Gemini

✓ Supports OpenRouter

✓ Supports Ollama

✓ `.env.example` added

✓ No runtime wiring

✓ No production behavior changes

✓ No API changes

✓ No Prompt Builder changes

✓ No ConversationManager changes

✓ No WorkflowEngine changes

✓ Fully backward compatible