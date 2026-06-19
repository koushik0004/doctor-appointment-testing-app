# Feature 4 Booking Search Analysis

## Scope

This document analyzes the current backend state before implementing appointment search.

The existing codebase already supports:

- doctor listing
- doctor availability lookup
- appointment creation
- appointment confirmation lookup

There is no appointment search endpoint yet.

## Current Models

### Appointment Model

Source: `backend/app/models/appointment.py`

Current ORM fields:

- `id`
- `confirmation_code`
- `doctor_id`
- `patient_id`
- `appointment_date`
- `appointment_time`
- `appointment_type`
- `health_description`
- `status`
- `created_at`
- `updated_at`

Current constraints and indexes:

- `confirmation_code` is unique and indexed
- `doctor_id` is indexed and has a foreign key to `doctors.id`
- `patient_id` is indexed and has a foreign key to `patients.id`
- `appointment_date` is indexed
- `status` is indexed
- composite index on `doctor_id`, `appointment_date`, `appointment_time`
- unique constraint on `doctor_id`, `appointment_date`, `appointment_time`
- check constraint on `appointment_type` values: `IN_PERSON`, `TELEMEDICINE`
- check constraint on `status` values: `PENDING`, `CONFIRMED`, `CANCELLED`

Important observation:

- The current SQLAlchemy model does not define `availability_id`
- The checked-in SQLite file `backend/app.db` still contains a legacy `availability_id` column on `appointments`
- The current tests and ORM metadata do not use that column

### Patient Model

Source: `backend/app/models/patient.py`

Current ORM fields:

- `id`
- `full_name`
- `email`
- `phone`
- `created_at`

Current constraints and indexes:

- `email` is unique and indexed
- `id` is indexed
- `phone` is nullable
- `full_name` has no index

### Doctor Model

Source: `backend/app/models/doctor.py`

Current ORM fields:

- `id`
- `name`
- `specialty`
- `rating`
- `review_count`
- `clinic_name`
- `location`
- `consultation_fee_min`
- `consultation_fee_max`
- `next_available_slot`
- `appointment_types`
- `languages`
- `description`
- `image_url`
- `is_active`

Current constraints and indexes:

- `specialty` is indexed
- `id` is indexed
- `appointment_types` and `languages` are stored as JSON text strings

### Doctor Availability Model

Source: `backend/app/models/availability.py`

Current ORM fields:

- `id`
- `doctor_id`
- `available_date`
- `start_time`
- `end_time`
- `appointment_type`
- `is_booked`
- `created_at`

Current constraints and indexes:

- foreign key to `doctors.id`
- `doctor_id` is indexed
- `available_date` is indexed
- `is_booked` is indexed
- `id` is indexed
- check constraint on `appointment_type`

## Relationships

### Doctor to Appointment

- `appointments.doctor_id` references `doctors.id`
- The code uses this relationship through foreign keys and explicit queries
- There is no SQLAlchemy `relationship()` declared in the model classes

### Patient to Appointment

- `appointments.patient_id` references `patients.id`
- Appointment confirmation loads the patient directly with `session.get(Patient, appointment.patient_id)`
- There is no SQLAlchemy `relationship()` declared in the model classes

### Doctor to Patient

- There is no direct foreign key between `doctors` and `patients`
- The connection is indirect through `appointments`

### Appointment to Availability

- The live SQLite artifact still has `appointments.availability_id`
- The current ORM model and booking service do not use it
- The current booking flow derives slot occupancy from appointments, not from `doctor_availability.is_booked`

## Existing DB Schema

This section reflects the current backend state from the ORM plus the checked-in SQLite artifact.

### `doctors`

- `id`
- `name`
- `specialty`
- `rating`
- `review_count`
- `clinic_name`
- `location`
- `consultation_fee_min`
- `consultation_fee_max`
- `next_available_slot`
- `appointment_types`
- `languages`
- `description`
- `image_url`
- `is_active`

Indexes:

- `ix_doctors_id`
- `ix_doctors_specialty`

### `patients`

- `id`
- `full_name`
- `email`
- `phone`
- `created_at`

Indexes:

- `ix_patients_id`
- `ix_patients_email` unique

### `doctor_availability`

- `id`
- `doctor_id`
- `available_date`
- `start_time`
- `end_time`
- `appointment_type`
- `is_booked`
- `created_at`

Indexes:

- `ix_doctor_availability_id`
- `ix_doctor_availability_doctor_id`
- `ix_doctor_availability_available_date`
- `ix_doctor_availability_is_booked`

### `appointments`

Current live SQLite artifact includes:

- `id`
- `confirmation_code`
- `doctor_id`
- `patient_id`
- `availability_id`
- `appointment_date`
- `appointment_time`
- `appointment_type`
- `health_description`
- `status`
- `created_at`
- `updated_at`

Indexes and constraints:

- `ix_appointments_id`
- `ix_appointments_confirmation_code` unique
- `ix_appointments_doctor_id`
- `ix_appointments_patient_id`
- `ix_appointments_appointment_date`
- `ix_appointments_status`
- `ix_appointments_doctor_date_time`
- `ix_appointments_availability_id` unique
- check constraint for `appointment_type`
- check constraint for `status`

