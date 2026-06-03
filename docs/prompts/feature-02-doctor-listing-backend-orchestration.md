# FEATURE-02 BACKEND ORCHESTRATION

# Doctor Listing & Filters

# FastAPI + SQLite

---

## ORCHESTRATION MODE

This file is designed for Codex CLI agent orchestration.

Execution strategy:

PHASE 1 → Analyze Existing Backend

PHASE 2 → Doctor Domain Model

PHASE 3 → Doctor Schemas

PHASE 4 → Doctor Seed Data

PHASE 5 → Repository Layer

PHASE 6 → Service Layer

PHASE 7 → Doctor APIs

PHASE 8 → Router Registration

PHASE 9 → Testing

PHASE 10 → Architecture Review

IMPORTANT RULES

* Execute phases sequentially.
* Complete current phase before next phase.
* Reuse existing project patterns.
* Never redesign project architecture.
* Never modify unrelated features.
* Keep implementation minimal.
* Keep SQLite compatible.
* Follow spec-driven development.

Reference files:

docs/project-context.md
docs/product-specification.md
docs/feature-02-doctor-listing.md

---

# PHASE 1

# BACKEND ANALYSIS

GOAL

Understand current backend foundation.

TASKS

1. Inspect backend folder structure.

2. Identify:

* FastAPI app initialization
* Router registration
* SQLAlchemy setup
* Session management
* Existing models
* Existing schemas

3. Produce implementation plan.

OUTPUT

Create:

docs/analysis/feature-02-analysis.md

Contents:

* existing reusable components
* required files
* required modifications
* implementation checklist

STOP AFTER COMPLETION

---

# PHASE 2

# DOCTOR MODEL

GOAL

Create doctor persistence model.

TASKS

Create or update Doctor model.

Required fields:

id
name
specialty
rating
review_count
clinic_name
location
consultation_fee_min
consultation_fee_max
next_available_slot
appointment_types
languages
description
image_url

REQUIREMENTS

* SQLite compatible
* SQLAlchemy ORM
* specialty index
* reusable for future appointment booking

DO NOT

* create APIs
* create repositories
* create services

OUTPUT

Model implementation only.

STOP AFTER COMPLETION

---

# PHASE 3

# DOCTOR SCHEMAS

GOAL

Create API response schemas.

TASKS

Create:

DoctorResponse

DoctorListResponse

DoctorResponse fields:

id
name
specialty
rating
review_count
clinic_name
location
consultation_fee_min
consultation_fee_max
next_available_slot
appointment_types
languages
description
image_url

DoctorListResponse:

{
"items": [],
"total": 0
}

REQUIREMENTS

* Pydantic
* Existing project conventions

DO NOT

* modify routers
* modify DB

STOP AFTER COMPLETION

---

# PHASE 4

# SEED DATA

GOAL

Create initial doctor dataset.

TASKS

Insert 10 doctors.

Required specialties:

General Practice
Cardiology
Pediatrics
Dermatology
Internal Medicine

Required appointment types:

IN_PERSON
TELEMEDICINE

REQUIREMENTS

* idempotent seed script
* avoid duplicate inserts
* realistic sample data

OUTPUT

Seed implementation only.

STOP AFTER COMPLETION

---

# PHASE 5

# REPOSITORY

GOAL

Create doctor data access layer.

TASKS

Implement:

get_doctors()

get_doctors_by_filters()

get_doctor_by_id()

Supported filters:

specialty
appointment_type

REQUIREMENTS

* SQLAlchemy queries
* ORM objects returned
* SQLite compatible

DO NOT

* add business logic
* add router code

STOP AFTER COMPLETION

---

# PHASE 6

# SERVICE LAYER

GOAL

Create doctor business layer.

TASKS

Implement:

list_doctors()

get_doctor()

Responsibilities:

* validate inputs
* invoke repository
* map responses if needed

DO NOT

* create API routes

STOP AFTER COMPLETION

---

# PHASE 7

# API IMPLEMENTATION

GOAL

Implement doctor APIs.

REQUIRED ENDPOINTS

GET /api/doctors

Query Parameters:

specialty
appointment_type

Example:

/api/doctors?specialty=Cardiology&appointment_type=IN_PERSON

Response:

{
"items": [...],
"total": 5
}

---

GET /api/doctors/{doctor_id}

Response:

DoctorResponse

VALIDATION

doctor not found:

404

empty list:

{
"items": [],
"total": 0
}

REQUIREMENTS

* FastAPI router
* Response models
* Dependency injection

STOP AFTER COMPLETION

---

# PHASE 8

# ROUTER REGISTRATION

GOAL

Expose doctor APIs.

TASKS

Register router.

Prefix:

/api/doctors

Verify:

GET /health

still works.

STOP AFTER COMPLETION

---

# PHASE 9

# TESTING

GOAL

Validate implementation.

CREATE

docs/testing/feature-02-test-report.md

Cover:

1. Happy path

GET /api/doctors

2. Specialty filtering

3. Appointment type filtering

4. Combined filtering

5. Invalid doctor id

6. Empty results

Provide:

request
expected response
actual response

STOP AFTER COMPLETION

---

# PHASE 10

# FINAL REVIEW

GOAL

Perform architecture review.

CHECK

* API design
* SQLAlchemy usage
* SQLite compatibility
* schema design
* naming conventions
* code duplication
* future compatibility with appointments

CREATE

docs/reviews/feature-02-review.md

Format

PASS
WARNING
FAIL

for each category.

If issue found:

* exact file
* exact fix

STOP

Feature complete.
