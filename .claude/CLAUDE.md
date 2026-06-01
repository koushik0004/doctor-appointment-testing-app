# CLAUDE.md

## Project Identity

You are working on a CareNow-style doctor appointment booking app.

Frontend:

- Next.js
- TypeScript
- Tailwind CSS
- SCSS
- Zustand
- React Hook Form
- Zod

Backend:

- FastAPI
- Python
- SQLite
- SQLAlchemy
- Pydantic
- `.venv`

## Current Development Priority

Build frontend, backend, and database first. Do not implement the AI chatbot or browser automation until the manual booking flow is complete.

## Spec-Driven Development Rule

Always work from these files:

- `docs/project-context.md`
- `docs/product-specification.md`
- `docs/architecture.md`
- `docs/feature-map.md`
- Relevant `docs/feature-*.md`

Before implementing a feature:

1. Read the feature spec.
2. Confirm API/data impact.
3. Implement minimal working version.
4. Update feature status.
5. Keep code simple.

## Coding Behavior

- Do not over-engineer.
- Do not add authentication in v1.
- Do not add payments in v1.
- Do not add admin dashboard in v1.
- Keep SQLite schema simple.
- Prefer readable code over clever abstractions.
- Add comments only where logic is not obvious.

## Done Definition

A feature is done only when:

- UI works.
- API works.
- DB persistence works if required.
- Validation works.
- Basic manual test is possible.

