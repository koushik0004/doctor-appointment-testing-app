Task: Enhance AI Chat Widget for Advanced Search Responses.

Requirements:

1. Support filtered doctor results.

2. Display applied filters.

Example:

Cardiology
Female
Tomorrow

3. Render matching doctor cards.

4. Show result counts.

Example:

Found 3 matching doctors.

5. Preserve existing doctor card and booking flow.

6. Preserve existing chat history.

7. Do not introduce business logic into UI components.

8. Keep implementation inside lib/ai-widget.

Acceptance Criteria:

User:
"Need female cardiologist tomorrow"

Chat Widget:

* Displays extracted filters
* Displays matching doctors
* Allows booking directly

Deliverables:

* Filter display component
* Enhanced rendering
* Integration updates
* Testing summary
