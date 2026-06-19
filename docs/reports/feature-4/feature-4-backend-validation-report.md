# Feature 4 Backend Validation Report

Validation date: 2026-06-19

## Summary

Feature 4 backend behavior was validated against the booking, search, and appointment-details flows.

Verified outcomes:

- Existing booking API works
- Appointment creation works
- Booking/confirmation payload remains unchanged
- Search by email works
- Search by phone works
- Search by name works
- Appointment details API works

## Test Run

Command:

```bash
cd backend
pytest tests/test_appointments_api.py tests/test_appointments_db.py tests/test_appointment_search_service.py
```

Result:

- `10 passed`
- `1 warning` from an unrelated Starlette/httpx test client deprecation notice

## Tested Endpoints

- `POST /api/appointments`
- `GET /api/appointments/{appointment_id}`
- `GET /api/appointments/search?name=...`
- `GET /api/appointments/search?email=...`
- `GET /api/appointments/search?phone=...`

## Sample Requests and Responses

### 1) Appointment creation

Request:

```http
POST /api/appointments
Content-Type: application/json
```

```json
{
  "doctor_id": 1,
  "appointment_date": "2026-06-20",
  "start_time": "10:00",
  "appointment_type": "IN_PERSON",
  "patient": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "9999999999"
  },
  "health_description": "Regular follow-up for high blood pressure."
}
```

Response:

```json
{
  "id": 1,
  "confirmation_code": "CN-17514-JY",
  "status": "CONFIRMED",
  "doctor_id": 1,
  "patient_id": 1,
  "appointment_date": "2026-06-20",
  "start_time": "10:00",
  "end_time": "10:30"
}
```

Notes:

- This matches the existing booking/confirmation payload shape.
- No fields were added or removed from the booking response during the appointment-details work.

### 2) Appointment details

Request:

```http
GET /api/appointments/1
```

Response:

```json
{
  "appointment_id": 1,
  "doctor": {
    "name": "Dr. Sarah Jenkins",
    "specialty": "Cardiology",
    "clinic_name": "CareNow Central Clinic",
    "location": "London, UK"
  },
  "patient": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "9999999999"
  },
  "appointment_date": "2026-06-20",
  "appointment_time": "10:00",
  "appointment_type": "IN_PERSON",
  "status": "CONFIRMED",
  "created_at": "2026-06-19T13:29:50.757458"
}
```

### 3) Search by name

Request:

```http
GET /api/appointments/search?name=john
```

Response:

```json
{
  "count": 1,
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

### 4) Search by email

Request:

```http
GET /api/appointments/search?email=john.doe@example.com
```

Response:

```json
{
  "count": 1,
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

### 5) Search by phone

Request:

```http
GET /api/appointments/search?phone=9999999999
```

Response:

```json
{
  "count": 1,
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

## Edge Cases Tested

- Missing search parameters return `400 Bad Request`
- Invalid email query input returns `422 Unprocessable Entity`
- Unknown appointment ID returns `404 Not Found`
- Duplicate booking on the same doctor/date/time returns `409 Conflict`
- Past slot booking returns `400 Bad Request`
- Search by whitespace-padded name is trimmed and still matches
- Search by email and phone is case/format tolerant as implemented

## Issues Found

- No functional issues were found in the validated feature set.
- The test run emits one unrelated Starlette/httpx deprecation warning in the FastAPI test client stack.

