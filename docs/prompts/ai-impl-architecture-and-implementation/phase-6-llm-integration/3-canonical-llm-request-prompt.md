# Doctor Appointment AI Assistant

Phase 6.3 — Canonical LLM Request & Response Contract Refinement

Assume all previous phases are complete.

Completed:

✓ Phase 1 — Hybrid AI Assistant Architecture

✓ Phase 2 — Conversation Manager

✓ Phase 3 — Workflow Engine

✓ Phase 4 — Vector-less RAG

✓ Phase 5 — Prompt Builder

✓ Phase 6.1 — LLM Integration Architecture

✓ Phase 6.2 — Provider Abstraction

The current project already contains:

- Provider-neutral LLM integration package
- Provider registry
- Base adapter
- Translation contracts
- Canonical request/response models
- Inactive LLMIntegrationService

Do NOT redesign any of these.

--------------------------------------------------

Objective

Refine the canonical LLM request/response contract so it becomes the long-term internal contract used by every future LLM provider.

This phase is still architecture only.

No provider integration.

No runtime integration.

No production changes.

--------------------------------------------------

Must NOT

- Do NOT integrate OpenAI SDK.
- Do NOT integrate Claude SDK.
- Do NOT integrate Gemini SDK.
- Do NOT integrate OpenRouter SDK.
- Do NOT add API keys.
- Do NOT add authentication.
- Do NOT add HTTP clients.
- Do NOT add retries.
- Do NOT add dependency injection.
- Do NOT modify ConversationManager.
- Do NOT modify WorkflowEngine.
- Do NOT modify Vector-less RAG.
- Do NOT modify Prompt Builder.
- Do NOT modify frontend.
- Do NOT modify backend APIs.
- Do NOT modify database.
- Do NOT modify runtime routing.

--------------------------------------------------

Goal

Review and refine the existing canonical request/response models so they are suitable for all future providers.

The canonical contract should support future capabilities while remaining provider-neutral.

Examples of future capabilities include:

- text generation
- system prompts
- conversation history
- structured JSON responses
- streaming metadata
- tool/function calling metadata
- reasoning metadata
- token usage
- provider metadata
- model metadata
- response finish reasons
- multimodal extensions (future)
- citations (future)

The contract should remain generic enough to support:

- OpenAI
- Claude
- Gemini
- OpenRouter
- Azure OpenAI
- AWS Bedrock
- Vertex AI
- Ollama
- LM Studio
- vLLM
- future providers

without exposing provider-specific request or response formats.

--------------------------------------------------

Responsibilities

Review the current models and refine them where appropriate.

Keep strict separation between:

- canonical request
- canonical response
- provider metadata
- generation constraints
- generation result
- token usage
- finish reasons
- tool invocation metadata
- structured output metadata

Provider-specific payloads must remain inside adapters.

The canonical contract must never leak:

- OpenAI message format
- Claude content blocks
- Gemini request schema
- OpenRouter payloads
- SDK response objects

--------------------------------------------------

Testing

Update only focused tests covering:

- canonical model validation
- backward compatibility
- deterministic serialization
- optional field handling
- future extensibility
- provider neutrality

Do NOT add provider tests.

--------------------------------------------------

Documentation

Update:

- architecture documentation
- Phase 6 report
- AI context files
- report index
- feature map
- important files
- current task

to reflect the refined canonical contract.

--------------------------------------------------

Success Criteria

✓ Provider-neutral canonical contract

✓ Supports future providers

✓ Supports future structured output

✓ Supports future tool calling

✓ Supports future streaming

✓ Supports future multimodal metadata

✓ No provider-specific payload leakage

✓ No runtime integration

✓ No SDK integration

✓ No production behavior changes

✓ No API changes

✓ No database changes

✓ No frontend changes

✓ No workflow changes

✓ No Prompt Builder changes

✓ Full backward compatibility

✓ Prototype-first

✓ Architecture remains simple

✓ Existing tests continue to pass