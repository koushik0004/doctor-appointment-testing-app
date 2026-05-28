# Coding Rules

## General

- Implement one feature at a time.
- Keep files small and readable.
- Prefer explicit names.
- Avoid premature abstraction.
- Avoid adding libraries unless required by the spec.

## Frontend

- Use TypeScript everywhere.
- Keep page files thin.
- Move reusable UI to `components/`.
- Move feature-specific logic to `features/`.
- Use React Hook Form for appointment forms.
- Use Zod for validation.
- Use Zustand only for simple booking selection state.
- Use Tailwind for layout and common styling.
- Use SCSS only for global utilities or complex reusable style blocks.

## Backend

- Use FastAPI routers.
- Keep route handlers thin.
- Use service classes/functions for business logic.
- Use SQLAlchemy models for DB.
- Use Pydantic schemas for request and response.
- Use dependency-injected DB sessions.
- Use `.venv` for backend dependencies.

## Database

- Keep SQLite schema simple.
- Do not model complex schedules in v1.
- Use `doctor_availability` slots.
- Mark slot as booked after appointment creation.

## Testing

- Backend tests have priority.
- Add tests for appointment creation and slot booking.
- Manual UI testing is acceptable for first frontend pass.

