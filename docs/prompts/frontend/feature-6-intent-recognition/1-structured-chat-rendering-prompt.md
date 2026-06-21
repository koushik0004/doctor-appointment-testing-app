Task: Enhance the AI Chat Widget to render structured doctor and appointment responses.

Context:

Frontend Stack:

* NextJS
* TypeScript
* TailwindCSS

Current State:

* Floating chat widget exists.
* Backend integration exists.
* Text messages render correctly.

Objective:

Support rich rendering of doctor-related responses returned from backend.

Requirements:

1. Preserve all existing functionality.

2. Add support for response types:

* text
* doctor_list
* availability
* appointment_help

3. For doctor_list responses render Doctor Cards.

Doctor Card Fields:

* Doctor Name
* Specialization
* Consultation Fee
* Next Available Slot

4. Add CTA button:

"Book Appointment"

5. For availability responses render:

* Doctor Name
* Available Date
* Available Time

6. Maintain chat history.

7. Maintain loading state.

8. Maintain error handling.

9. Keep implementation isolated inside:

lib/ai-widget

10. Do not place doctor-specific business logic inside widget components.

11. Widget must remain reusable and future-extractable.

12. Follow existing project styling and UI patterns.

Acceptance Criteria:

* User asks: "Show cardiologists"

* Backend returns structured response

* Chat widget renders doctor cards

* User asks: "Who is available tomorrow?"

* Chat widget renders availability cards

* Existing text responses continue working

Deliverables:

* Updated widget types
* Structured response renderer
* Doctor card component
* Availability component
* Integration updates
* Implementation summary
