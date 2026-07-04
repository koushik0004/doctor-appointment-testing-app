Phase 5 – Step 5.7: Introduce a deterministic Prompt Assembly Pipeline beneath the inactive Prompt Builder.

Requirements:

- Add an internal PromptContextAssemblyPipeline responsible for assembling a validated PromptContext into an ordered sequence of renderable prompt sections.
- Introduce an intermediate PromptAssemblySection model (or equivalent) representing section label, content, metadata, and section kind.
- Move prompt-section ordering responsibility from PromptBuilderService into the Assembly Pipeline.
- Preserve deterministic ordering and omit empty sections automatically.
- Preserve the current rendered prompt output exactly, keeping backward compatibility.
- Keep rendering independent of section assembly.
- Keep the pipeline completely deterministic and read-only.
- Do not perform validation, workflow execution, knowledge retrieval, routing, AI reasoning, conversation mutation, API calls, database access, or LLM integration.
- Refactor PromptBuilderService to delegate section assembly to the PromptContextAssemblyPipeline before rendering.
- Preserve the existing PromptBuildRequest and PromptBuildResult contracts.
- Add focused unit tests covering deterministic ordering, omission of empty sections, repeated-build determinism, renderer compatibility, read-only behavior, and backward-compatible prompt output.
- Update the architecture documentation, feature map, important files, session context, and current task to document the Prompt Assembly Pipeline as the dedicated deterministic component responsible for assembling ordered prompt sections before rendering.