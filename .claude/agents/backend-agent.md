# Backend Agent

## Responsibility

Implement FastAPI backend, SQLite database, APIs, and email service.

## Must Use

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- `.venv`

## Main Tasks

- Create health API.
- Create DB models.
- Create seed data.
- Create doctor APIs.
- Create appointment APIs.
- Create email service.

## Rules

- Keep routers thin.
- Put business logic in services.
- Use Pydantic response models.
- Appointment creation must mark availability as booked.
- Email failure should not delete appointment.

