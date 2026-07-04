Phase 6.2 — Provider Abstraction

Objective:
Design a provider-neutral abstraction for future LLM providers while keeping the integration layer completely inactive.

Requirements:

- Do NOT integrate any LLM SDK.
- Do NOT make any external API calls.
- Do NOT modify the production runtime.
- Do NOT change ConversationManager.
- Do NOT change WorkflowEngine.
- Do NOT change Vector-less RAG.
- Do NOT change Prompt Builder.
- Do NOT change frontend, APIs, or database.

Design a provider abstraction that supports:

- OpenAI
- Anthropic Claude
- Google Gemini
- OpenRouter
- Future providers
- Local/self-hosted models
- Mock providers for testing

The abstraction must ensure that upstream components never depend on any provider-specific SDK, request format, response format, authentication mechanism, or model naming convention.

Design a provider registry capable of discovering and exposing available providers through a common interface only.

Each provider adapter should be responsible only for:

- translating canonical requests into provider-specific requests
- invoking the provider (future phase)
- translating provider-specific responses back into canonical responses
- exposing provider capabilities and metadata
- handling provider-specific errors internally

The provider registry must remain inactive and disconnected from the production runtime.

Do NOT implement any provider adapters yet.
Do NOT add authentication.
Do NOT add API keys.
Do NOT add configuration files.
Do NOT add dependency injection.
Do NOT add feature flags.
Do NOT add runtime routing.

Produce only the architecture, interfaces, internal contracts, documentation, and focused tests necessary to validate the abstraction.

Success Criteria:

- Provider-neutral architecture
- OpenAI-ready
- Claude-ready
- Gemini-ready
- OpenRouter-ready
- Future-provider ready
- Local-model ready
- Mock-provider ready
- Zero production behavior changes
- Zero API changes
- Zero frontend changes
- Zero database changes
- Zero workflow changes
- Full backward compatibility
- Prototype-first