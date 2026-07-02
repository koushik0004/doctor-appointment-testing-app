Phase 4 Regression Fix – Booking Workflow Entity Extraction & Conversation Continuation

Manual testing identified regressions introduced after the Vector-less RAG integration.

Observed issues:

1. Single-message booking requests containing:
   - doctor name
   - appointment date
   - appointment time

are not fully parsed.

Example:

Book appointment as below

Dr. Elena Rodriguez
2nd July 2026
6:00 PM

The workflow starts but fails to extract all entities and incorrectly asks again for the appointment date.

2. Multi-turn booking continuation is inconsistent.

Example:

User:
02/07/2026

User:
Pandora Kaki

The workflow frequently repeats the previous assistant response instead of merging the newly supplied information into the active workflow.

Expected behavior:

1. Preserve the existing Phase 3 booking workflow.
2. Preserve workflow-first routing.
3. Improve deterministic entity extraction for:
   - doctor name
   - appointment date
   - appointment time
   - patient full name
   - patient email
4. Merge newly extracted entities into the existing workflow draft before validating missing fields.
5. Never ask again for fields that have already been successfully extracted.
6. Prevent duplicate assistant responses when workflow state has progressed.
7. Preserve backward compatibility.
8. Do not redesign WorkflowEngine.
9. Do not redesign ConversationManager.
10. Do not introduce LLMs, Prompt Builder logic, embeddings, or vector databases.

Regression tests to add/update:

Happy Path 1
- Complete booking request in a single message.

Happy Path 2
- Multi-turn booking with one field supplied per message.

Happy Path 3
- Partial booking request followed by incremental replies.

Regression verification:

- Booking
- Cancellation
- Confirmation lookup
- Doctor search
- Knowledge Retrieval
- Conversation continuity

Keep the implementation prototype-first, deterministic, and additive.