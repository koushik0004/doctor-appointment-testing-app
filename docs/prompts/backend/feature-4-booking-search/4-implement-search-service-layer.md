TASK: Implement Appointment Search Service

Implement service layer only.

Requirements:

Search appointment by:

1. email
2. phone
3. patient name

Rules:

EMAIL:
exact match
case insensitive

PHONE:
exact match

NAME:
partial match
case insensitive

Return:

appointments ordered by:

appointment_date DESC
appointment_time DESC

If no records found:

return empty list

DO NOT CREATE API ROUTES YET.

Add unit-testable service functions.