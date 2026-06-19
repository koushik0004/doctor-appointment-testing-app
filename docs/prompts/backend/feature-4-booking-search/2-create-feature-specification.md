TASK: Create Feature 4 Specification

Create:

docs/analysis/feature-4/feature-4-booking-search-spec.md

Business Requirements:

A patient can search appointments using:

- email
- phone number
- full name

Search should return:

- appointment id
- patient name
- patient email
- patient phone
- doctor name
- specialty
- appointment date
- appointment time
- appointment type
- booking status

Status values:

- booked
- completed
- cancelled

Rules:

- Case insensitive search
- Partial search supported for name
- Exact search for email
- Exact search for phone

Generate:

1. User flow
2. API contracts
3. DB requirements
4. Validation rules
5. Error responses

DO NOT IMPLEMENT.