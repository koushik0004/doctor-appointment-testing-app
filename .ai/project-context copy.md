# Project Context

## Product Name

CareNow-style Doctor Appointment Booking App

## Objective

Build a simple web application for a clinic where users can browse doctors, filter doctors by specialty and appointment type, select a time slot, enter patient details, confirm an appointment, and receive an email confirmation.

The first development phase focuses only on the frontend, backend, and SQLite database. The AI chatbot and browser automation agent will be added after the manual appointment flow is stable.

## Reference Design Screens

The uploaded designs show these main screens:

1. Home / appointment search and booking overview
2. Filtered doctor list
3. Time selection and patient details form
4. Booking confirmation page

## Primary User Journey

```txt
User lands on home page
↓
User views recommended doctors
↓
User opens doctor listing/search page
↓
User filters or selects a doctor
↓
User chooses date and time
↓
User enters patient details
↓
User confirms appointment
↓
System saves appointment in SQLite
↓
System sends confirmation email
↓
User sees confirmation page
```

## Technical Stack

Frontend:

- Next.js
- TypeScript
- Tailwind CSS
- SCSS modules or global SCSS utilities where required
- Zustand for simple state management
- React Hook Form for forms
- Zod for validation

Backend:

- Python
- FastAPI
- SQLite
- SQLAlchemy ORM
- Pydantic schemas
- Alembic optional for later migrations
- `.venv` for Python virtual environment

Email:

- SMTP-based email sending for v1
- Console/log email mode allowed in local development

Future AI Layer:

- OpenAI / Claude for natural-language appointment command parsing
- Playwright for visible browser automation
- Chatbot UI embedded in frontend

## Development Style

Use spec-driven development. Each feature should have:

- Functional requirement
- UI requirement
- API requirement
- DB requirement
- Validation requirement
- Acceptance criteria
- Implementation checklist

