---
name: refresh-test-data
description: Detect schema changes after recent commits, Validate all existing demo data against the current implementation, Remove or repair only invalid demo records (never user data), Update knowledge-source examples to reflect new workflows, Produce a data health report
---

# Refresh Test Data Skill

You are maintaining the Doctor Appointment AI Assistant project.

Your responsibility is to keep existing demo data synchronized with the latest implementation.

Never assume anything.

Always inspect the project first.

---

## Step 1

Read

AGENTS.md

README.md

project-memory

report-index

implementation reports

workflow reports

feature reports

architecture reports

knowledge source

completion reports

execution status

Determine

• implemented features

• completed workflows

• supported entities

• validation rules

• business rules

---

## Step 2

Inspect current database schema.

Compare it with existing data.

Detect

missing fields

invalid values

broken relationships

invalid appointment states

invalid schedules

duplicate records

orphan records

invalid availability

past appointments created as future demo data

---

## Step 3

Repair demo data only.

Never modify production-like records.

Never touch user-created records.

---

## Step 4

If newly implemented features require demo data

Insert only missing data.

Maximum new rows

10

---

## Step 5

Synchronize knowledge source.

Update

FAQs

sample conversations

supported workflows

business examples

only when required.

---

## Step 6

Generate

docs/reports/test-data-health-report.md

Include

Schema changes detected

Broken demo records

Repairs performed

Rows inserted

Rows skipped

Knowledge updates

Remaining issues

---

Rules

Never delete user data.

Never overwrite good records.

Never insert duplicates.

Always use existing services or repository layer.

Be idempotent.