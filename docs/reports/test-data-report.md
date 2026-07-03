# Test Data Report

- Initial seed execution date: 2026-07-03T06:08:19.028364+00:00
- Idempotency verification date: 2026-07-03T06:09:17.069171+00:00
- Database inspected: `backend/app.db`
- Tables inspected: `doctors`, `patients`, `appointments`, `doctor_availability`
- Rows before initial seed: doctors=10, patients=5, appointments=6, doctor_availability=20
- Rows inserted on initial seed: patients=3, appointments=3, total=6
- Rows skipped on initial seed: 0
- Rows before verification rerun: doctors=10, patients=8, appointments=9, doctor_availability=20
- Rows inserted on verification rerun: patients=0, appointments=0, total=0
- Rows skipped on verification rerun: 3

## Inserted Records

- Inserted appointment `CN-42165-EY` for `maya.patel@example.com` on `2026-07-07` at `08:00` with Dr. Marcus Chen (`IN_PERSON`).
- Inserted appointment `CN-44551-P9` for `ethan.brooks@example.com` on `2026-07-08` at `10:00` with Dr. Daniel Park (`TELEMEDICINE`).
- Inserted appointment `CN-81370-5B` for `olivia.carter@example.com` on `2026-07-09` at `12:00` with Dr. Priya Nair (`TELEMEDICINE`).

## Duplicate Detection

- Verification rerun skipped `maya.patel@example.com` because a future `IN_PERSON` appointment already exists with doctor `2` on `2026-07-07` at `08:00`.
- Verification rerun skipped `ethan.brooks@example.com` because a future `TELEMEDICINE` appointment already exists with doctor `6` on `2026-07-08` at `10:00`.
- Verification rerun skipped `olivia.carter@example.com` because a future `TELEMEDICINE` appointment already exists with doctor `9` on `2026-07-09` at `12:00`.

## Validation Checks

- Confirmed the active backend environment uses `backend/.env` with `DATABASE_URL=sqlite:///./app.db`.
- Validated appointment type support through the existing appointment service before each insert.
- Validated only future schedule-generated slots were booked.
- Validated duplicate doctor/date/time conflicts before each insert.
- Validated patient email reuse never overwrites mismatched name or phone data.
- Confirmed a second execution is safe and inserts no duplicates.

## Knowledge Source Updates

- None. No knowledge-source or FAQ updates were required for demo booking data.

## Remaining Missing Demo Data

- Legacy `doctor_availability` rows remain historical only and were not extended because the live booking flow uses generated schedule slots.
- The seeded dataset still favors manual booking/search coverage over chat-specific conversation history because chat state is request-scoped, not persisted.

## Rows After Final Verification

- doctors=10
- patients=8
- appointments=9
- doctor_availability=20
