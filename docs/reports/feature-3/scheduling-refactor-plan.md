# Scheduling Refactor Plan

## Objective

Remove the booking flow's dependency on pre-created doctor availability rows stored in the database.

## What I inspected

- `docs/prompts/integration/feature-3-timeslot-selection/1-analysis-timeslot-existing-logic.md`
- `docs/feature-map.md`
- Frontend booking flow:
  - `frontend/app/appointments/page.tsx`
  - `frontend/features/appointments/components/AppointmentCalendar.tsx`
  - `frontend/features/appointments/api.ts`
  - `frontend/features/appointments/utils.ts`
- Backend availability and booking flow:
  - `backend/app/api/availability.py`
  - `backend/app/services/availability_service.py`
  - `backend/app/repositories/availability_repository.py`
  - `backend/app/services/appointment_service.py`
  - `backend/app/api/appointments.py`
  - `backend/app/db/seed.py`
  - `backend/app/db/database.py`
  - `backend/app/models/availability.py`
  - `backend/app/models/appointment.py`

## Current Flow

### 1. Frontend calendar request

- `frontend/app/appointments/page.tsx` calls `getDoctorAvailability(effectiveDoctorId)`.
- `frontend/features/appointments/api.ts` sends `GET /api/doctors/{doctorId}/availability`.
- The response is parsed into:
  - `availableDates: Date[]`
  - `morningSlots`
  - `afternoonSlots`

### 2. Backend availability API

- Route: `backend/app/api/availability.py`
- Service: `backend/app/services/availability_service.py`
- Repository: `backend/app/repositories/availability_repository.py`
- The service reads the `doctor_availability` table, groups the slots, and returns available dates only from existing rows.

### 3. Frontend date enable/disable logic

- `frontend/features/appointments/components/AppointmentCalendar.tsx`
  - builds a set from `availableDates`
  - disables every day that is:
    - before `referenceDate`, or
    - not present in the `availableDates` set
- `frontend/app/appointments/page.tsx`
  - further filters `availability.availableDates`
  - removes any date that does not have at least one unbooked slot matching the selected appointment type
  - resets the selected date if the filtered list becomes empty

### 4. Appointment booking validation

- Route: `backend/app/api/appointments.py`
- Service: `backend/app/services/appointment_service.py`
- Validation steps:
  - resolve the selected slot by `availability_id`
  - confirm slot belongs to the doctor
  - confirm date, time, and appointment type match
  - reject already booked slots
  - reject elapsed slots using server time

## Root Cause

The current UI is not generating availability dynamically. It is rendering only the dates that exist in `doctor_availability`.

The database seed data is the immediate blocker:

- `backend/app/db/seed.py` contains fixed availability dates from `2026-06-09` through `2026-06-18`.
- The current environment date is `2026-06-19`.
- That means all seeded slots are already in the past, so the backend returns no future availability rows.
- Because the frontend calendar disables any date not present in the backend response, the calendar appears to have no selectable current/future dates.

So the issue is not a single UI bug. It is a data-model dependency:

- calendar availability depends on persisted `doctor_availability` rows
- those rows are static seed data
- static seed data can expire
- once expired, the calendar has nothing to render

## Locations That Depend on Pre-Created Availability Rows

### Backend

- `backend/app/db/seed.py`
  - `DOCTOR_AVAILABILITY_SEED_DATA`
  - `seed_availability`
- `backend/app/db/database.py`
  - `init_db` calls `seed_availability`
- `backend/app/models/availability.py`
  - `DoctorAvailability` table definition
- `backend/app/repositories/availability_repository.py`
  - `get_available_dates`
  - `get_available_slots`
  - `get_availability_by_id`
  - `mark_slot_booked`
- `backend/app/services/availability_service.py`
  - `get_doctor_availability`
  - `get_doctor_availability_window`
  - `get_available_dates`
  - `get_available_slots`
  - `_filter_slots`
  - `_group_slots_by_session`
