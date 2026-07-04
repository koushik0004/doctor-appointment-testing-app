Phase 5 – Step 5.3: Introduce an internal Conversation Context Collector for the Prompt Builder.

Requirements:
- Add an internal Conversation Context Collector beneath the existing Prompt Builder.
- The collector must normalize caller-supplied conversation state into the Conversation Context section of the canonical PromptContext model.
- Preserve chronological ordering, current user message, previous turns, assistant turns, and existing conversation metadata where available.
- Keep the collector deterministic and read-only; it must not perform intent detection, entity extraction, workflow execution, knowledge retrieval, summarization, routing, or conversation mutation.
- Refactor PromptBuilderService so it delegates conversation normalization to the collector before PromptContext validation and rendering.
- Preserve the existing external PromptBuilderService contract and rendered prompt output.
- Do not modify ConversationManager, WorkflowEngine, Vector-less RAG, APIs, frontend, database, or runtime chat behavior.
- Add focused unit tests covering empty, single-turn, and multi-turn conversations, deterministic normalization, metadata preservation, and backward compatibility with existing Prompt Builder tests.
- Update the architecture documentation to describe the Conversation Context Collector as an internal Prompt Builder component responsible only for deterministic conversation normalization.