# Feature 3 Backend Review Report

## Scope

Review of the Feature 3 backend work for appointment booking: schema foundation, availability service, validation, appointment creation, and confirmation response support.

## Findings

### 1. No blocking product defects found

- The appointment foundation tables exist.
- The availability service returns doctor availability data.
- The appointment creation flow validates input, creates/reuses a patient, books a slot, and returns a confirmation payload.
- The confirmation endpoint returns the expected appointment summary.
- The backend test slices pass when run in isolation:
  - `backend/tests/test_appointments_api.py`
  - `backend/tests/test_availability_service.py`
  - `backend/tests/test_appointments_db.py`
  - `backend/tests/test_doctors_api.py`

## Risks

### 1. Combined pytest execution still shows test harness isolation sensitivity

- An all-in-one pytest command across the new API test file and the existing backend tests can still surface a stale SQLite state ordering issue in `backend/tests/test_appointments_api.py`.
- The code itself passes when the tests are run in isolated slices, but the test harness is still more fragile than it should be.
- Recommendation: keep the module-level app reload pattern, or refactor the tests so each module builds its own app and database session factory with no shared global state.

### 2. Confirmation payload does not expose a doctor address field

- The current doctor model does not store an address, so the confirmation response uses the available doctor summary fields only.
- This matches the live backend data model, but if the frontend later needs a full address line, the doctor schema and seeds will need to expand.

## Defects

- No code defects blocking Feature 3 completion were identified in the reviewed backend changes.

## Recommendations

1. Keep the current transactional booking flow and slot booking checks.
2. Add a small cleanup pass for the test harness if CI must run every backend test module in one command.
3. If the booking UI needs a full address, extend the doctor data model before wiring the confirmation page.
