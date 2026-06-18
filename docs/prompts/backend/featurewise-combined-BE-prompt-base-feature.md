You are a senior backend engineer working on a spec-driven project.

PROJECT CONTEXT:
- Read docs from /docs (not the /docs/prompts) and .claude folder before implementation
- Follow spec-driven development strictly
- Do NOT assume anything outside spec
- Keep implementation simple and production-ready
- This time only focus on BE part not the FE part

FEATURE:
feature-01-project-foundation.md

SCOPE:
- Only implement what is defined in this feature
- Do NOT jump to future features

TECH STACK:
- FastAPI
- SQLite
- SQLAlchemy
- Python (.venv)

TASK:
1. Create backend folder structure:
   - app/
     - main.py
     - core/
     - db/
     - models/
     - schemas/
     - api/

2. Setup SQLite connection using SQLAlchemy

3. Create base DB session

4. Create Doctor model

5. Create health API:
   GET /health → {"status": "ok"}

CONSTRAINTS:
- Follow .claude/coding-rules.md
- Keep code minimal and modular
- No over-engineering

OUTPUT:
- Generate code only
- Mention created files