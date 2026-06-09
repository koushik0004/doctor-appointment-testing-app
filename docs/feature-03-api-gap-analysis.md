# Feature 03 API Gap Analysis

## Scope

Frontend booking flow vs. backend doctor, availability, and appointment APIs.

## Frontend booking flow

- The doctors page already calls the live doctors API through `frontend/features/doctors/api.ts`.
- The booking page in `frontend/app/appointments/page.tsx` still uses static doctor, date, and slot fixtures from `frontend/features/appointments/mock-data.ts`.
- The confirmation page in `frontend/app/appointments/confirmation/page.tsx` reads from local store state and fallback mock data instead of the backend confirmation endpoint.

## Backend booking APIs

- `GET /api/doctors`
- `GET /api/doctors/{doctor_id}`
- `GET /api/doctors/{doctor_id}/availability`
- `POST /api/appointments`
- `GET /api/appointments/{appointment_id}`

## Response mismatches

- Doctor records from the backend use snake_case fields such as `review_count`, `clinic_name`, `consultation_fee_min`, and `next_available_slot`.
- The frontend doctor model uses camelCase fields and derived structures such as `feeRange` and `nextAvailable`.
- The frontend already maps doctor list and doctor detail responses correctly, but the appointment flow does not yet reuse the live doctor response.
- The availability API returns `available_dates`, `morning_slots`, and `afternoon_slots`, with each slot carrying `id`, `available_date`, `start_time`, `end_time`, `appointment_type`, and `is_booked`.
- The current appointment UI expects a flat `AppointmentSlot[]` with display-time strings and no slot IDs, so it cannot submit a valid `availability_id`.
- The appointment confirmation API returns confirmation data from the backend, but the current confirmation page renders local fallback data instead of fetching by `appointment_id`.

## Request mismatches

- `POST /api/appointments` expects:
  - `doctor_id`
  - `availability_id`
  - `appointment_date`
  - `start_time` in `HH:MM`
  - `appointment_type`
  - `patient.full_name`
  - `patient.email`
  - `patient.phone`
  - optional `health_description`
- The current booking form only produces flat patient fields and does not submit `availability_id` or the backend time format.
- The current appointment page stores a synthetic confirmation code instead of the backend `appointment_id` and `confirmation_code`.

## Integration gaps to close

- Replace the booking page mock doctor and mock availability data with live API calls.
- Track the selected availability slot ID and backend-formatted start time.
- Submit the backend appointment payload shape from the booking form.
- Fetch the confirmation page from the backend using the real appointment ID.
- Keep the booking store aligned with the live flow so navigation between pages remains stable.
