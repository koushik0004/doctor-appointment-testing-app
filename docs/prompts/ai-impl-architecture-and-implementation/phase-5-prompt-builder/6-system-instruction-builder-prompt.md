Phase 5 – Step 5.6: Introduce an internal System Instruction Builder for the Prompt Builder.

Requirements:
- Add an internal PromptContextSystemInstructionBuilder beneath the existing Prompt Builder.
- The builder must construct the canonical PromptContextSystemInstructions section from deterministic application rules and caller-supplied instructions.
- Preserve deterministic instruction ordering, remove duplicate instructions while keeping the first occurrence, and keep the output provider-agnostic.
- Keep the builder read-only and deterministic.
- The builder must not perform workflow execution, knowledge retrieval, routing, AI reasoning, conversation mutation, database access, API calls, or LLM integration.
- Refactor PromptBuilderService so system instruction construction is delegated to the System Instruction Builder before PromptContext validation and rendering.
- Preserve the existing PromptBuilderService request/result contract and rendered prompt behavior.
- Do not modify ConversationManager, WorkflowEngine, Vector-less RAG retrieval, frontend, APIs, database, or runtime chatbot behavior.
- Add focused unit tests covering empty instructions, default instructions, caller instructions, merged instructions, duplicate elimination with deterministic ordering, read-only behavior, and backward compatibility.
- Update the architecture documentation, feature map, important files, current task, and session context to document the System Instruction Builder as the dedicated deterministic component responsible for constructing PromptContext system instructions before validation and rendering.