## Existing Booking APIs

### `POST /api/appointments`

Source:

- `backend/app/api/appointments.py`
- `backend/app/services/appointment_service.py`

Behavior:

- validates doctor, slot date, slot time, appointment type, and patient data
- creates or updates a patient by email
- creates an appointment
- returns a booking confirmation payload

### `GET /api/appointments/{appointment_id}`

Source:

- `backend/app/api/appointments.py`
- `backend/app/services/appointment_service.py`

Behavior:

- returns the appointment confirmation payload
- includes doctor summary, patient summary, appointment date/time, type, and health description

### Supporting booking API: `GET /api/doctors/{doctor_id}/availability`

Source:

- `backend/app/api/availability.py`
- `backend/app/services/availability_service.py`

Behavior:

- returns available slots for a doctor on a given date
- derives booked slots from existing appointments

## Current Response Payloads

### Create Appointment Response

Schema source: `backend/app/schemas/appointment.py`

Returned fields:

- `id`
- `confirmation_code`
- `status`
- `doctor_id`
- `patient_id`
- `appointment_date`
- `start_time`
- `end_time`

Current service behavior:

- `status` is returned as `CONFIRMED` for newly created bookings

### Appointment Confirmation Response

Returned fields:

- `id`
- `confirmation_code`
- `status`
- `doctor`
- `patient`
- `appointment_date`
- `start_time`
- `end_time`
- `appointment_type`
- `health_description`

Nested doctor payload:

- `name`
- `specialty`
- `clinic_name`
- `location`

Nested patient payload:

- `full_name`
- `email`
- `phone`

### Doctor Availability Response

Returned fields:

- `date`
- `doctor_id`
- `available_slots`

Each slot includes:

- `id`
- `available_date`
- `start_time`
- `end_time`
- `is_booked`

### Doctor List Response

Returned fields:

- `items`
- `total`

Each doctor item includes:

- `id`
- `name`
- `specialty`
- `rating`
- `review_count`
- `clinic_name`
- `location`
- `consultation_fee_min`
- `consultation_fee_max`
- `next_available_slot`
- `appointment_types`
- `languages`
- `description`
- `image_url`

## Reusable Models

The following pieces are reusable for appointment search:

- `Patient` model
- `Appointment` model
- `Doctor` model
- `AppointmentStatus` enum
- `AppointmentType` enum
- appointment repository helpers for fetching by id and by doctor/date/time
- patient repository helper `get_patient_by_email`
- doctor service lookup helpers

What is not reusable as-is:

- There is no search request schema
- There is no search response schema
- There is no search repository/service function
- There is no route for appointment search

## Required Changes For Appointment Search

To support the planned search feature, the backend needs:

1. A new search request schema for query params `name`, `email`, and `phone`
2. Validation that at least one query param is provided
3. Whitespace trimming before searching
4. Case-insensitive exact match for email
5. Exact match for phone
6. Case-insensitive partial match for patient name
7. A repository query that joins `appointments`, `patients`, and `doctors`
8. A service layer that returns search results ordered by:
   - `appointment_date DESC`
   - `appointment_time DESC`
9. A response schema that returns `count` and an `appointments` list
10. Status normalization for the search API
11. Database indexes for patient search fields

### Status Normalization Gap

The search feature spec expects these status values:

- `booked`
- `completed`
- `cancelled`

The current database and booking code only use:

- `PENDING`
- `CONFIRMED`
- `CANCELLED`

This means the search feature needs an explicit mapping layer. The current code does not define any `COMPLETED` status.

## Missing Indexes

Current schema gaps for search:

- `patients.phone` has no index
- `patients.full_name` has no index
- case-insensitive email search may not fully benefit from the existing unique index unless the query strategy matches the index collation

Existing helpful indexes already in place:

- `patients.email` unique index
- `appointments.patient_id`
- `appointments.doctor_id`
- `appointments.appointment_date`
- `appointments.doctor_date_time`

Important note:

- A plain index on `patients.full_name` may only help limited patterns depending on the query form
- For true partial substring search, SQLite may still scan unless the implementation uses prefix search, normalized search columns, or FTS

## Recommended API Design

### Endpoint

`GET /api/appointments/search`

### Query Params

- `name`
- `email`
- `phone`

### Validation

- At least one parameter required
- Trim all incoming values
- Validate email format when `email` is present

### Response Shape

```json
{
  "count": 2,
  "appointments": [
    {
      "appointment_id": 1,
      "patient_name": "John Doe",
      "patient_email": "john.doe@example.com",
      "patient_phone": "9999999999",
      "doctor_name": "Dr. Sarah Jenkins",
      "doctor_specialty": "Cardiology",
      "appointment_date": "2026-06-20",
      "appointment_time": "10:00",
      "appointment_type": "IN_PERSON",
      "status": "booked"
    }
  ]
}
```

### Implementation Notes

- Use a dedicated service function for search logic
- Keep the route thin
- Join across `appointments`, `patients`, and `doctors`
- Return an empty list when no matches are found
- Do not change the existing booking create/confirmation endpoints while adding search

