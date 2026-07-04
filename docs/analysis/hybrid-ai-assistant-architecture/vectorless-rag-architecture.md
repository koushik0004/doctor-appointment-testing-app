# Vector-less RAG Architecture

## Status

Prototype implementation in progress. Phase 4.2 added the passive knowledge repository; Phase 4.3 added deterministic top-document retrieval; Phase 4.4 wired the retrieval service into `ConversationManager` as a read-only fallback when no workflow is active. The module still does not change APIs, live prompt building, LLM calls, embeddings, or a vector database.

## Purpose

This document defines the prototype architecture for a Vector-less RAG module for the Doctor Appointment AI Assistant. The goal is to introduce a simple, trusted knowledge layer backed by Markdown and JSON files without adding embeddings, vector databases, or LLM dependencies.

The design preserves the current deterministic assistant architecture:

- `ConversationManager` still owns the orchestration entry point, but it now consults the knowledge retrieval service only when no workflow is active.
- `WorkflowEngine` remains unchanged.
- Existing doctor, availability, and appointment services remain the source of truth for live operational data.
- The deterministic chat engine remains the primary execution path and still handles the fallback when retrieval does not produce a knowledge-backed response.

## Scope

In scope:

- Define a prototype folder structure.
- Define supported knowledge source formats.
- Define the knowledge document schema.
- Define a loader interface contract.
- Define deterministic title/keyword retrieval over loaded documents.
- Define extension seams for a future Prompt Builder.
- Document boundaries and migration path.

Out of scope:

- Implementing semantic matching.
- Adding a vector database or embedding model.
- Modifying chat orchestration code.
- Modifying workflow execution code.
- Replacing existing database-backed doctor or appointment services.

## Architectural Position

The Vector-less RAG module is a future knowledge-support layer under the existing backend AI architecture. It should not own intent detection, workflow execution, appointment mutation, or frontend rendering.

```text
Frontend AI Widget
  ->
Chat API
  ->
ConversationManager
  ->
Deterministic Chat Service / WorkflowEngine
  ->
Future Knowledge Access Seam
  ->
Vector-less RAG Retrieval Service
  ->
Vector-less RAG Repository / Loader
  ->
Markdown and JSON knowledge sources
```

The implemented module now participates in chat orchestration as a read-only fallback. It can load, validate, cache, and deterministically select one top matching document, and `ConversationManager` uses that result only when no workflow is active before falling back to the deterministic chat engine.

The inactive Prompt Builder seam under `backend/app/services/prompt_builder.py` now includes deterministic internal collectors for conversation context, workflow context, and knowledge context before PromptContext validation and rendering. These collectors are provider-agnostic normalization components only; they do not perform retrieval, ranking, semantic search, workflow execution, routing, conversation mutation, API calls, or database access.

## Proposed Folder Structure

Runtime-facing module layout:

```text
backend/app/knowledge/
  __init__.py
  documents.py
  loader.py
  repository.py
  retrieval.py
  sources/
    README.md
    faq/
      booking.md
      cancellation.md
      fees.md
    policies/
      appointment-policy.md
      privacy-guidance.md
    structured/
      assistant-capabilities.json
      escalation-rules.json
```

Test layout:

```text
backend/tests/knowledge/
  test_documents.py
  test_loader.py
  fixtures/
    valid_faq.md
    valid_capability.json
    invalid_missing_metadata.md
```

Documentation layout:

```text
docs/analysis/hybrid-ai-assistant-architecture/
  vectorless-rag-architecture.md

docs/reports/feature-10/ai-impl-architecture-and-implementation/
  phase-04-report.md
```

Folder responsibilities:

- `documents.py`: typed document and metadata models.
- `loader.py`: file loading and validation interface.
- `repository.py`: in-memory repository abstraction for loaded documents.
- `retrieval.py`: deterministic title/keyword retrieval service that returns one top matching document.
- `sources/`: curated Markdown and JSON knowledge files committed to the repo.
- `sources/faq/`: user-facing support answers and procedural help.
- `sources/policies/`: product, safety, privacy, and appointment guidance.
- `sources/structured/`: machine-readable capability and routing reference data.

## Knowledge Source Strategy

The prototype should use repository-local files only.

Markdown files are best for authored guidance:

- booking help
- cancellation guidance
- fee explanation
- appointment policy language
- assistant capability descriptions
- safety or escalation notes

JSON files are best for structured reference data:

- canonical assistant capabilities
- supported intent-to-topic mappings
- escalation rules
- product limits
- prompt-builder control flags

Live operational facts should stay in existing services:

