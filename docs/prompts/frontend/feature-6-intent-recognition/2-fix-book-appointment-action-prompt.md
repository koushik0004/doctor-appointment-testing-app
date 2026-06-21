Task: Fix Chat Widget "Book Appointment" Action End-to-End.

Problem:

Doctor cards are rendering correctly inside the AI Chat Widget.

The "Book Appointment" button is visible but clicking it does nothing.

Expected Behavior:

When a user clicks "Book Appointment" from a doctor card inside the chat widget:

1. Navigation must occur.
2. User must land on the correct appointment booking page.
3. The selected doctor must be pre-selected if supported by the application.
4. Existing booking flow must continue normally.

Requirements:

1. Trace the complete flow:

Chat Widget
→ Doctor Card
→ Book Appointment Button
→ Click Handler
→ Navigation
→ Appointment Page

2. Verify:

* Button click event is attached.
* Event is firing.
* Correct doctor data is available.
* Correct route is being generated.
* Navigation is executed successfully.

3. Reuse existing application routing.

Do NOT create a new booking page.

Use the existing appointment booking flow already implemented in the application.

4. Determine the correct target route from the current application.

Examples:

/appointments/book
/appointments/new
/doctors/[doctorId]
/book-appointment

Use whatever already exists in the codebase.

5. Pass doctor information during navigation.

Preferred:

doctorId

Example:

{
doctorId: "123"
}

6. If the booking page supports query parameters:

Navigate using:

?doctorId=<id>

Otherwise use the application's existing navigation pattern.

7. Verify the selected doctor appears correctly on the booking page.

8. Add graceful fallback:

If doctorId is missing:

* Disable booking action.
  OR
* Show meaningful error message.

9. Test the following scenarios:

* Doctor card from cardiologist search
* Doctor card from availability search
* Doctor card from doctor details search

10. Do not modify unrelated chat functionality.

Acceptance Criteria:

✓ Clicking Book Appointment always triggers navigation.

✓ User lands on the correct appointment booking page.

✓ Selected doctor is available on the booking page.

✓ Existing appointment creation flow continues working.

✓ No console errors.

Deliverables:

* Root cause analysis
* Files modified
* Navigation flow implemented
* Testing summary
* Final verification results
