Phase 4 – Vector-less RAG Retrieval Quality Improvement

The Vector-less RAG pipeline is working, but manual testing has revealed retrieval quality and routing issues.

Observed behavior:

1. Query:
   "Do you provide online consultation?"

Current Result:
- Knowledge Retrieval is invoked.
- An unrelated Booking FAQ is returned because it matches the keyword "provide".

Expected:
- Retrieve the Telemedicine / Online Consultation knowledge document.

2. Query:
   "What payment methods are accepted?"

Current Result:
- Routed to an unrelated deterministic doctor-search intent.
- Knowledge Retrieval is never invoked.

Expected:
- Query should reach the Knowledge Retrieval layer.
- Return the Payment Methods knowledge document if available.

Requirements:

- Do NOT redesign the architecture.
- Do NOT introduce embeddings, vector databases, or LLMs.
- Preserve the existing Phase 3 workflow routing.
- Preserve existing business APIs.
- Keep the implementation prototype-first.

Improve the Vector-less RAG by:

1. Enhance knowledge document metadata:
   - title
   - category
   - keywords
   - synonyms
   - aliases (optional)

2. Improve deterministic retrieval scoring by prioritizing:
   - title matches
   - keyword matches
   - synonym matches
   - category relevance
   - body-text matches

3. Improve ConversationManager routing:
   - Business workflows remain highest priority.
   - Business intents that require API execution continue unchanged.
   - General informational questions should reach Knowledge Retrieval before falling back to legacy deterministic responses.

4. Add or update knowledge documents for:
   - Telemedicine / Online Consultation
   - Payment Methods
   - Appointment Preparation
   - Consultation Hours
   - Insurance
   - Parking

5. Add regression tests covering:
   - "Do you provide online consultation?"
   - "What payment methods are accepted?"
   - "How do I prepare before my appointment?"
   - "What are your consultation hours?"
   - Existing booking, cancellation, and confirmation workflows remain unaffected.

Keep all changes additive, deterministic, and backward compatible.