- doctor records remain in `doctor_service.py` and repository/database layers
- slot availability remains in `availability_service.py` and `schedule_service.py`
- appointments remain in `appointment_service.py` and repositories

The Vector-less RAG knowledge source should not duplicate live doctor, patient, appointment, or slot data.

## Knowledge Document Schema

Each knowledge document should normalize into a shared internal shape regardless of source format.

```python
KnowledgeDocument:
  id: str
  title: str
  source_type: Literal["markdown", "json"]
  source_path: str
  domain: Literal["faq", "policy", "capability", "workflow_guidance", "safety"]
  audience: Literal["patient", "assistant", "developer", "internal"]
  status: Literal["draft", "active", "deprecated"]
  version: str
  tags: list[str]
  priority: int
  summary: str
  content: str | dict
  prompt_hints: PromptHints | None
  metadata: dict[str, Any]
```

Prompt hints are optional and should remain non-executing metadata in this phase.

```python
PromptHints:
  include_when_intents: list[str]
  exclude_when_intents: list[str]
  safe_to_quote: bool
  requires_domain_validation: bool
  max_context_chars: int | None
```

Required fields:

- `id`
- `title`
- `source_type`
- `source_path`
- `domain`
- `audience`
- `status`
- `version`
- `summary`
- `content`

Recommended fields:

- `tags`
- `priority`
- `prompt_hints`
- `metadata`

## Markdown Source Format

Markdown files should use YAML front matter followed by authored content.

```markdown
---
id: faq.booking.general
title: Booking Appointment Help
domain: faq
audience: patient
status: active
version: "1.0"
tags:
  - booking
  - appointment
priority: 50
summary: Explains how patients can book appointments through the app.
prompt_hints:
  include_when_intents:
    - booking_help
  exclude_when_intents: []
  safe_to_quote: true
  requires_domain_validation: false
  max_context_chars: 1200
---

# Booking Appointment Help

Patients can choose a doctor, select an available date and time, provide contact details, and confirm the appointment.
```

Markdown loader responsibilities:

- parse front matter
- validate required metadata
- preserve body text as `content`
- derive `source_path`
- reject duplicate document IDs
- reject unsupported status/domain/audience values

## JSON Source Format

JSON files should use a top-level document object.

```json
{
  "id": "capabilities.assistant.v1",
  "title": "Assistant Capabilities",
  "source_type": "json",
  "domain": "capability",
  "audience": "assistant",
  "status": "active",
  "version": "1.0",
  "tags": ["assistant", "capabilities"],
  "priority": 40,
  "summary": "Defines current supported assistant capabilities.",
  "content": {
    "can_help_with": [
      "doctor discovery",
      "appointment availability",
      "booking guidance",
      "appointment confirmation lookup",
      "cancellation guidance"
    ],
    "cannot_help_with": [
      "medical diagnosis",
      "emergency triage",
      "insurance verification"
    ]
  },
  "prompt_hints": {
    "include_when_intents": ["help", "capability_question"],
    "exclude_when_intents": [],
    "safe_to_quote": false,
    "requires_domain_validation": false,
    "max_context_chars": 1000
  },
  "metadata": {}
}
```

JSON loader responsibilities:

- parse JSON safely
- validate the shared document schema
- preserve structured `content`
- derive `source_path`
- reject duplicate document IDs
- reject arrays as the top-level structure

## Loader Interface

The loader interface should be small and independent of chat orchestration.

```python
class KnowledgeLoader(Protocol):
    def load(self) -> list[KnowledgeDocument]:
        """Load all configured knowledge documents."""

    def load_path(self, path: Path) -> KnowledgeDocument:
        """Load and validate one Markdown or JSON knowledge document."""

    def validate(self, document: KnowledgeDocument) -> None:
        """Raise a validation error when a document violates the schema."""
```

Recommended concrete implementation:

```python
class FileSystemKnowledgeLoader:
    def __init__(self, root: Path) -> None:
        self.root = root

    def load(self) -> list[KnowledgeDocument]:
        ...

    def load_path(self, path: Path) -> KnowledgeDocument:
        ...

    def validate(self, document: KnowledgeDocument) -> None:
        ...
```

Loader constraints:

- deterministic output ordering by `priority`, then `id`
- no network access
- no database access
- no embeddings
- no vector index creation
- no calls into `ConversationManager`
- no calls into `WorkflowEngine`

## Repository Interface

The repository is an in-memory read model built from loaded documents.

```python
class KnowledgeRepository:
    def all(self) -> list[KnowledgeDocument]:
        ...

    def get(self, document_id: str) -> KnowledgeDocument | None:
        ...

    def by_domain(self, domain: str) -> list[KnowledgeDocument]:
        ...

    def by_tag(self, tag: str) -> list[KnowledgeDocument]:
        ...
```

