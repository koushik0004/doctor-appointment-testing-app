# Testing Strategy

## Backend Tests First

Use pytest.

Recommended tests:

- Health endpoint returns ok.
- Doctors endpoint returns seeded doctors.
- Doctor availability endpoint returns slots.
- Appointment creation succeeds with valid payload.
- Appointment creation fails if slot is already booked.
- Appointment creation fails for invalid doctor.
- Cancel appointment updates status.

## Frontend Testing

For v1, start with manual testing and simple component tests later.

Manual test cases:

1. Open home page.
2. Open doctor listing page.
3. Apply specialty filter.
4. Select doctor.
5. Select date and time.
6. Submit invalid patient form.
7. Submit valid patient form.
8. Verify confirmation page.
9. Verify backend DB contains appointment.
10. Verify email logged/sent.

## AI Agent Testing Later

Future tests:

- Parse appointment command.
- Detect missing doctor/date/time.
- Fill defaults.
- Book appointment through Playwright visible browser.

