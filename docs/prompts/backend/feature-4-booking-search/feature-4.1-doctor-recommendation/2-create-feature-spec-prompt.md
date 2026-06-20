TASK: Create Recommended Doctors Backend Specification

Create:

docs/analysis/feature-4.1/feature-4-recommended-doctors-spec.md

Business Requirement:

After viewing an appointment:

- identify appointment doctor
- identify doctor's specialty

Return recommended doctors having:

- same specialty
- active status
- available for booking

Sort priority:

1. highest rating
2. most reviews
3. doctor name

Exclude:

- currently selected doctor

Limit:

maximum 5 doctors

Document:

- API contract
- validation rules
- response structure
- edge cases

DO NOT IMPLEMENT.