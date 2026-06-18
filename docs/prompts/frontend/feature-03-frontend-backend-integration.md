# Phase 1 - API Contract Analysis

Objective

Understand frontend/backend integration requirements.

Tasks

1. Analyze frontend booking flow.
2. Analyze backend booking APIs.
3. Analyze doctor APIs.
4. Analyze availability APIs.
5. Identify response mismatches.
6. Identify request mismatches.

Deliverable

feature-03-api-gap-analysis.md

Restrictions

No code changes.

Review

Verify all integration gaps documented.

Agent Prompt

Analyze frontend and backend contracts.

Generate:

feature-03-api-gap-analysis.md

Do not modify code.

Perform review before completion.

---

# Phase 2 - Doctor Selection Integration

Objective

Replace static doctor data.

Tasks

1. Identify hardcoded doctor objects.
2. Connect doctor APIs.
3. Add loading state.
4. Add error state.
5. Verify rendering.

Acceptance Criteria

Doctor information comes from backend.

Review

Verify no mock doctor data remains.

Agent Prompt

Integrate doctor APIs.

Replace static doctor information.

Add loading and error handling.

Review all rendering paths.

---

# Phase 3 - Availability Integration

Objective

Connect calendar and slots.

Tasks

1. Load available dates.
2. Load available slots.
3. Disable unavailable dates.
4. Separate morning slots.
5. Separate afternoon slots.

Acceptance Criteria

Calendar data comes from backend.

Review

Verify doctor selection still works.

Agent Prompt

Integrate availability APIs.

Implement:

- date loading
- slot loading
- loading states
- error states

Review calendar behavior.

---

# Phase 4 - Booking Store Integration

Objective

Persist booking selections.

Tasks

1. Store doctor.
2. Store date.
3. Store time.
4. Store appointment type.

Acceptance Criteria

Selections survive navigation.

Review

Verify Zustand state consistency.

Agent Prompt

Integrate booking state.

Persist all booking selections.

Review state transitions.

---

# Phase 5 - Form Integration

Objective

Connect patient details form.

Tasks

1. Map form fields.
2. Connect validation.
3. Match backend schema.

Acceptance Criteria

Payload matches backend requirements.

Review

Verify all validations.

Agent Prompt

Integrate booking form.

Align validation with backend.

Review field mapping.

---

# Phase 6 - Appointment Creation

Objective

Create appointments.

Tasks

1. Connect POST API.
2. Implement mutation.
3. Add loading state.
4. Add success state.
5. Add error state.
6. Prevent duplicate submissions.

Acceptance Criteria

Appointment created successfully.

Review

Verify payload and response.

Agent Prompt

Integrate appointment creation.

Implement:

- API mutation
- loading state
- success state
- error state

Prevent duplicate submissions.

---

# Phase 7 - Confirmation Integration

Objective

Use backend confirmation response.

Tasks

1. Remove placeholder data.
2. Use backend response.
3. Map appointment information.

Acceptance Criteria

Confirmation page displays backend data.

Review

Verify response mapping.

Agent Prompt

Integrate confirmation page.

Use backend response.

Review all displayed values.

---

# Phase 8 - Error Handling

Objective

Handle integration failures.

Tasks

1. Validation errors.
2. Network failures.
3. Backend failures.
4. Slot unavailable errors.

Acceptance Criteria

User receives meaningful feedback.

Review

Verify all error paths.

Agent Prompt

Implement error handling.

Review all failure scenarios.

---

# Phase 9 - Final Review

Objective

Validate complete flow.

Checklist

Doctor Selection

Availability

Date Selection

Time Selection

Patient Details

Appointment Creation

Confirmation

Validation

Loading States

Error States

Review

Generate:

feature-03-integration-review-report.md

Agent Prompt

Review complete integration.

Do not implement new features.

Generate review report.

---

<!-- 
command to run backend feature orchestrator
Run .ai/feature-backend-frontend-integration.md

FEATURE_FILE=docs/prompts/frontend/feature-03-frontend-backend-integration.md
-->