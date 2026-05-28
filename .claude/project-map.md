# Project Map

## Root

```txt
doctor-appointment-ai/
├── frontend/
├── backend/
├── ai-agent/
├── docs/
├── .claude/
├── AGENTS.md
└── README.md
```

## Frontend Map

```txt
frontend/app/page.tsx
```

Home page.

```txt
frontend/app/doctors/page.tsx
```

Doctor listing and filters.

```txt
frontend/app/appointments/new/page.tsx
```

Appointment booking page.

```txt
frontend/app/appointments/[appointmentId]/confirmation/page.tsx
```

Booking confirmation page.

```txt
frontend/features/doctors/
```

Doctor API calls, types, and feature components.

```txt
frontend/features/appointments/
```

Appointment API calls, Zod schema, types, and form components.

```txt
frontend/stores/booking-store.ts
```

Zustand store for selected doctor/date/time.

## Backend Map

```txt
backend/app/main.py
```

FastAPI app creation and middleware.

```txt
backend/app/api/
```

API route files.

```txt
backend/app/models/
```

SQLAlchemy models.

```txt
backend/app/schemas/
```

Pydantic schemas.

```txt
backend/app/services/
```

Business logic.

```txt
backend/app/db/
```

Database session, base model, seed logic.

## Documentation Map

```txt
docs/product-specification.md
```

Full product spec.

```txt
docs/feature-map.md
```

Feature status and order.

```txt
docs/api-spec.md
```

REST API contract.

```txt
docs/db-schema.md
```

SQLite schema.

