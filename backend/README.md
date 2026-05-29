# Backend README

## 1. Project Overview

This backend is the FastAPI API for the doctor appointment booking app. The current codebase is a minimal foundation: it exposes a health check, loads settings from `.env`, and creates the SQLite schema on startup.

## 2. Tech Stack

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic
- `pydantic-settings`
- `python-dotenv`
- `pytest`

## 3. Folder Structure

```txt
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── router.py
│   │   └── health.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── database.py
│   ├── models/
│   │   └── doctor.py
│   └── schemas/
│       └── doctor.py
├── requirements.txt
└── README.md
```

## 4. Python Version Requirement

Use Python 3.12 or newer. The project docs prefer Python 3.12.

## 5. Virtual Environment Setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
```

## 6. Dependency Installation

```bash
cd backend
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 7. Environment Variables

Settings are loaded from `backend/.env` through `pydantic-settings`.

- `APP_NAME=Doctor Appointment API`
- `API_PREFIX=/api`
- `DATABASE_URL=sqlite:///./app.db`

These values are required by the backend settings loader.

## 8. Database Setup

The app creates tables on startup with `Base.metadata.create_all(bind=engine)`.

Database URL from `.env`:

```txt
sqlite:///./app.db
```

SQLite is configured with `check_same_thread=False` when the database URL starts with `sqlite`.

## 9. Run Development Server

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 4001
```

## 10. API Documentation URLs

When the server is running on port `4001`:

- Swagger UI: `http://localhost:4001/docs`
- ReDoc: `http://localhost:4001/redoc`
- OpenAPI JSON: `http://localhost:4001/openapi.json`

## 11. Common Development Commands

```bash
cd backend
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 4001
```

## 12. Troubleshooting Notes

- If `uvicorn` is not found, activate `.venv` first.
- If the app cannot open the database, confirm `DATABASE_URL` points to a valid SQLite file path.
- If the schema looks stale, delete the local `app.db` file and restart the server so the tables are recreated.
- If imports fail, make sure commands are run from the `backend/` directory.
