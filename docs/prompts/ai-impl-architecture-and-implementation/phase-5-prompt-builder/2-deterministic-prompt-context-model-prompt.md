Phase 5 – Step 5.2: Introduce a deterministic Prompt Context Model beneath the existing Prompt Builder.

Requirements:
- Define a structured internal PromptContext model as the canonical contract for prompt construction.
- Organize the model into logical sections including Metadata, User Context, Conversation Context, Workflow Context, Knowledge Context, System Instructions, Constraints, and Rendering Options.
- Keep the PromptContext independent of any LLM provider, prompt template, or rendering format.
- Refactor the existing PromptBuilderService to construct and validate a PromptContext before producing prompt text, while preserving its current external behavior and deterministic output.
- Do not introduce any LLM integration, retrieval logic, workflow execution, routing changes, database access, or API/UI changes.
- Add focused unit tests covering PromptContext creation, optional section handling, deterministic defaults, and backward compatibility with the existing PromptBuilderService.
- Update the architecture documentation to describe PromptContext as the canonical internal representation used by the Prompt Builder.