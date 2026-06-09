# Feature 03 Integration Memory

## Implemented

- Replaced the appointments page mock booking data with live doctor availability from the backend.
- Wired the booking submit flow to `POST /api/appointments`.
- Wired the confirmation page to `GET /api/appointments/{appointment_id}`.
- Preserved the doctor selection flow by passing the backend doctor ID through the booking and confirmation URLs.
- Added frontend booking API types for availability, appointment creation, and appointment confirmation payloads.

## Notable Contract Detail

- The frontend doctor model now keeps both the UI string `id` and the backend numeric `backendId`.
- Booking requests now use the numeric backend doctor ID and backend slot IDs.

