Phase 4 Final Stabilization – Booking Business Validation

Manual testing identified a business validation regression.

Current behavior:

When a booking request contains a past date, unavailable slot, or other expected business validation failure, the backend throws an exception and returns HTTP 503.

Example:

Book an appointment with Dr. Elena Rodriguez on 2nd July 2026 at 6:00 PM.

Expected behavior:

These are business validation scenarios and must not be treated as server failures.

Requirements:

- Preserve the existing architecture.
- Do not redesign ConversationManager.
- Do not redesign WorkflowEngine.
- Do not modify Vector-less RAG.

Update the booking execution flow so that expected validation failures return deterministic chatbot responses instead of HTTP 500/503.

Handle at least:

- Past appointment date
- Slot already booked
- Invalid doctor
- Invalid appointment time
- Invalid patient information
- Duplicate booking (if applicable)

Return structured business responses while keeping the booking workflow active whenever possible.

Only unexpected system exceptions should result in HTTP 500.

Add regression tests covering every validation scenario.

Keep all changes additive and backward compatible.