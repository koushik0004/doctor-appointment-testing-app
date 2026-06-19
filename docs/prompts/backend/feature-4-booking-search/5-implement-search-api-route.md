TASK: Implement Appointment Search API

Create endpoint:

GET /api/appointments/search

Query params:

name
email
phone

Validation:

- At least one parameter required

Response:

{
  "count": n,
  "appointments": [...]
}

Status codes:

200
400
500

Reuse existing service layer.

Add OpenAPI documentation.

Do not modify booking APIs.