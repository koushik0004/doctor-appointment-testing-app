TASK: Build Appointment Details Panel

When user clicks:

View Details

Load:

GET /api/appointments/{id}

Display:

Patient Information:
- Name
- Email
- Phone

Doctor Information:
- Name
- Specialty

Appointment Information:
- Date
- Time
- Appointment Type
- Status
- Booking Date

States:

- No appointment selected
- Loading
- Error
- Success

Desktop:
right-side panel

Mobile:
stack below result list

Reuse existing card components where possible.