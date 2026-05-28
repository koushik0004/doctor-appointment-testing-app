# Backend Instructions

## Python Environment

* Always create venv before install
* Store dependencies in requirements.txt

## FastAPI Structure

* api/
* services/
* models/
* schemas/

## Database

* Use SQLite
* Use Alembic migrations

## API Rules

* No DB queries inside route handlers
* Use dependency injection

## Testing

* Use pytest
* Add API tests for all endpoints
