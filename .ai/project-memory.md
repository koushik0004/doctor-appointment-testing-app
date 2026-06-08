# Project Memory

## Current Feature

Feature 02 - Doctor Listing and Filters

## Completed

✓ Backend analysis
✓ Doctor ORM model
✓ Doctor schemas
✓ Seed data
✓ Repository layer
✓ Service layer
✓ Doctor APIs
✓ Router registration
✓ API validation

## Remaining

□ Frontend backend integration for the doctor listing screen
□ Optional pagination/search expansion if the product spec requires it

## Backend Decisions

- Use SQLite-compatible ORM fields for appointment types and languages
- Seed 10 doctors with idempotent startup seeding
- Keep doctor list filtering in the repository/service split

## Routes

/api/health
/api/doctors
/api/doctors/{doctor_id}
