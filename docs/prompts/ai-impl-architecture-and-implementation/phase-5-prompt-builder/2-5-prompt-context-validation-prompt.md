Phase 5 – Step 5.2.5: Introduce PromptContext Validation.

Requirements:

- Add a dedicated PromptContext validation layer inside the Prompt Builder.
- Validate the canonical PromptContext after all collectors populate it and before prompt rendering begins.
- Keep validation deterministic and read-only.
- Validation should verify:
  - required PromptContext sections are structurally valid,
  - user_context contains a non-empty message,
  - constraint values are within supported limits,
  - rendering options are internally consistent,
  - knowledge documents do not contain duplicate document IDs,
  - included/excluded document metadata remains consistent,
  - workflow metadata is internally consistent.
- Return deterministic validation errors suitable for debugging, without changing production chat behavior.
- Do not introduce LLM integration, workflow execution, retrieval logic, routing changes, database access, frontend changes, or API changes.
- Preserve complete backward compatibility with the existing PromptBuilderService contract.
- Add focused unit tests covering valid PromptContext instances, validation failures, duplicate knowledge documents, invalid constraints, invalid rendering options, and backward compatibility.
- Update architecture documentation to describe PromptContext validation as the final deterministic gate before prompt rendering.