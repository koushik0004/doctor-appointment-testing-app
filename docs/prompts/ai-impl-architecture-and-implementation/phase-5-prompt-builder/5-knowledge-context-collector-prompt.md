Phase 5 – Step 5.5: Introduce an internal Knowledge Context Collector for the Prompt Builder.

Requirements:
- Add an internal PromptContextKnowledgeCollector beneath the existing Prompt Builder.
- The collector must normalize already-selected KnowledgeDocument objects into the canonical PromptContextKnowledgeContext.
- Preserve deterministic document ordering, included/excluded document tracking, prompt-hint metadata, safe-to-quote flags, context limits, and document metadata.
- Keep the collector deterministic, read-only, and provider-agnostic.
- The collector must not perform retrieval, ranking, semantic search, workflow execution, routing, database access, API calls, or conversation mutation.
- Refactor PromptBuilderService so knowledge normalization is delegated to the Knowledge Context Collector before PromptContext validation and rendering.
- Preserve the existing external PromptBuilderService request/result contract and rendered prompt behavior.
- Do not modify ConversationManager, Vector-less RAG retrieval, WorkflowEngine, frontend, APIs, database, or runtime chatbot behavior.
- Add focused unit tests covering empty knowledge sets, single and multiple documents, deterministic ordering, include/exclude behavior, prompt-hint handling, safe-to-quote processing, context clipping, read-only behavior, and backward compatibility.
- Update the Prompt Builder architecture documentation and project context files to describe the Knowledge Context Collector as the dedicated component responsible for deterministic knowledge normalization before validation and rendering.