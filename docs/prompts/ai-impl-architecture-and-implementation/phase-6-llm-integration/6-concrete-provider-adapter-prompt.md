# Doctor Appointment AI Assistant

Phase 6.6 — First Concrete Provider Adapter (OpenRouter)

Assume Phases 1–6.5.5 are complete.

The project already contains:

✓ Prompt Builder
✓ Canonical PromptContext
✓ Prompt Assembly Pipeline
✓ PromptRenderer
✓ LLM Generation Orchestrator
✓ Canonical Request/Response Contracts
✓ Provider Registry
✓ Base Provider Adapter
✓ Provider Configuration
✓ Generation Budget
✓ Environment Configuration

Do NOT redesign any existing module.

--------------------------------------------------

Objective

Implement the first concrete provider adapter using OpenRouter.

This phase introduces the first real provider implementation while keeping the production runtime completely disconnected.

No ConversationManager integration.

No WorkflowEngine integration.

No Prompt Builder runtime wiring.

--------------------------------------------------

Requirements

Implement:

- OpenRouterProviderAdapter
- OpenRouter request translator
- OpenRouter response translator
- Provider registration
- Authentication using the existing configuration layer
- HTTP client abstraction
- Error normalization into canonical provider-neutral errors
- Mapping between canonical generation budget and OpenRouter request parameters

Use only the existing canonical contracts and provider interfaces.

--------------------------------------------------

Must NOT

- Do NOT modify ConversationManager.
- Do NOT modify WorkflowEngine.
- Do NOT modify Vector-less RAG.
- Do NOT modify Prompt Builder.
- Do NOT modify frontend.
- Do NOT modify backend APIs.
- Do NOT modify runtime routing.
- Do NOT enable automatic LLM execution.
- Do NOT implement streaming.
- Do NOT implement tool calling.
- Do NOT implement MCP.
- Do NOT replace deterministic chatbot.

--------------------------------------------------

Responsibilities

The adapter should:

- translate canonical requests to OpenRouter payloads
- authenticate using the configuration layer
- invoke the OpenRouter API
- translate responses into canonical models
- map provider errors into canonical errors
- map canonical generation budgets into OpenRouter request fields
- expose provider capabilities

The adapter must not:

- build prompts
- collect context
- perform retrieval
- execute workflows
- validate business rules
- mutate conversation state

--------------------------------------------------

Testing

Add focused tests covering:

- request translation
- response translation
- authentication configuration
- generation budget mapping
- error normalization
- deterministic serialization
- provider registration
- mocked HTTP interactions

No live network calls in automated tests.

--------------------------------------------------

Documentation

Update:

- LLM Integration Architecture
- Provider Adapter documentation
- OpenRouter integration guide
- AI Context files
- Feature Map
- Important Files
- Report Index
- Current Task

--------------------------------------------------

Success Criteria

✓ First concrete provider adapter

✓ Uses existing configuration layer

✓ Uses existing generation budget

✓ Uses canonical contracts

✓ Provider-neutral architecture preserved

✓ No runtime wiring

✓ No production behavior changes

✓ No API changes

✓ No frontend changes

✓ No database changes

✓ No workflow changes

✓ Deterministic chatbot remains primary

✓ Fully backward compatible