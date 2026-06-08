# Feature 3 (F006/F011) – Appointment Booking Backend Development Master Plan

## Objective

Implement the backend for Appointment Booking while preserving all existing functionality.

Frontend pages already exist as static implementations:

1. Doctor Search & Booking Page
2. Appointment Date/Time Selection Page
3. Appointment Confirmation Flow

The backend implementation must progressively connect these screens to real APIs without breaking existing features.

---

# Critical Rules

## Must Not Break

- Authentication flow
- Existing doctor listing functionality
- Existing search functionality
- Existing API contracts
- Existing database entities
- Existing frontend routing
- Existing completed features

## Required Approach

- Small incremental backend tasks
- One implementation objective per execution step
- Review after every implementation step
- No large refactoring
- No unrelated code modifications

---

# Functional Flow

## Step 1

User opens doctor listing page.

Backend returns:

- Doctor information
- Specialty
- Rating
- Location
- Earliest availability
- Telemedicine support

---

## Step 2

User selects a doctor.

Backend returns:

- Doctor profile summary
- Available booking dates

---

## Step 3

User selects date.

Backend returns:

- Available morning slots
- Available afternoon slots

---

## Step 4

User selects time slot.

Backend validates:

- Slot exists
- Slot still available
- Slot belongs to selected doctor

---

## Step 5

User enters patient information.

Backend validates:

- appointment_type
- full_name
- email
- phone
- health_description

---

## Step 6

Appointment is created.

Backend:

- Creates patient record if needed
- Creates appointment
- Marks slot booked
- Returns appointment confirmation

---

# Backend Development Breakdown

---

# Phase 1 – Domain Review Only

## Purpose

Understand current implementation.

## Deliverables

Identify:

- Doctor module
- Doctor entity
- Availability entity
- Appointment entity
- Patient entity
- Existing API structure
- Validation strategy
- Repository pattern usage
- Service layer pattern

## No Code Changes

Allowed:
- Read
- Analyze
- Document

Not Allowed:
- Modify code

---

# Agent Prompt – Phase 1

You are implementing Feature 3 Appointment Booking.

PLANNING MODE ONLY.

Tasks:

1. Analyze complete backend structure.
2. Locate doctor-related modules.
3. Locate appointment-related modules.
4. Identify database entities.
5. Identify repositories.
6. Identify services.
7. Identify controllers/routes.
8. Document findings.

Create:

feature-3-backend-analysis.md

Include:

- file paths
- dependencies
- reusable components
- implementation risks

Do not modify any code.

Perform a review before finishing.

---

# Phase 2 – Data Model Gap Analysis

## Purpose

Identify missing booking structures.

## Verify

### Doctor

Required:

- id
- name
- specialty
- rating
- location

### Availability

Required:

- doctor_id
- date
- start_time
- end_time
- status

### Patient

Required:

- full_name
- email
- phone

### Appointment

Required:

- doctor_id
- patient_id
- appointment_date
- appointment_time
- appointment_type
- health_description
- status

---

# Agent Prompt – Phase 2

Review current database design.

Tasks:

1. Compare existing schema with Feature 3 requirements.
2. Identify missing columns.
3. Identify missing tables.
4. Identify migration requirements.

Create:

feature-3-schema-gap-analysis.md

Do not generate migrations yet.

Do not modify code.

Perform self-review.

---

# Phase 3 – Appointment Database Foundation

## Purpose

Create backend persistence layer.

## Deliverables

If missing:

- Appointment entity/model
- Appointment repository
- Appointment migration

Status values:

- PENDING
- CONFIRMED
- CANCELLED

Constraints:

- foreign keys
- indexes
- timestamps

---

# Agent Prompt – Phase 3

Implement only database foundation.

Tasks:

1. Create appointment entity/model if missing.
2. Create repository.
3. Create migration.
4. Add indexes.
5. Add foreign key constraints.

Do not implement APIs.

Do not implement business logic.

Run project validation.

Review all changes.

Confirm no existing entity was broken.

---

# Phase 4 – Availability Management Layer

## Purpose

Support calendar and slot selection.

## UI Mapping

Image: Appointment Booking Screen

Calendar requires:

- available dates

