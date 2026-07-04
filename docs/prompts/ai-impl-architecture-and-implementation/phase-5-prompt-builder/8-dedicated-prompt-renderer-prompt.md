Phase 5 – Step 5.8: Introduce a dedicated Prompt Renderer for the inactive Prompt Builder.

Background

The Prompt Builder currently contains the following internal pipeline:

Conversation Context Collector
↓

Workflow Context Collector
↓

Knowledge Context Collector
↓

System Instruction Builder
↓

PromptContext
↓

PromptContext Validation
↓

Prompt Assembly Pipeline
↓

PromptBuilderService rendering logic

The final rendering logic still lives inside PromptBuilderService.

This step completes the Prompt Builder pipeline by extracting rendering into its own deterministic component.

Requirements

Create an internal PromptRenderer component beneath the Prompt Assembly Pipeline.

Responsibilities

The PromptRenderer must be responsible only for:

- rendering ordered PromptAssemblySection objects
- applying section headers
- respecting rendering options
- joining rendered sections
- applying total prompt truncation
- respecting truncation markers
- returning the final prompt string and truncation status

Move all rendering-related logic from PromptBuilderService into PromptRenderer, including:

- section rendering
- section-header handling
- prompt concatenation
- truncation handling
- rendering option application

PromptBuilderService should become only an orchestrator:

Build Context
↓

Validate Context
↓

Assemble Sections
↓

PromptRenderer.render(...)
↓

PromptBuildResult

The renderer must NOT:

- validate PromptContext
- assemble prompt sections
- retrieve knowledge
- execute workflows
- inspect ConversationManager
- mutate PromptContext
- call APIs
- access databases
- perform AI reasoning
- integrate with any LLM provider

Architecture Constraints

- Preserve complete backward compatibility.
- Preserve PromptBuildRequest.
- Preserve PromptBuildResult.
- Preserve PromptContext.
- Preserve PromptAssemblySection.
- Preserve rendered prompt output exactly.
- Keep PromptRenderer deterministic.
- Keep PromptRenderer provider-agnostic.
- Keep PromptBuilder inactive in production.
- Do not modify ConversationManager.
- Do not modify WorkflowEngine.
- Do not modify Vector-less RAG.
- Do not modify frontend.
- Do not modify backend APIs.
- Do not modify database schema.
- Do not introduce LLM integration.

Testing Requirements

Add focused unit tests covering:

- deterministic rendering
- rendering with section headers enabled
- rendering with section headers disabled
- empty assembled section list
- prompt truncation
- truncation marker handling
- repeated rendering determinism
- read-only behavior
- backward-compatible rendered prompt output
- PromptBuilderService integration with PromptRenderer

Documentation

Update:

- vectorless-rag-architecture.md
- current-task.md
- feature-map.md
- important-files.md
- session-context.md

to describe PromptRenderer as the final deterministic stage of the inactive Prompt Builder pipeline.

Acceptance Criteria

At the end of this step the internal Prompt Builder pipeline must be:

Conversation Context Collector
↓

Workflow Context Collector
↓

Knowledge Context Collector
↓

System Instruction Builder
↓

PromptContext
↓

Validation
↓

Prompt Assembly Pipeline
↓

PromptRenderer
↓

PromptBuildResult

PromptBuilderService must act only as an orchestrator and no longer contain prompt rendering logic.

No runtime chatbot behavior must change.