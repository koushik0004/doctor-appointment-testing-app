# Feature 3 Schema Gap Analysis

## Scope

Phase 2 of `docs/prompts/backend/feature-3-backend-orchestration-plan.md` compares the live backend schema against the appointment booking requirements. No code changes are required for this phase.

## Current Database Shape

The live backend database currently contains only the `doctors` table.

### Existing Table

- `doctors`

### Existing ORM Model

- [backend/app/models/doctor.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/models/doctor.py)

### Existing Startup Behavior

- [backend/app/db/database.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/db/database.py)
- `init_db()` creates metadata tables at startup and reseeds doctors.

## Feature 3 Required Tables

### 1. Doctor

Required fields for the booking flow:

- `id`
- `name`
- `specialty`
- `rating`
- `location`

Current status:

- Present
- The live model already includes these fields and several extra doctor-listing fields.

### 2. Availability

Required fields:

- `doctor_id`
- `date`
- `start_time`
- `end_time`
- `status`

Current status:

- Missing
- No ORM model, repository, schema, or seed data exists yet for availability slots.

### 3. Patient

Required fields:

- `full_name`
- `email`
- `phone`

Current status:

- Missing
- No patient table or persistence layer exists yet.

### 4. Appointment

Required fields:

- `doctor_id`
- `patient_id`
- `appointment_date`
- `appointment_time`
- `appointment_type`
- `health_description`
- `status`

Current status:

- Missing
- No appointment table or persistence layer exists yet.

## Schema Gap Summary

### Already Covered By Existing Code

- Doctor identity and display fields needed for doctor selection.
- SQLite-backed ORM and session wiring.
- Startup table creation path through SQLAlchemy metadata.

### Missing For Feature 3

- appointment slot table
- patient table
- appointment table
- foreign key relationships for booking
- slot booking status tracking
- appointment status lifecycle values
- confirmation data storage

## Migration Requirements

The repository currently has no Alembic or migration workflow in the live backend tree.

That means Feature 3 will need one of these approaches:

1. Continue with `create_all()`-style startup table creation for the new tables.
2. Add an Alembic migration layer before writing booking persistence changes.

## Risks

- Adding booking tables without a migration strategy will increase schema drift risk over time.
- Startup seeding currently only knows how to rebuild seeded doctor data, not future booking tables.
- Appointment creation depends on a stable availability model, but that model does not exist yet.

## Review Notes

- The doctor schema is sufficient for the current listing flow and can be reused for booking reads.
- The booking flow requires three new persistence entities before any API or service work is safe.
- No code was changed for this phase.