Time sections require:

- morning slots
- afternoon slots

---

## Deliverables

Availability Service

Methods:

- getDoctorAvailability()
- getAvailableDates()
- getAvailableSlots()
- markSlotBooked()

---

# Agent Prompt – Phase 4

Implement availability layer only.

Tasks:

1. Build service methods.
2. Return available dates.
3. Return available slots.
4. Exclude booked slots.
5. Add unit validation.

Do not create booking API yet.

Review code.

Verify no doctor APIs were impacted.

---

# Phase 5 – Appointment Validation Layer

## Validation Rules

appointment_type

- required

full_name

- required
- minimum 2 chars

email

- required
- valid email

phone

- optional

health_description

- max 500 chars

selected_date

- required

selected_time

- required

doctor_id

- required

---

# Agent Prompt – Phase 5

Implement validation layer only.

Tasks:

1. Create DTO/request schema.
2. Add validation rules.
3. Add reusable validators.
4. Add error responses.

Do not create endpoint.

Review validation coverage.

Verify backward compatibility.

---

# Phase 6 – Doctor Availability APIs

## Purpose

Support FE dynamic calendar.

## APIs

GET /api/doctors/{doctorId}/availability

Response:

- doctor summary
- available dates
- available slots

---

# Agent Prompt – Phase 6

Implement availability API.

Tasks:

1. Create endpoint.
2. Connect service.
3. Return standardized response.
4. Add error handling.

Do not create booking API.

Run tests.

Review endpoint contract.

Verify existing doctor endpoints unchanged.

---

# Phase 7 – Appointment Creation Service

## Purpose

Core booking business logic.

## Workflow

Validate:

1. Doctor exists.
2. Slot exists.
3. Slot available.

Then:

4. Create patient.
5. Create appointment.
6. Mark slot booked.

Transaction required.

Rollback on failure.

---

# Agent Prompt – Phase 7

Implement appointment creation service only.

Tasks:

1. Build transactional workflow.
2. Validate slot ownership.
3. Validate slot availability.
4. Create patient.
5. Create appointment.
6. Mark slot booked.

No endpoint yet.

Review transaction safety.

Review concurrency risks.

---

# Phase 8 – Appointment Booking API

## API

POST /api/appointments

Request:

- doctor_id
- appointment_date
- appointment_time
- appointment_type
- full_name
- email
- phone
- health_description

Response:

- appointment_id
- booking_reference
- status

---

# Agent Prompt – Phase 8

Implement booking endpoint.

Tasks:

1. Create controller/route.
2. Connect validation.
3. Connect service.
4. Return API response.
5. Handle failures.

Review:

- validation
- error handling
- transaction safety

Verify no existing API contract changed.

---

# Phase 9 – Confirmation Response Support

## Purpose

Support booking confirmation page.

## Response Data

- appointment id
- doctor summary
- date
- time
- patient name
- status

---

# Agent Prompt – Phase 9

Extend appointment response.

Tasks:

1. Create confirmation DTO.
2. Add response mapper.
3. Return confirmation payload.

Review response structure.

Verify frontend compatibility.

---

# Phase 10 – Integration Review

## Purpose

Final backend verification.

Checklist

### Database

- migrations valid
- constraints valid
- indexes valid

### APIs

- availability API works
- booking API works

### Booking

- slot booking works
- duplicate booking blocked

### Validation

- invalid requests blocked

### Safety

- existing features unaffected

---

# Agent Prompt – Phase 10

REVIEW MODE.

Tasks:

1. Review every Feature 3 change.
2. Review migrations.
3. Review APIs.
4. Review services.
5. Review validation.
6. Review transactions.
7. Review database indexes.
8. Review backward compatibility.

Create:

feature-3-backend-review-report.md

Include:

- findings
- risks
- defects
- recommendations

Do not add new features.

Only review.

---

# Orchestration Execution Order

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
6. Phase 6
7. Phase 7
8. Phase 8
9. Phase 9
10. Phase 10

Never execute multiple phases together.

Complete and review one phase before moving to the next.

This sequencing minimizes regression risk and works well with multi-agent orchestration systems such as Codex CLI, Claude Code, or planner/executor workflows.
