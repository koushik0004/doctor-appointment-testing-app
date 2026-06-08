# Feature 3 Backend Analysis

## Scope

Phase 1 of `docs/prompts/backend/feature-3-backend-orchestration-plan.md` is a read-only backend review. No code changes were required for this phase.

## Current Backend Structure

The backend is still a small FastAPI app centered on doctor listing and health checks.

### Application Bootstrap

- [backend/app/main.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/main.py)
- [backend/app/api/router.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/api/router.py)

### API Layer

- [backend/app/api/health.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/api/health.py)
- [backend/app/api/doctors.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/api/doctors.py)

### Core / Config

- [backend/app/core/config.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/core/config.py)
- [backend/app/core/errors.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/core/errors.py)

### Database Layer

- [backend/app/db/base.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/db/base.py)
- [backend/app/db/database.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/db/database.py)
- [backend/app/db/seed.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/db/seed.py)

### Doctor Domain

- [backend/app/models/doctor.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/models/doctor.py)
- [backend/app/repositories/doctor_repository.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/repositories/doctor_repository.py)
- [backend/app/schemas/doctor.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/schemas/doctor.py)
- [backend/app/services/doctor_service.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/services/doctor_service.py)

### Tests

- [backend/tests/test_doctors_api.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/tests/test_doctors_api.py)

## What Exists Already

- FastAPI app creation with lifespan startup in `main.py`.
- Router assembly in `api/router.py`.
- `/api/health` and `/api/doctors` routes.
- SQLAlchemy session management and SQLite engine setup.
- Idempotent doctor seeding at startup.
- Repository/service separation for doctor reads.
- Startup repair for stale seeded `doctors` schemas.

## Reusable Components For Feature 3

- `get_db()` in [backend/app/db/database.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/db/database.py) for dependency-injected sessions.
- `Base` in [backend/app/db/base.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/db/base.py) for new ORM models.
- `Settings` in [backend/app/core/config.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/core/config.py) for database and API prefix configuration.
- `doctor_not_found()` in [backend/app/core/errors.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/core/errors.py) as the current pattern for domain-specific HTTP errors.
- `AppointmentType` in [backend/app/schemas/doctor.py](/Users/koushiksadhukhan/projects/doctor-appointment-testing-app/backend/app/schemas/doctor.py) for appointment type validation reuse.
- The repository/service split in the doctor domain as the pattern to mirror for booking work.

## Missing Feature 3 Backend Pieces

The current backend does not yet contain:

- availability model
- patient model
- appointment model
- availability repository/service
- appointment repository/service
- appointment validation schemas
- availability API
- appointment creation API
- confirmation response DTOs

## Dependencies And Coupling

- `backend/app/main.py` currently calls `init_db()` during startup, so any new appointment-related tables or seeds will need to be included in the same startup path.
- `backend/app/db/base.py` only exposes the declarative base. New ORM models must be imported through the package import path used by `init_db()`.
- `backend/app/db/database.py` currently handles seeded-table schema drift only for `doctors`. If appointment tables are added, the startup logic may need to account for them separately.
- `backend/app/api/router.py` only registers health and doctors routers. Booking routes will need explicit registration there.
- `backend/app/tests/test_doctors_api.py` currently covers only doctor listing and startup repair behavior, so Feature 3 will need a new test file or a broadened backend test suite.

## Implementation Risks

- The backend currently has no appointment persistence layer, so booking work will require new tables and careful startup registration.
- `database.py` uses `create_all()` instead of migrations. That is fine for the current doctor-only app, but appointment expansion will make schema drift more likely.
- The existing doctor schema is doctor-listing oriented and does not yet expose availability slots, which means the booking flow will need new read models rather than just extending current list responses.
- The current repo has no appointment-specific error helpers yet, so the new flow needs clear validation and conflict handling for booked slots and invalid doctor IDs.
- The feature plan mentions migrations, but the repo currently has no Alembic setup in the live backend tree, so that gap should be acknowledged before implementation work starts.

## Review Notes

- The backend architecture is clean enough to extend without rewriting the doctor flow.
- The current service/repository structure is the right place to add booking logic next.
- No code was changed for this phase.
