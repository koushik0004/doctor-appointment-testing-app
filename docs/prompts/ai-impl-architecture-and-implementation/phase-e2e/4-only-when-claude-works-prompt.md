Claude production transport is complete.

Use it as the reference implementation.

Implement production transports for:

- OpenAI
- Gemini
- OpenRouter
- Ollama

Requirements:

- Reuse the same transport framework.
- Do NOT duplicate business logic.
- Do NOT modify existing adapters.
- Do NOT redesign runtime architecture.
- Follow the same dependency injection pattern used for Claude.
- Add provider-specific SDK/HTTP implementation only inside transport classes.
- Extend the ProductionLLMProviderTransportFactory to instantiate transports based on configuration.
- Update tests and documentation accordingly.
- Generate an implementation report describing new providers, modified files, validation steps, and manual testing instructions.