# Feature 4: Appointment Search Specification

## Goal

Allow a patient or staff user to search booked appointments by patient identity.

## User Story

As a user, I want to search appointments by patient name, email, or phone so that I can quickly find booking details.

## Search Requirements

A patient can search appointments using:

- email
- phone number
- full name

Search behavior:

- case insensitive
- partial search for name
- exact search for email
- exact search for phone

## Search Results

Each result should include:

- appointment id
- patient name
- patient email
- patient phone
- doctor name
- specialty
- appointment date
- appointment time
- appointment type
- booking status

## Status Values

Search results must expose booking status as:

- `booked`
- `completed`
- `cancelled`

### Status Mapping Note

The current backend appointment model stores:

- `PENDING`
- `CONFIRMED`
- `CANCELLED`

The search API should normalize backend values to the public search statuses above.

Recommended mapping:

- `PENDING` -> `booked`
- `CONFIRMED` -> `booked`
- `CANCELLED` -> `cancelled`

If the product later introduces a completed workflow, map that state to `completed`.

## User Flow

1. User opens the appointment search page or search panel.
2. User enters at least one of:
   - name
   - email
   - phone
3. User submits the search request.
4. Backend validates input and performs a case-insensitive lookup.
5. Backend returns matching appointments ordered by most recent appointment first.
6. UI renders the results list or an empty state when no records are found.

## API Contracts

### GET /api/appointments/search

Query params:

```txt
name?: string
email?: string
phone?: string
```

### Request Rules

- At least one search parameter is required
- Whitespace must be trimmed before search
- Email must be valid when provided

### Response

```json
{
  "count": 2,
  "appointments": [
    {
      "appointment_id": 5001,
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

### Empty Response

```json
{
  "count": 0,
  "appointments": []
}
```

## DB Requirements

The search feature should read from these existing tables:

- `appointments`
- `patients`
- `doctors`

Required join path:

- `appointments.patient_id` -> `patients.id`
- `appointments.doctor_id` -> `doctors.id`

Recommended searchable columns:

- `patients.full_name`
- `patients.email`
- `patients.phone`

Existing helpful columns:

- `appointments.appointment_date`
- `appointments.appointment_time`
- `appointments.appointment_type`
- `appointments.status`

## Validation Rules

- reject requests with no search parameters
- trim leading and trailing whitespace from all query params
- email must pass standard email validation
- name search must allow partial matching
- phone search must match exactly after trimming
- name, email, and phone searches should be case insensitive where applicable

## Error Responses

### 400 Bad Request

Returned when the request has no search parameters or invalid input.

Example:

```json
{
  "detail": "At least one search parameter is required."
}
```

### 422 Unprocessable Entity

Returned when query parameter validation fails, such as an invalid email format.

Example:

```json
{
  "detail": [
    {
      "loc": ["query", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 200 OK

Returned when the search succeeds, including when zero records are found.

## Non-Goals

- do not change appointment creation behavior
- do not change confirmation page payloads
- do not introduce AI-assisted search
- do not require browser automation

## Implementation Notes

- keep search logic in the backend service layer
- keep route logic thin
- prefer reusable response schemas
- order results by:
  - `appointment_date DESC`
  - `appointment_time DESC`
- add indexes for patient search fields if query performance requires it

