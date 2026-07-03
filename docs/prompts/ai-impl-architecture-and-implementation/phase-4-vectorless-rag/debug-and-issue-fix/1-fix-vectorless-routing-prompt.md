Phase 4 Debug 01 – Fix Vector-less RAG Routing

The Phase 4 implementation is complete, but manual testing shows that knowledge questions are still being answered by the legacy deterministic chatbot instead of the Vector-less RAG.

Observed examples:
- "What are your consultation hours?"
- "What is telemedicine?"
- "How do I prepare before my appointment?"

Current behavior:
- Appointment Help is returned.
- UNKNOWN intent falls back immediately.
- knowledge_source is always null.
- Existing deterministic response is returned.

Expected behavior:
ConversationManager should process requests in this order:

1. Active Workflow?
   → Workflow Engine

2. No active workflow?
   → Knowledge Retrieval Service

3. Knowledge found?
   → Return knowledge response with populated knowledge_source metadata.

4. No knowledge found?
   → Fall back to the existing deterministic chatbot.

Requirements:
- Do NOT redesign the architecture.
- Do NOT modify Workflow Engine behavior.
- Do NOT change business APIs.
- Preserve all Phase 3 functionality.
- Verify that the Knowledge Repository loads successfully.
- Verify that the Knowledge Retrieval Service is actually invoked.
- Verify that retrieval returns matches for existing knowledge documents.
- Ensure knowledge_source is populated whenever a knowledge answer is returned.
- Keep all changes backward compatible.
- Add or update backend tests covering:
  - successful knowledge retrieval
  - fallback when no knowledge exists
  - workflow-first routing
  - knowledge-before-deterministic routing
- Do not modify the frontend unless required by an API contract bug.