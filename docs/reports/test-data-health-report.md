# Test Data Health Report

- Execution date: 2026-07-03T17:30:00+00:00
- Database inspected: `backend/app.db`
- Write policy used: no data loss; no records were deleted or overwritten
- Rows inserted: 0
- Rows repaired: 0
- Rows deleted: 0

## Schema Changes Detected

- No schema drift was detected between the current SQLAlchemy models and the live `backend/app.db` tables inspected for `doctors`, `patients`, `appointments`, and `doctor_availability`.
- Current live tables inspected: `alembic_version`, `appointments`, `doctor_availability`, `doctors`, `patients`.
- No missing columns, broken foreign-key relationships, or duplicate appointment slot conflicts were found.

## Validation Coverage

- Verified doctor list rows decode correctly for `appointment_types` and `languages`.
- Verified every appointment references an existing doctor and patient.
- Verified every appointment uses an appointment type supported by its doctor profile.
- Verified duplicate appointment slot conflicts are absent.
- Verified the three seeded future demo bookings on July 7, 8, and 9, 2026 are correctly excluded from generated availability.
- Verified all current appointment confirmations still resolve through `AppointmentService`.

## Broken Demo Records

- No active demo records required repair.
- No `@example.com` demo appointment has drifted into the past as of July 3, 2026.

## Repairs Performed

- None.
- No database rows were modified because the current dataset passes live business-rule validation for the implemented booking and search flows.

## Rows Skipped

- Skipped modifying 20 legacy `doctor_availability` rows because the current booking flow uses generated schedule slots rather than persisted availability rows, and the no-data-loss requirement takes priority.
- Skipped modifying 1 legacy `doctor_availability` inconsistency: row `id=2` marks Dr. Sarah Jenkins as `TELEMEDICINE` while the live doctor profile supports only `IN_PERSON`.
- Skipped modifying 5 historical appointments dated June 24, 2026 through July 4, 2026 because they remain valid retained records and are not safely distinguishable as disposable demo-only data.

## Knowledge Updates

- None required.
- No FAQ, knowledge-source, or sample-conversation updates were necessary for this refresh run.

## Remaining Issues

- `doctor_availability` remains a historical table with 20 past-dated rows and 0 future rows. This is expected under the current generated-schedule implementation, but the retained data is not aligned with current live booking behavior.
- Some doctor `next_available_slot` strings are presentation text rather than generated schedule data. They remain readable UI seed content, but they are not a computed availability source.
- A root-level stray `doctor_appointment.db` file exists outside the active backend DB path. It was not touched during this refresh run.

## Current Row Counts

- doctors=14
- patients=8
- appointments=9
- doctor_availability=20

## Recommended Next Execution

- Re-run this health check after any schema change to appointment, doctor, patient, or availability models.
- If the team decides to retire legacy `doctor_availability` data formally, do that as an explicit migration or cleanup task rather than as part of test-data refresh.
