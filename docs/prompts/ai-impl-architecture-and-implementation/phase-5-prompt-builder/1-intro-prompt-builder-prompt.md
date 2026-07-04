Phase 5 – Step 5.1: Introduce a standalone Prompt Builder module as a deterministic orchestration component.

Requirements:
- Add a new Prompt Builder service/module to the backend architecture.
- Do not modify the Conversation Manager, Workflow Engine, Vector-less RAG, Business Services, or Chat Widget behavior.
- Define a clear internal service contract for prompt construction.
- Ensure the Prompt Builder only accepts context from existing modules and does not perform routing, retrieval, workflow execution, database access, API calls, or AI reasoning.
- Keep the module inactive in the production request flow for now; it should be independently instantiable and testable.
- Preserve complete backward compatibility and avoid any external API or UI changes.