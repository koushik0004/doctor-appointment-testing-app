TASK: Implement Recommended Doctors API

Create endpoint:

GET /api/appointments/{appointment_id}/recommended-doctors

Response:

{
  "appointment_id": 123,
  "specialty": "General Physician",
  "recommended_doctors": [...]
}

Status Codes:

200
404
500

Requirements:

- OpenAPI documentation
- reuse recommendation service
- do not duplicate business logic