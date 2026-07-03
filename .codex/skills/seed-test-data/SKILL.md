---
name: seed-test-data
description: Read the current impl reports and insert max 10 rows of realistic test data for implemented features. Do not insert duplicates or invalid data.
---

# Seed Test Data

You are the Test Data Maintenance Agent for the Doctor Appointment AI Assistant.

Your responsibility is to continuously build and maintain a realistic business dataset for every IMPLEMENTED feature.

This skill is intended to be executed repeatedly throughout the project lifecycle.

Never redesign the application.

Never change business logic.

Never modify existing implementation.

Your responsibility is ONLY to inspect the project and insert valid demo data.

--------------------------------------------------
STEP 1 — Discover Current Implementation
--------------------------------------------------

Inspect the project before making any decision.

Read every available project document including (if present):

- AGENTS.md
- README.md
- report-index.md
- execution-status.json
- project-memory.md
- implementation reports
- feature reports
- workflow reports
- architecture reports
- knowledge-source documents
- completion reports
- database migration history

Determine

• implemented features
• completed workflows
• supported APIs
• business entities
• validation rules
• required fields
• relationships
• lookup/reference tables

Never assume anything.

--------------------------------------------------
STEP 2 — Inspect Database
--------------------------------------------------

Inspect the current database.

Discover

Tables

Columns

Relationships

Constraints

Indexes

Existing row counts

Current demo data

Existing user data

Never delete anything.

--------------------------------------------------
STEP 3 — Determine Coverage Requirements
--------------------------------------------------

Build a coverage map based on IMPLEMENTED FEATURES.

Example

Doctor Listing

↓

Requires Doctors

Booking

↓

Requires

Doctors

Patients

Availability

Appointments

Cancellation

↓

Requires cancelled appointments

Confirmation

↓

Requires confirmed appointments

Doctor Search

↓

Requires diverse doctors

Patient Search

↓

Requires diverse patients

Knowledge Source

↓

Requires realistic examples

Conversation Testing

↓

Requires realistic business scenarios

Never create data for unfinished features.

--------------------------------------------------
STEP 4 — Minimum Coverage Targets
--------------------------------------------------

Maintain approximately

Doctors

10

Patients

20

Appointments

30

Availability Slots

100

Specializations

All implemented specializations

Clinic Locations

Enough to support implemented UI

Appointment Types

Every implemented type

Conversation Examples

Enough for implemented AI workflows

Knowledge Source Examples

Enough for implemented features

These are TARGETS.

Do NOT try to reach them in one execution.

--------------------------------------------------
STEP 5 — Progressive Seeding
--------------------------------------------------

Never insert more than

10

records during one execution.

Instead

Inspect current counts.

Determine the biggest coverage gaps.

Prioritize in this order

1. Doctors
2. Availability
3. Patients
4. Appointments
5. Supporting lookup tables

Example

Current

Doctors = 4

Target = 10

Insert

6? NO

Insert

4

Next execution

Doctors = 8

Insert

2

Continue until target reached.

Running this skill multiple times should gradually build the dataset.

--------------------------------------------------
STEP 6 — Generate High Quality Data
--------------------------------------------------

Generate realistic business data.

Doctors

Real names

Different genders

Different specialties

Different consultation fees

Different years of experience

Different education

Languages

Clinic addresses

Working schedules

Patients

Real names

Emails

Phone numbers

Age

Gender

Health descriptions

Appointments

Future dates only

Available slots only

Mix of

Confirmed

Pending

Cancelled

Completed

Only if those statuses exist.

Availability

Working hours

Breaks

Weekdays

Weekends

Realistic slot distribution.

--------------------------------------------------
STEP 7 — Duplicate Prevention
--------------------------------------------------

Before inserting

Search using

Doctor email

Doctor phone

Doctor license

Patient email

Patient phone

Appointment uniqueness

Availability uniqueness

Never create duplicates.

Running this skill repeatedly must always be safe.

--------------------------------------------------
STEP 8 — Business Rule Validation
--------------------------------------------------

Respect

Foreign keys

Unique constraints

Required fields

Validation rules

Booking rules

Availability rules

Business APIs

Repository layer

Service layer

Prefer existing application services instead of raw SQL.

Never bypass validation.

--------------------------------------------------
STEP 9 — Knowledge Source Synchronization
--------------------------------------------------

Inspect

Knowledge source

FAQ

Prompt examples

Conversation examples

Business examples

If new demo data improves AI responses

Update them.

Avoid duplicates.

--------------------------------------------------
STEP 10 — Reporting
--------------------------------------------------

Generate

docs/reports/test-data-report.md

Include

Execution timestamp

Implemented features discovered

Coverage analysis

Current row counts

Rows inserted

Rows skipped

Duplicate detection

Business validation

Knowledge source updates

Current coverage percentage

Recommended next execution

--------------------------------------------------
SUCCESS CRITERIA
--------------------------------------------------

After execution

✓ Every implemented feature moves closer to complete test coverage.

✓ Dataset grows gradually.

✓ Maximum 10 inserted rows.

✓ No duplicate records.

✓ No invalid business data.

✓ No broken relationships.

✓ Safe to execute repeatedly.

✓ Uses existing services whenever possible.
