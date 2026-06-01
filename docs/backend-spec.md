# Backend Engineering Specification

## 1. Framework

Use:

- Python 3.12 preferred
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic
- python-dotenv
- pytest

Use `.venv` for package isolation.

## 2. Backend Folder Structure

```txt
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── router.py
│   │   ├── health.py
│   │   ├── doctors.py
│   │   └── appointments.py
│   ├── core/
│   │   ├── config.py
│   │   └── errors.py
│   ├── db/
│   │   ├── database.py
│   │   ├── base.py
│   │   └── seed.py
│   ├── models/
│   │   ├── doctor.py
│   │   ├── availability.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   └── email_log.py
│   ├── schemas/
│   │   ├── doctor.py
│   │   ├── availability.py
│   │   ├── patient.py
│   │   └── appointment.py
│   └── services/
│       ├── doctor_service.py
│       ├── appointment_service.py
│       └── email_service.py
│
├── scripts/
│   └── seed_db.py
├── tests/
├── requirements.txt
└── README.md
```

## 3. FastAPI Paradigm

Use clean separation:

```txt
API routers        → request/response only
Schemas            → Pydantic validation
Services           → business logic
Models             → SQLAlchemy tables
DB session          → dependency injection
Config              → environment variables
```

Avoid putting business logic directly inside route handlers.

## 4. Virtual Environment Setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Minimal `requirements.txt`:

```txt
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pydantic-settings
python-dotenv
email-validator
pytest
httpx
```

## 5. Local Run Command

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## 6. Backend Rules

- Use dependency-injected DB sessions.
- Use Pydantic request/response schemas.
- Use SQLAlchemy ORM models.
- Keep SQLite DB simple.
- Use service functions for appointment creation.
- Mark availability slot as booked after successful appointment.
- Generate confirmation code in backend.
- Send or log email after appointment creation.

## 7. Appointment Creation Logic

```txt
Validate doctor exists
↓
Validate selected availability exists and is not booked
↓
Create or reuse patient by email
↓
Create appointment with CONFIRMED status
↓
Mark availability as booked
↓
Send/log confirmation email
↓
Return appointment response
```

## 8. Email Service Modes

Use `SMTP_MODE`:

```txt
console → print email to terminal and create email_log as LOGGED
smtp    → send using SMTP config
```

Start with console mode for local development.

