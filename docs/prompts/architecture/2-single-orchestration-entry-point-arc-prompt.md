Goal:
Introduce a Conversation Manager as the single orchestration entry point for all chat requests while preserving the existing deterministic chatbot behavior.

Scope:
- Design and implement a Conversation Manager responsible for:
  - maintaining conversation context
  - tracking conversation lifecycle
  - accumulating extracted entities
  - resolving contextual references
  - routing requests to the Deterministic Engine, Workflow Engine, or future AI layer
- Define a canonical conversation context model.
- Update the chat request/response contracts to support optional conversation metadata while maintaining backward compatibility.
- Ensure existing doctor search, availability search, FAQ, booking help, and cancellation help continue to function unchanged.
- Keep all business execution inside existing services and future Workflow Engine.

Out of Scope:
- No LLM integration.
- No workflow execution.
- No booking or cancellation implementation.
- No vector-less RAG.
- No database schema expansion beyond what is minimally required for conversation state.
- No frontend redesign.

Acceptance Criteria:
- All chat requests flow through the Conversation Manager.
- Multi-turn context can be maintained and resolved.
- Routing decisions are centralized.
- Existing deterministic functionality remains unchanged.
- The architecture is ready for Workflow Engine integration in the next phase.