# AGENTS.md

Use this file for ChatGPT/Codex-style coding agents.

## Project Summary

This is a doctor appointment booking application with a Next.js frontend, FastAPI backend, and SQLite database.

The first version must focus on the manual booking flow only. AI chatbot and browser automation are future features.

## Architecture Rules

- Frontend is inside `frontend/`.
- Backend is inside `backend/`.
- Specs are inside `docs/`.
- Claude-specific memory is inside `.claude/`.
- Do not mix frontend and backend logic.

## Frontend Rules

- Use Next.js App Router.
- Use TypeScript.
- Use Tailwind CSS.
- Use SCSS only for global utilities or complex style grouping.
- Use Zustand only for simple booking state.
- Use React Hook Form and Zod for forms.
- Keep components small.

## Backend Rules

- Use FastAPI standard routing style.
- Use SQLAlchemy ORM.
- Use SQLite for v1.
- Use Pydantic schemas.
- Use services for business logic.
- Use `.venv` for Python dependencies.

## Development Rule

Implement one feature at a time. Before coding, check `docs/feature-map.md` and the relevant feature spec file.

