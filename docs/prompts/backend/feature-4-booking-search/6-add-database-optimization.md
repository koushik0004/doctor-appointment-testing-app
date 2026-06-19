TASK: Optimize Appointment Search Queries

Review appointment search implementation.

Add appropriate indexes:

Patient.email
Patient.phone
Patient.full_name

Generate migration if project supports migrations.

Requirements:

- No schema breaking changes
- Backward compatible
- Existing booking feature must continue working

Create:

docs/analysis/feature-4/feature-4-search-performance.md

containing:

- indexes added
- expected query improvements