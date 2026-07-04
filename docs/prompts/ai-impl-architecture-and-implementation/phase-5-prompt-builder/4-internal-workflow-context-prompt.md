Phase 5 – Step 5.4: Introduce an internal Workflow Context Collector for the Prompt Builder.

Requirements:
- Add an internal Workflow Context Collector beneath the existing Prompt Builder.
- The collector must normalize caller-supplied workflow state into the Workflow Context section of the canonical PromptContext model.
- Preserve active workflow identity, workflow status, collected fields, missing fields, workflow metadata, and original workflow state where available.
- Keep the collector deterministic, read-only, and provider-agnostic.
- The collector must not perform workflow execution, business validation, routing, entity extraction, knowledge retrieval, conversation mutation, database access, or API calls.
- Refactor PromptBuilderService so workflow normalization is delegated to the Workflow Context Collector before PromptContext validation and rendering.
- Preserve the existing external PromptBuilderService request/result contract and rendered prompt behavior.
- Do not modify ConversationManager, WorkflowEngine, Vector-less RAG, frontend, APIs, database, or runtime chatbot behavior.
- Add focused unit tests covering no active workflow, booking workflow, cancellation workflow, partial workflows, completed workflows, deterministic normalization, metadata preservation, read-only behavior, and backward compatibility with existing Prompt Builder tests.
- Update architecture documentation, feature map, current task, important files, and session context to describe the Workflow Context Collector as an internal Prompt Builder component responsible only for deterministic workflow normalization.