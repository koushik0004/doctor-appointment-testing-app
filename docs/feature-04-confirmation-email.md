# Feature F007/F012: Confirmation Page and Email

## Goal

Show appointment confirmation and send/log confirmation email.

## User Story

As a patient, I want to see confirmation details and receive an email so that I know my appointment is successfully booked.

## UI Requirements

Confirmation page should show:

- Success icon
- `Appointment confirmed!`
- Confirmation ID
- Doctor name and specialty
- Date and time
- Location
- Patient info
- Visit reason
- What to do next instructions
- Back to home link
- Print summary placeholder button

## Backend Requirements

- Generate confirmation code.
- Send email in `smtp` mode.
- Log email in `console` mode.
- Store email status in `email_logs` if table is implemented.

## Email Template

Subject:

```txt
Your CareNow appointment is confirmed
```

Body:

```txt
Hello {patient_name},

Your appointment is confirmed.

Doctor: {doctor_name}
Date: {date}
Time: {time}
Location: {clinic_name}
Confirmation ID: {confirmation_code}

Please arrive 15 minutes early.
```

## Acceptance Criteria

- Confirmation page loads by appointment id.
- Confirmation ID appears.
- Email is printed to console or sent through SMTP.
- Failure to send email should not delete appointment.

