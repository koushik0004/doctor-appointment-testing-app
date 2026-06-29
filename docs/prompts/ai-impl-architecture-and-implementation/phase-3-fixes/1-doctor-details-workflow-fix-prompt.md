Phase 3 Stabilization - Defect #1: Doctor Details Workflow

Expected behavior:

When the user asks queries such as:

* Tell me about Dr. Sofia
* Tell me about Dr Sofia
* Who is Dr. Sofia?
* Show doctor details for Dr. Sofia
* Doctor profile of Dr. Sofia

the Conversation Manager should deterministically route the request to the existing Doctor Details workflow, extract the doctor name correctly, invoke the existing doctor details/business service, and return the doctor's information.

Current behavior:

The chatbot falls back to the generic response:

"I can help with available doctors, specializations, consultation fees, and appointment slots."

Tasks:

1. Trace the request flow from Conversation Manager to the Doctor Details handler.
2. Verify whether the intent detection recognizes doctor detail/profile queries.
3. Verify doctor name extraction, including names prefixed with "Dr.".
4. Verify routing priority so Doctor Details requests do not fall through to the generic FAQ/fallback handler.
5. Reuse the existing Doctor Details/business service if it already exists.
6. Make the smallest localized code change required.
7. Preserve deterministic behavior.
8. Do not redesign the architecture.
9. Do not modify Booking, Cancellation, Confirmation, Availability, or unrelated workflows.
10. Do not modify existing business APIs or database models.

After implementing:

* Describe the root cause.
* List the files changed.
* Explain why the fix is backward compatible.
* Suggest manual test cases for this defect only.