# Project Map

## Current Architecture

```txt
Browser
  -> Next.js App Router frontend (`frontend/`)
  -> local proxy API routes (`frontend/app/api/[...path]/route.ts`)
  -> FastAPI backend (`backend/app/`)
  -> SQLite database (`backend/app.db` by default)
```

The repository is a two-app monorepo centered on the manual doctor-booking flow, with an additional AI chat surface already present in both frontend and backend.

## Top-Level Areas

### `frontend/`

Next.js 15 + React 19 + TypeScript frontend.

- `app/`
  - Route entry points and the API proxy layer.
  - Main user-facing routes:
    - `/` home
    - `/doctors`
    - `/appointments`
    - `/appointments/search`
    - `/appointments/confirmation`
- `components/`
  - Shared UI grouped by domain-like areas.
  - `components/doctors/` contains the doctor listing page shell and filtering UI.
  - `components/layout/` contains header, footer, and global AI widget mount.
- `features/`
  - Feature-specific API clients, types, hooks, validation, and booking components.
  - `features/doctors/` owns doctor-list API mapping and doctor domain types.
  - `features/appointments/` owns booking/search API mapping, schemas, hooks, and most booking UI.
- `lib/`
  - Shared utilities plus the AI widget implementation.
  - `lib/api-client.ts` is the common fetch wrapper used by frontend features.
  - `lib/ai-widget/` contains chat UI, services, adapters, styles, and shared widget types.
- `stores/`
  - Zustand cross-route booking state.
- `styles/`
  - Global SCSS utilities and design tokens.
- `public/avatars/`
  - Doctor avatar assets.

### `backend/`

FastAPI + SQLAlchemy + SQLite API application.

- `app/main.py`
  - Creates the FastAPI app, configures CORS, initializes the DB on startup.
- `app/api/`
  - Thin HTTP route layer.
  - Exposes health, doctors, availability, appointments, and chat endpoints.
- `app/services/`
  - Business logic layer.
  - Booking validation, availability generation, doctor search/filtering, appointment search, and rule-based chat live here.
- `app/repositories/`
  - Data access helpers for doctors, appointments, availability, and patients.
- `app/models/`
  - SQLAlchemy models for doctors, availability, appointments, and patients.
- `app/schemas/`
  - Pydantic request/response contracts.
- `app/db/`
  - Engine/session setup and startup seeding.
- `alembic/`
  - Migration history exists, but startup still uses `create_all` plus seeding.
- `tests/`
  - API and service coverage for doctors, appointments, search, availability, chat intent, and entity extraction.
- `scripts/seed_db.py`
  - Local seed helper.

### `docs/`

Project specs, architecture notes, prompts, reports, reviews, and AI context files.

- `ai-content/`
  - Lightweight startup context for coding agents.
- `reports/`
  - Deep-dive implementation and validation reports by feature area.
- Feature specs such as `feature-02-doctor-listing.md`, `feature-03-appointment-booking.md`, and `feature-04-confirmation-email.md`.

## Request/Data Flow

### Frontend to backend

1. UI pages call feature API helpers in `frontend/features/*/api.ts`.
2. Those helpers use `frontend/lib/api-client.ts`.
3. Requests hit the Next.js catch-all proxy route in `frontend/app/api/[...path]/route.ts`.
4. The proxy forwards requests to the FastAPI backend using `BACKEND_API_BASE_URL`.

### Backend processing

1. `backend/app/api/*` routes validate and dispatch requests.
2. `backend/app/services/*` enforce business rules.
3. `backend/app/repositories/*` query or mutate SQLite through SQLAlchemy sessions.
4. Responses are serialized by `backend/app/schemas/*`.

## Notes About Current State

- The codebase is beyond pure foundation status; live doctor listing, booking, booking confirmation, appointment search, and AI chat are implemented.
- The global AI widget is mounted in the root layout, but it uses a noop navigation adapter while consuming the live backend chat API.
- The backend seeds doctor data automatically at startup and rebuilds the doctors table if required columns are missing.
