TASK: Fix Appointment Search Result Card Information Hierarchy

Review the current appointment result card implementation.

The current card incorrectly emphasizes patient information.

Refactor the card to follow this hierarchy:

SECTION 1 (Primary)

Doctor Name
Doctor Specialty
Appointment Status

SECTION 2

Appointment ID
Appointment Date
Appointment Time
Appointment Type

SECTION 3

Patient Name
Patient Email
Patient Phone

Requirements:

- Doctor information must appear first
- Patient information must appear last
- Do not change API contracts
- Do not modify backend

Generate clean reusable component structure.

Do not change styling yet.