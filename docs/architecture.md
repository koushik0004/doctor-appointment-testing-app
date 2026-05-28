# Architecture Specification

## 1. High-Level Architecture

```txt
Browser
  ↓
Next.js Frontend
  ↓ REST API
FastAPI Backend
  ↓ ORM
SQLite Database
  ↓
SMTP Email Provider / Local Email Logger
```

Future AI architecture:

```txt
Browser Chatbot
  ↓
Next.js Chat UI
  ↓
FastAPI AI endpoint
  ↓
LLM command parser
  ↓
Playwright browser automation agent
  ↓
Visible frontend navigation and appointment booking
```

## 2. Monorepo Structure

```txt
doctor-appointment-ai/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── lib/
│   ├── stores/
│   ├── styles/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── ai-agent/
│   └── future-placeholder.md
│
├── docs/
├── .claude/
├── AGENTS.md
└── README.md
```

## 3. Frontend Layer

Responsibilities:

- Render UI pages
- Manage route transitions
- Validate forms before API call
- Store selected doctor/slot in Zustand when useful
- Call backend APIs
- Display success/error states

Do not put database logic in frontend.

## 4. Backend Layer

Responsibilities:

- Expose REST APIs
- Validate payloads using Pydantic
- Persist records using SQLAlchemy
- Generate confirmation codes
- Send email confirmation
- Seed initial doctors and availability

Do not put UI-specific state in backend.

## 5. Database Layer

Use SQLite for v1.

Database file:

```txt
backend/app.db
```

For development simplicity, tables can be created using SQLAlchemy metadata at startup. Alembic can be added later if schema changes become frequent.

## 6. API Style

Use RESTful endpoints:

```txt
GET    /api/health
GET    /api/doctors
GET    /api/doctors/{doctor_id}
GET    /api/specialties
GET    /api/appointments
POST   /api/appointments
GET    /api/appointments/{appointment_id}
PATCH  /api/appointments/{appointment_id}/cancel
```

## 7. Environment Files

Frontend:

```txt
frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:4001/api
```

Backend:

```txt
backend/.env
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:3000
SMTP_MODE=console
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=no-reply@carenow.local
```

