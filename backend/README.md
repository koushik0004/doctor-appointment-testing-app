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
├── pyproject.toml
└── README.md
```

## 4. Python Version Requirement

Use Python 3.11, 3.12, or 3.13. Activate your conda environment before running `make setup`.

## 5. Virtual Environment Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

## 6. Dependency Installation

```bash
cd backend
source .venv/bin/activate
python -m ensurepip --upgrade
python -m pip install --no-build-isolation -e ".[dev]"
```

## 7. Environment Variables

Settings are loaded from `backend/.env` through `pydantic-settings`.

- `APP_NAME=Doctor Appointment API`
- `API_PREFIX=/api`
- `DATABASE_URL=sqlite:///./app.db`
- `CORS_ORIGINS=http://localhost:4002,http://127.0.0.1:4002`

These values are required by the backend settings loader.

## 8. Database Setup

The app creates tables on startup with `Base.metadata.create_all(bind=engine)`.

Database URL from `.env`:

```txt
sqlite:///./app.db
```

SQLite is configured with `check_same_thread=False` when the database URL starts with `sqlite`.

## 9. Run Development Server

From the repo root:

```bash
make dev
```

Use `make setup` first if you want to prepare both the backend and frontend dependencies explicitly.
Use `make stop` to stop both background servers.

## 10. API Documentation URLs

When the server is running on port `4001`:

- Swagger UI: `http://localhost:4001/docs`
- ReDoc: `http://localhost:4001/redoc`
- OpenAPI JSON: `http://localhost:4001/openapi.json`

## 11. Common Development Commands

```bash
make help
make setup
make dev
make stop
```

## 12. Troubleshooting Notes

- If `make setup` creates a venv with the wrong interpreter, remove `backend/.venv`, activate the conda env with Python 3.11, 3.12, or 3.13, and rerun `make setup`.
- If the app cannot open the database, confirm `DATABASE_URL` points to a valid SQLite file path.
- If the schema looks stale, delete the local `app.db` file and restart the server so the tables are recreated.
- If imports fail, make sure the backend virtual environment exists under `backend/.venv`.
