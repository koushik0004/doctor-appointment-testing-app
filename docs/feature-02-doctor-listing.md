# Feature F005/F010: Doctor Listing and Filters

## Goal

Allow users to browse doctors and filter by specialty and appointment type.

## User Story

As a patient, I want to view available doctors and filter them so that I can quickly find the right doctor for my visit.

## UI Requirements

- Sidebar filter section.
- Specialty filter options:
  - General Practice
  - Cardiology
  - Pediatrics
  - Dermatology
  - Internal Medicine
- Appointment type options:
  - In-person
  - Telemedicine
- Doctor cards with:
  - Photo/avatar
  - Name
  - Specialty
  - Rating
  - Reviews
  - Clinic/location
  - Next available slot
  - Fee range
  - Choose time / selected button
- Booking summary card on right side.

## API Requirements

Use:

```txt
GET /api/doctors?specialty=Cardiology&appointment_type=IN_PERSON
```

## Acceptance Criteria

- Doctors load from backend.
- Filters update doctor list.
- Selecting a doctor navigates to `/appointments/new?doctorId=<id>`.
- Empty state appears if no doctor matches filters.

