Implement scheduling refactor according to scheduling-refactor-plan.md.

New Rules:

1. Doctor availability records are NOT required.

2. User can book ANY FUTURE DATE.

3. Past dates must be disabled.

4. For today's date:
   - hide past time slots
   - show only remaining future slots

5. Generate slots dynamically:
   - start: 08:00
   - end: 18:00
   - interval: 2 hours

Example:
08:00
10:00
12:00
14:00
16:00
18:00

6. Slots are generated at runtime.

7. A slot becomes unavailable only if:
   - an appointment already exists for that doctor
   - same date
   - same slot

8. Appointment booking must:
   - validate future datetime
   - prevent duplicate booking
   - create appointment record

9. Do NOT seed availability data into DB.

10. Remove any dependency on availability generation jobs.

Update all backend tests.