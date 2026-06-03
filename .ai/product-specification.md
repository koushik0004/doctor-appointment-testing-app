# Product Specification

## 1. Product Summary

The app helps patients find and book doctors in a clinic. The design should feel clean, modern, simple, and healthcare-focused. It should not become a hospital management system in v1. Keep data minimal and flows straightforward.

## 2. Core Pages

### 2.1 Home Page

Route:

```txt
/
```

Purpose:

- Introduce the booking platform.
- Show recommended doctor.
- Show available doctors.
- Show a lightweight booking summary side card.

Main UI blocks:

- Header navigation
- Hero section
- Recommended doctor card
- Available doctors grid
- Booking status side card
- Why book with CareNow card
- Footer

### 2.2 Doctor Listing Page

Route:

```txt
/doctors
```

Purpose:

- Show available doctors.
- Allow filtering by specialty.
- Allow filtering by appointment type.
- Allow selecting a doctor/time.

Main UI blocks:

- Sidebar filters
- Doctor result cards
- Booking summary card
- Pagination placeholder

### 2.3 Appointment Booking Page

Route:

```txt
/appointments/new?doctorId=<id>
```

Purpose:

- Select date.
- Select time slot.
- Enter patient details.
- Confirm appointment.

Main UI blocks:

- Doctor summary card
- Calendar/date selector
- Morning/afternoon slots
- Appointment type selector
- Patient details form
- Confirm appointment button

### 2.4 Booking Confirmation Page

Route:

```txt
/appointments/:appointmentId/confirmation
```

Purpose:

- Show confirmed booking details.
- Show confirmation ID.
- Show doctor details.
- Show patient info.
- Show visit instructions.
- Provide print summary placeholder.

## 3. V1 Functional Scope

Include:

- Static header and footer
- Doctor listing from backend
- Doctor filters from backend or frontend derived values
- Appointment date/time selection
- Patient details form
- Appointment create API
- SQLite persistence
- Confirmation page
- Email confirmation
- Basic loading/error states

Do not include in v1:

- Authentication
- Payments
- Admin dashboard
- Complex doctor schedule management
- Real calendar integrations
- Medical record uploads
- Video consultation
- Multi-clinic support

## 4. Data Rules

### Doctor

A doctor has:

- Name
- Specialty
- Rating
- Review count
- Clinic/location
- Consultation fee range
- Appointment types
- Next available date/time

### Patient

A patient has:

- Full name
- Email
- Phone optional in v1

### Appointment

An appointment has:

- Doctor
- Patient
- Date
- Time
- Appointment type
- Health description
- Status
- Confirmation code

## 5. Appointment Status Values

```txt
PENDING
CONFIRMED
CANCELLED
```

For v1, create appointments directly as `CONFIRMED`.

## 6. Acceptance Criteria for V1

- User can open home page.
- User can view doctors loaded from backend.
- User can open doctor listing page.
- User can filter by specialty and appointment type.
- User can open appointment booking page for selected doctor.
- User can choose date and time.
- User can enter patient details.
- User can submit appointment.
- Appointment is saved in SQLite.
- Confirmation page shows correct appointment details.
- Confirmation email is sent or logged.

