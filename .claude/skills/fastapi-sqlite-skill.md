# Skill: FastAPI + SQLite

## Purpose

Use this skill when building backend APIs and database logic.

## Standards

- Use FastAPI routers.
- Use SQLAlchemy ORM.
- Use Pydantic schemas.
- Use dependency injection for DB sessions.
- Use SQLite for local persistence.

## Route Handler Pattern

```txt
Validate request through schema
↓
Call service function
↓
Return response schema
```

## Service Pattern

Services should contain business logic such as:

- Checking doctor existence
- Checking slot availability
- Creating patient
- Creating appointment
- Marking slot booked
- Sending/logging email

