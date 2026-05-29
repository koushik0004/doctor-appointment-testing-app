# Backend Project Map

## Scope

Current backend implementation for the doctor appointment app.

## Folder Structure Summary

```txt
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── doctor.py
│   └── schemas/
│       ├── __init__.py
│       └── doctor.py
├── README.md
├── requirements.txt
└── AGENTS.md
```

## API Inventory

- `GET /api/health`

## Database Model Inventory

- `doctors`

## Module Inventory

### Added / Present

- `backend/app/main.py` - app entrypoint
- `backend/app/api/router.py` - API router assembly
- `backend/app/api/health.py` - health route
- `backend/app/core/config.py` - settings
- `backend/app/db/base.py` - declarative base and model import
- `backend/app/db/database.py` - engine and session factory
- `backend/app/models/doctor.py` - doctor model
- `backend/app/schemas/doctor.py` - doctor schema

### Removed / Not Present

- `backend/app/api/doctors.py`
- `backend/app/api/appointments.py`
- `backend/app/core/errors.py`
- `backend/app/db/seed.py`
- `backend/app/models/availability.py`
- `backend/app/models/patient.py`
- `backend/app/models/appointment.py`
- `backend/app/models/email_log.py`
- `backend/app/schemas/availability.py`
- `backend/app/schemas/patient.py`
- `backend/app/schemas/appointment.py`
- `backend/app/services/`

## Notes

- `backend/app/main.py` creates tables on startup.
- `backend/app/core/config.py` reads `.env` with defaults.
- `backend/app/db/database.py` uses SQLite by default.
