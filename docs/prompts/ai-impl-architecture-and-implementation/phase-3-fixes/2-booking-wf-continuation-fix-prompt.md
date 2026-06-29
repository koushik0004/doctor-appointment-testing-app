Phase 3 Stabilization - Defect #3: Booking Workflow Continuation

Expected behavior:

Once the user starts the Booking Workflow, the Workflow Engine must retain ownership of the conversation until the booking is either completed, cancelled, times out, or the user explicitly switches workflows.

Current behavior:

After collecting some required booking fields, subsequent user messages (such as patient name or email) are treated as new standalone queries. The chatbot exits the active Booking Workflow and falls back to displaying the doctor details card, availability, and "Book Appointment" button instead of completing the booking.

Tasks:

1. Trace the Booking Workflow state from Conversation Manager through the Workflow Engine.
2. Verify that the active booking workflow is preserved across all conversation turns.
3. Ensure every new user message is first evaluated against the active booking workflow before intent reclassification.
4. Persist and merge collected booking fields (doctor, date, time, patient name, email, phone, appointment type, health description) into the workflow state.
5. Ask only for fields that are still missing.
6. As soon as all mandatory fields are available, automatically invoke the existing appointment creation service.
7. On successful booking, navigate to the appointment confirmation flow/page instead of returning the doctor details card or manual booking UI.
8. Do not require the user to click the "Book Appointment" button once sufficient information has already been collected through chat.
9. Preserve deterministic behavior and existing business APIs.
10. Do not modify unrelated workflows (Doctor Details, Availability, Cancellation, Confirmation) or redesign the architecture.

After implementation, provide:

* Root cause.
* Files modified.
* How workflow state is preserved.
* Manual verification scenarios covering incremental booking conversations and automatic booking completion.