The repository supports exact ID, domain, and tag filtering. It should not implement natural-language retrieval directly.

## Retrieval Service

The retrieval service sits on top of the repository. It performs deterministic token matching only:

- title matches are weighted higher than summary/content/tag keyword matches
- common suffix normalization is allowed for simple variants such as plural `s` and `ing`
- repository priority and document id are deterministic tie-breakers
- the service returns at most one top document
- no LLM, embeddings, vector index, external search, prompt building, or chat orchestration calls are allowed

## Future Prompt Builder Seam

The Prompt Builder should be a later layer that receives already-selected knowledge documents and formats them into bounded context for a future LLM or deterministic response composer.

Phase 5.1 now provides an inactive standalone backend implementation of this seam as a deterministic service module. It remains outside the production request flow and only formats caller-provided context.
Phase 5.2 adds a canonical internal `PromptContext` model beneath that service. Phase 5.2.5 adds a dedicated deterministic validation gate over that model. Phase 5.3 adds an internal Conversation Context Collector, so the Prompt Builder now deterministically normalizes caller-supplied conversation state into structured conversation context, assembles metadata, user, workflow, knowledge, instruction, constraint, and rendering sections, validates the full `PromptContext`, and only then renders bounded prompt text.

Planned contract:

```python
class PromptContextBuilder(Protocol):
    def build(
        self,
        *,
        user_message: str,
        conversation_state: dict[str, Any],
        documents: list[KnowledgeDocument],
    ) -> PromptContext:
        ...
```

Important boundary:

- The Prompt Builder should not load files directly.
- The Prompt Builder should not mutate workflow state.
- The Prompt Builder should not bypass appointment or doctor services for live data.
- The Prompt Builder should treat `prompt_hints` as constraints, not as executable instructions.
- `PromptContext` is the canonical internal representation for prompt construction, but it remains provider-agnostic and is not an LLM API payload by itself.
- The internal Conversation Context Collector is responsible only for deterministic and read-only conversation normalization; it must not do routing, summarization, extraction, or workflow work.
- PromptContext validation is the final deterministic and read-only gate before prompt rendering begins.

## Future Integration Path

Phase 4.1, this document:

- architecture only
- no code changes
- no retrieval behavior

Phase 4.2, knowledge repository prototype:

- add document models
- add file-system loader
- add validation tests
- add sample Markdown and JSON knowledge files
- keep loader unused by chat runtime unless explicitly wired in a later phase

Phase 4.3, retrieval strategy:

- define exact-match and metadata-filtered retrieval
- keep vector-less behavior
- add deterministic tests
- avoid semantic or embedding dependency

Phase 4.4, controlled chat integration:

- introduce a read-only knowledge adapter behind the deterministic assistant
- preserve `ConversationManager` and `WorkflowEngine` contracts unless a separate migration prompt explicitly changes them

Phase 4.5, prompt/context builder:

- format selected knowledge into bounded context
- apply prompt hints
- add token/character budgeting
- keep domain validation in existing backend services

## Safety And Data Boundaries

The Vector-less RAG module must not become a second source of truth for mutable healthcare or appointment data.

Allowed content:

- general booking instructions
- app capability descriptions
- cancellation policy text
- non-diagnostic support guidance
- escalation instructions
- developer-authored assistant behavior notes

Disallowed content:

- patient records
- booked appointments
- dynamic doctor availability
- diagnosis or treatment advice
- secrets, API keys, or credentials
- generated content without review

## Validation Rules

The future loader should reject a document when:

- required metadata is missing
- `id` is duplicated
- `domain`, `audience`, or `status` is unsupported
- Markdown front matter is invalid
- JSON source is not an object
- document content is empty
- `prompt_hints.max_context_chars` is negative
- `priority` is not an integer

The future loader should warn, but not necessarily fail, when:

- a document has no tags
- a document is marked `draft`
- `summary` is longer than the configured limit
- content exceeds a configured size threshold

## Testing Strategy For Future Implementation

Unit tests should cover:

- valid Markdown document loading
- valid JSON document loading
- required metadata validation
- duplicate ID detection
- deterministic ordering
- unsupported extension handling
- registry filtering by exact ID, domain, and tag

No integration tests against chat routes are required for this architecture-only phase.

## Acceptance Criteria

This architecture is ready for the next phase when:

- the module has a clear folder structure
- Markdown and JSON source responsibilities are defined
- the normalized document schema is defined
- the loader interface is defined
- the registry boundary is defined
- future Prompt Builder integration is documented
- non-goals explicitly prevent retrieval logic and orchestration changes in this phase
