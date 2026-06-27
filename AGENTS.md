# AGENTS.md

Use this file for ChatGPT/Codex-style coding agents.

## Project Summary

This is a doctor appointment booking application with a Next.js frontend, FastAPI backend, and SQLite database.

The current version focuses on the manual booking flow. AI chatbot, browser automation, advanced AIML workflows, and assistant-driven booking are future or evolving features.

## Repository Structure

* Frontend: `frontend/`
* Backend: `backend/`
* Specs and project docs: `docs/`
* Reports: `docs/reports/`
* Claude-specific files: `.claude/`

Do not mix frontend and backend logic.

## Startup Context Rule

Before doing any work, read only these files if they exist:

1. `docs/ai-content/manifest.yaml`
2. `docs/ai-content/session-context.md`
3. `docs/ai-content/current-task.md`
4. `docs/ai-content/important-files.md`
5. `docs/ai-content/report-index.md`

Read `docs/ai-content/feature-map.md` only when the task needs feature-to-file mapping.

Do not scan the full repository unless explicitly requested.

## Report Loading Rule

Do not read full report files automatically.

Use `docs/ai-content/report-index.md` first.

Read a full report from `docs/reports/` only when:

* the task directly matches that report topic
* the report-index says it is required
* implementation is blocked without deeper context
* the user explicitly asks to use that report

Prefer report summaries over full reports to reduce token usage.

## Task Resume Rule

For unfinished work, always check:

* `docs/ai-content/current-task.md`
* files listed under "Required Files for This Task"

Continue from the recorded status. Do not restart analysis from scratch unless the current-task file is outdated.

## Context Update Rule

After completing a feature, defect fix, redesign, or major refactor, update:

* `docs/ai-content/current-task.md`
* `docs/ai-content/feature-map.md`
* `docs/ai-content/important-files.md`
* `docs/ai-content/session-context.md`
* `docs/ai-content/report-index.md` if reports changed

Keep `docs/ai-content/session-context.md` compact.

## Architecture Rules

* Use feature-based organization where possible.
* Keep frontend, backend, API, DB, and AIML logic separated.
* Prefer small, focused files.
* Do not introduce new architecture patterns without updating docs.
* Before coding, check the relevant feature spec and feature-map.

## Frontend Rules

* Use Next.js App Router.
* Use TypeScript.
* Use Tailwind CSS.
* Use SCSS only for global utilities or complex style grouping.
* Use Zustand only for simple shared state.
* Use React Hook Form and Zod for forms.
* Keep components small and reusable.
* Avoid duplicating UI logic across pages.

## Backend Rules

* Use FastAPI standard routing style.
* Use SQLAlchemy ORM.
* Use SQLite for v1.
* Use Pydantic schemas.
* Use services for business logic.
* Use `.venv` for Python dependencies.
* Keep route handlers thin.
* Put business rules inside service files.

## Development Rules

* Implement one feature at a time.
* Read only task-relevant files.
* Do not perform broad rewrites unless requested.
* Preserve existing working behavior unless redesign is explicitly requested.
* When redesigning an existing feature, first identify existing files from `docs/feature-map.md`.
* Keep changes traceable and update docs after meaningful changes.

## Token Optimization Rule

Use this priority order for context:

1. `docs/ai-content/manifest.yaml`
2. `docs/ai-content/current-task.md`
3. `docs/ai-content/session-context.md`
4. `docs/ai-content/important-files.md`
5. `docs/ai-content/report-index.md`
6. `docs/ai-content/feature-map.md` when feature mapping is needed
7. task-specific source files
8. full reports only if required

Avoid reading large reports, generated files, build folders, dependency folders, or unrelated feature files.

Ignore:

* `node_modules/`
* `.next/`
* `dist/`
* `build/`
* `coverage/`
* `.venv/`
* `__pycache__/`
* `.git/`
