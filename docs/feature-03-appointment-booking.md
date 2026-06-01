# Feature F006/F011: Appointment Booking

## Goal

Allow the user to select date/time, enter patient details, and create an appointment.

## User Story

As a patient, I want to select a doctor slot and enter my details so that I can confirm my appointment.

## UI Requirements

- Doctor summary card at top/right.
- Date selector similar to calendar layout.
- Morning slot buttons.
- Afternoon slot buttons.
- Appointment type selector.
- Patient details form.
- Confirm appointment button.

## Form Fields

```txt
appointment_type
full_name
email
phone
health_description
```

## Validation Rules

```txt
appointment_type: required
full_name: required, min 2 characters
email: required, valid email
phone: optional
health_description: optional, max 500 characters
```

## API Requirements

Use:

```txt
POST /api/appointments
```

## Acceptance Criteria

- User cannot submit without date/time.
- User cannot submit invalid form.
- Backend creates patient and appointment.
- Availability slot is marked as booked.
- User is redirected to confirmation page.

