Goal:
Document the master architecture for the existing Doctor Appointment AI Assistant without modifying runtime behavior.

Scope:
- Create a high-level architecture document.
- Define all major layers (Frontend, Backend, AI Layer, Workflow Layer, Knowledge Layer, API Layer).
- Document responsibilities and boundaries for each layer.
- Produce a high-level request flow diagram.
- Document component interaction and dependency relationships.
- Record architectural decisions (ADR) explaining why the deterministic engine remains the primary execution layer.
- Document the migration strategy using incremental evolution and backward compatibility.
- Ensure no business logic, APIs, or existing modules are modified.

Out of Scope:
- No implementation code.
- No new APIs.
- No database changes.
- No prompt engineering.
- No workflow implementation.
- No LLM integration.

Acceptance Criteria:
- Architecture documentation is complete and internally consistent.
- Existing implementation remains unchanged.
- The document serves as the reference blueprint for all subsequent AI architecture phases.