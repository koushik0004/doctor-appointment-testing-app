You are a senior backend engineer working on a spec-driven project.

PROJECT CONTEXT:
- Read docs/db-schema.md, docs/backend-spec.md, docs/architecture.md
- Follow .claude/coding-rules.md and fastapi-sqlite-skill.md

FEATURE:
feature-01-project-foundation.md

SCOPE:
- Setup FastAPI project structure
- Setup SQLite connection
- Setup base models and DB session
- Setup health check API

TECH STACK:
- FastAPI
- SQLite
- SQLAlchemy (simple ORM)
- Python with .venv

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

4. Create simple Doctor model (id, name, specialization, email)

5. Create health API:
   GET /health → returns {"status": "ok"}

CONSTRAINTS:
- Keep setup minimal
- No authentication
- No complex config
- Use env file for DB path

OUTPUT:
- Generate full code
- Mention all created files