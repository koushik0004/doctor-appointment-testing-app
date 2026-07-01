Phase 4.4 – Conversation Manager Integration

Integrate the Knowledge Retrieval Service.

Requirements:
- Preserve workflow-first routing.
- Preserve deterministic fallback.
- Query Knowledge Retrieval only when no workflow is active.
- Keep API contracts unchanged.
- No business logic changes.

Goal Flow Chart (Better understanding):
Conversation Manager

↓

Workflow?

↓

YES → Workflow Engine

↓

NO

↓

Knowledge Retrieval

↓

NO MATCH

↓

Existing Deterministic Chat