- `backend/app/api/availability.py`
  - `/doctors/{doctor_id}/availability`
- `backend/app/services/appointment_service.py`
  - `_validate_slot`
  - `create_appointment_booking`
  - `get_appointment_confirmation`
- `backend/app/models/appointment.py`
  - `availability_id` foreign key to `doctor_availability.id`

### Frontend

- `frontend/app/appointments/page.tsx`
  - filters dates by matching slots
  - disables booking when there are no matching slots
  - treats backend dates as the source of truth
- `frontend/features/appointments/components/AppointmentCalendar.tsx`
  - disables dates that are not in the backend-provided list
- `frontend/features/appointments/utils.ts`
  - `isPastAppointmentDate`
  - `isElapsedAppointmentSlot`
  - `filterBookableSlotsForDate`

## Future-Date Filtering Points

- Backend:
  - `backend/app/services/availability_service.py::_filter_slots`
    - filters by `date_from` and `date_to`
  - `backend/app/services/appointment_service.py::_slot_has_passed`
    - rejects elapsed slots based on server time
- Frontend:
  - `frontend/app/appointments/page.tsx`
    - filters dates to only those with matching unbooked slots
  - `frontend/features/appointments/components/AppointmentCalendar.tsx`
    - disables dates before today and dates not present in the backend response
  - `frontend/features/appointments/utils.ts`
    - filters out past dates and already elapsed times

## Files To Modify

- `backend/app/db/seed.py`
  - stop seeding fixed availability dates or replace them with rolling future dates
- `backend/app/db/database.py`
  - remove or replace the automatic `seed_availability` dependency
- `backend/app/models/availability.py`
  - remove the table if the refactor eliminates stored availability entirely
- `backend/app/repositories/availability_repository.py`
  - replace DB-backed slot lookup with generated availability logic
- `backend/app/services/availability_service.py`
  - compute availability from a schedule rule instead of querying stored availability rows
- `backend/app/api/availability.py`
  - keep or reshape the endpoint contract after the service changes
- `backend/app/services/appointment_service.py`
  - validate bookings against generated slot rules instead of a persisted availability row
- `backend/app/models/appointment.py`
  - remove `availability_id` if appointments no longer reference availability rows
- `frontend/app/appointments/page.tsx`
  - align date filtering with the new availability source
- `frontend/features/appointments/components/AppointmentCalendar.tsx`
  - may need simplified enable/disable logic if backend returns generated dates directly
- `frontend/features/appointments/api.ts`
  - update parsing if the response shape changes

## Functions That Can Be Deleted If Availability Is Generated Dynamically

- `backend/app/db/seed.py::seed_availability`
- `backend/app/repositories/availability_repository.py::get_available_dates`
- `backend/app/repositories/availability_repository.py::get_available_slots`
- `backend/app/repositories/availability_repository.py::get_availability_by_id`
- `backend/app/repositories/availability_repository.py::mark_slot_booked`
- `backend/app/services/availability_service.py::get_available_dates`
- `backend/app/services/availability_service.py::get_available_slots`
- `backend/app/services/availability_service.py::_group_slots_by_session` if grouping is moved upstream or the response shape changes
- `backend/app/services/availability_service.py::_filter_slots` if filtering is handled before persistence disappears
- `backend/app/models/availability.py::DoctorAvailability`

## Database Tables No Longer Required

- `doctor_availability`

## Tables That Must Remain

- `doctors`
- `patients`
- `appointments`

## Recommended Refactor Direction

1. Replace static seeded slot rows with a generated schedule source.
2. Make the availability API derive dates and times from doctor schedule rules instead of querying `doctor_availability`.
3. Update booking validation so it verifies a slot against generated rules rather than a foreign-keyed availability row.
4. Remove the availability table only after the booking model no longer depends on it.

## Conclusion

The calendar is empty because the app treats stored availability rows as the only source of current/future dates, and the current seed data has already expired. The refactor should remove that dependency rather than trying to patch the calendar UI alone.
