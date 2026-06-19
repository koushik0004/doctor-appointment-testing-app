TASK: Implement Feature 4 API Schemas

Create request/response schemas only.

Endpoint target:

GET /api/appointments/search

Request query params:

name
email
phone

Response:

{
  "count": 2,
  "appointments": [...]
}

Each appointment must contain:

- appointment_id
- patient_name
- patient_email
- patient_phone
- doctor_name
- doctor_specialty
- appointment_date
- appointment_time
- appointment_type
- status

Validation:

- At least one search parameter required
- Trim whitespace
- Email validation

DO NOT IMPLEMENT SERVICE OR ROUTE LOGIC.