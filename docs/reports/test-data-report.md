# Test Data Report

- Initial doctor-seed execution date: 2026-07-03T17:24:32.274708+00:00
- Idempotency verification date: 2026-07-03T17:25:37.566837+00:00
- Database inspected: `backend/app.db`
- Tables inspected: `doctors`, `patients`, `appointments`, `doctor_availability`
- Rows before initial doctor-seed run: doctors=10, patients=8, appointments=9, doctor_availability=20
- Rows inserted on initial doctor-seed run: doctors=4, patients=0, appointments=0, total=4
- Rows skipped on initial doctor-seed run: 3
- Rows before verification rerun: doctors=14, patients=8, appointments=9, doctor_availability=20
- Rows inserted on verification rerun: doctors=0, patients=0, appointments=0, total=0
- Rows skipped on verification rerun: 7

## Inserted Records

- Inserted doctor profile for Dr. Amelia Foster (Neurology).
- Inserted doctor profile for Dr. Rohan Mehta (Orthopedics).
- Inserted doctor profile for Dr. Grace Okafor (Gynecology).
- Inserted doctor profile for Dr. Leo Hammond (ENT).

## Duplicate Detection

- Initial doctor-seed run skipped maya.patel@example.com because a future IN_PERSON appointment already exists with doctor 2 on 2026-07-07 at 08:00.
- Initial doctor-seed run skipped ethan.brooks@example.com because a future TELEMEDICINE appointment already exists with doctor 6 on 2026-07-08 at 10:00.
- Initial doctor-seed run skipped olivia.carter@example.com because a future TELEMEDICINE appointment already exists with doctor 9 on 2026-07-09 at 12:00.
- Verification rerun skipped Dr. Amelia Foster because the doctor already exists.
- Verification rerun skipped Dr. Rohan Mehta because the doctor already exists.
- Verification rerun skipped Dr. Grace Okafor because the doctor already exists.
- Verification rerun skipped Dr. Leo Hammond because the doctor already exists.
- Verification rerun skipped maya.patel@example.com because a future IN_PERSON appointment already exists with doctor 2 on 2026-07-07 at 08:00.
- Verification rerun skipped ethan.brooks@example.com because a future TELEMEDICINE appointment already exists with doctor 6 on 2026-07-08 at 10:00.
- Verification rerun skipped olivia.carter@example.com because a future TELEMEDICINE appointment already exists with doctor 9 on 2026-07-09 at 12:00.

## Validation Checks

- Confirmed script targets `/Users/koushiksadhukhan/projects/doctor-appointment-app/backend/app.db` via an absolute SQLite DATABASE_URL when none is preconfigured.
- Validated appointment types against doctor-supported appointment_types via service-layer booking.
- Validated only future schedule-generated slots were booked.
- Validated duplicate doctor/date/time conflicts before insert.
- Validated patient email reuse never overwrites mismatched name or phone data.

## Knowledge Source Updates

- None. No knowledge-source or FAQ updates were required for demo booking data.

## Remaining Missing Demo Data

- Doctor coverage is broader than the default startup seed now, but some specialties still have only one profile and no associated future appointments.
- Legacy `doctor_availability` rows remain historical only and were not extended because the live booking flow uses generated schedule slots.
- The seeded dataset still favors manual booking/search coverage over chat-specific conversation history because chat state is request-scoped, not persisted.

## Rows After

- doctors=14
- patients=8
- appointments=9
- doctor_availability=20
