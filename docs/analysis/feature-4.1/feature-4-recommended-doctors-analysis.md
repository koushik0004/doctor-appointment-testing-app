# Feature 4.1 Recommended Doctors Analysis

## Scope

This document analyzes the current backend implementation that can support a recommended-doctors feature after viewing an appointment.

The goal of this analysis is to identify:

- the existing doctor model
- how specialty data is stored
- where rating data comes from
- what availability data exists
- which current doctor-related APIs can be reused
- the best API shape for the recommendation endpoint

No code changes are made in this step.

## Existing Doctor Schema

Source: [`backend/app/models/doctor.py`](../../../backend/app/models/doctor.py:9)

Current `doctors` table fields:

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

Important model details:

- `id` is the primary key and indexed
- `specialty` is indexed
- `rating` is stored as `Float`
- `review_count` is stored as `Integer`
- `appointment_types` and `languages` are stored as JSON-encoded text strings
- `is_active` is the current availability flag for list filtering

## Specialty Storage Approach

Source: [`backend/app/models/doctor.py`](../../../backend/app/models/doctor.py:14), [`backend/app/db/seed.py`](../../../backend/app/db/seed.py:6)

Specialty is stored as a plain text column on the `doctors` table.

Current values are human-readable labels such as:

- `Cardiology`
- `Pediatrics`
- `Dermatology`
- `Internal Medicine`
- `General Practice`

Observations:

- there is no separate specialty lookup table
- there is no specialty normalization layer
- recommendation logic will need to compare the specialty string directly
- if related-specialty fallback is added later, that mapping will have to live in service logic or a separate reference structure

## Rating Data Source

Source: [`backend/app/models/doctor.py`](../../../backend/app/models/doctor.py:15), [`backend/app/db/seed.py`](../../../backend/app/db/seed.py:6)

Rating data is stored directly on the doctor record.

Fields involved:

- `rating` - float value used for ranking
- `review_count` - integer tie-breaker used for ranking

Current ranking logic in the doctor repository sorts by:

1. `rating DESC`
2. `review_count DESC`
3. `id ASC`

Source: [`backend/app/repositories/doctor_repository.py`](../../../backend/app/repositories/doctor_repository.py:8)

There is no separate review table or aggregate rating service in the current backend. The seeded doctor records are the source of truth for the initial rating values.

## Availability Fields

There are two availability-related sources in the current backend.

### 1. Doctor display field

Source: [`backend/app/models/doctor.py`](../../../backend/app/models/doctor.py:21)

`next_available_slot` is a text field on the doctor record.

Current use:

- it is returned in doctor list and doctor detail responses
- it is seeded as display text such as `Today, 10:30 AM`

Important limitation:

- this field is presentation data, not a normalized availability source
- it should not be treated as authoritative booking availability for recommendation logic

### 2. Normalized availability table

Source: [`backend/app/models/availability.py`](../../../backend/app/models/availability.py:9)

Current `doctor_availability` fields:

- `id`
- `doctor_id`
- `available_date`
- `start_time`
- `end_time`
- `appointment_type`
- `is_booked`
- `created_at`

Important constraints:

- `doctor_id` is a foreign key to `doctors.id`
- `available_date` is indexed
- `is_booked` is indexed
- `appointment_type` is constrained to `IN_PERSON` or `TELEMEDICINE`

### Availability service behavior

Source: [`backend/app/services/availability_service.py`](../../../backend/app/services/availability_service.py:31)

Current availability logic does not read from `doctor_availability` for booking decisions.

Instead, it:

- loads booked appointments for the doctor and date
- generates available slots from the schedule service
- returns a response containing `date`, `doctor_id`, and `available_slots`

This is important for recommendation work because "available for booking" currently means "has an open booking slot in the scheduling flow", not simply "has a `doctor_availability` row".

## Existing Doctor Search and List APIs

### `GET /api/doctors`

Source: [`backend/app/api/doctors.py`](../../../backend/app/api/doctors.py:11)

Current behavior:

- returns active doctors only
- supports optional `specialty` filter
- supports optional `appointment_type` filter
- reuses the doctor service and repository layers

Response model:

- `DoctorListResponse`
- `items: list[DoctorResponse]`
- `total: int`

Source: [`backend/app/schemas/doctor.py`](../../../backend/app/schemas/doctor.py:11)

### `GET /api/doctors/{doctor_id}`

Source: [`backend/app/api/doctors.py`](../../../backend/app/api/doctors.py:20)

Current behavior:

- returns one active doctor by id
- raises a not-found error if the doctor does not exist or is inactive

### `GET /api/doctors/{doctor_id}/availability`

Source: [`backend/app/api/availability.py`](../../../backend/app/api/availability.py:13)

Current behavior:

- returns generated availability for one doctor on one date
- uses the schedule and appointment data path rather than the `doctor_availability` table directly

This endpoint is useful for later implementation work if recommendation responses need a true next-bookable date or slot.

## Reusable Services

The following existing backend pieces are directly reusable for the recommended-doctors feature.

### Doctor lookup and filtering

- [`get_doctor_by_id`](../../../backend/app/repositories/doctor_repository.py:38)
- [`get_doctor`](../../../backend/app/services/doctor_service.py:43)
- [`get_doctors_by_filters`](../../../backend/app/repositories/doctor_repository.py:17)
- [`list_doctors`](../../../backend/app/services/doctor_service.py:30)

### Availability lookup

- [`get_doctor_available_slots`](../../../backend/app/services/availability_service.py:31)
- [`get_available_slots`](../../../backend/app/services/availability_service.py:50)
- [`get_appointments_for_doctor_on_date`](../../../backend/app/repositories/appointment_repository.py:29)

### Appointment context lookup

- [`get_appointment_by_id`](../../../backend/app/repositories/appointment_repository.py:13)
- [`get_appointment_details`](../../../backend/app/services/appointment_service.py:144)

That appointment lookup path is the cleanest way to resolve the source doctor for a recommendation request.

## API Design Recommendation

Recommended endpoint:

```txt
GET /api/appointments/{appointment_id}/recommended-doctors
```

Why this shape fits the current backend:

- the recommendation is triggered after an appointment is viewed
- the appointment id is already the natural entry point for resolving the current doctor
- the backend can load the appointment, then load the appointment doctor, then derive the specialty
- this keeps client code thin and avoids duplicating doctor resolution logic in the frontend

Recommended response shape:

```json
{
  "appointment_id": 123,
  "specialty": "General Practice",
  "recommended_doctors": []
}
```

Recommendation rules that fit the current data model:

- filter by `doctor.specialty == current_specialty`
- filter by `doctor.is_active == true`
- exclude the current doctor id
- sort by `rating DESC`, `review_count DESC`, `name ASC`
- cap the result set at 5 doctors

Availability note:

- the current backend has enough data to find active doctors by specialty
- if the endpoint must only return doctors that are currently bookable, it should also check schedule availability using the availability service or a dedicated recommendation availability query
- `next_available_slot` alone is not sufficient as a booking-availability signal

## Analysis Summary

The current backend already has the core primitives needed for recommended doctors:

- doctor identity and specialty
- rating and review count for ranking
- active/inactive filtering
- appointment-based availability lookup
- appointment-to-doctor lookup

The main missing piece is a dedicated recommendation service and API route that combines those existing primitives into one appointment-centric response.
