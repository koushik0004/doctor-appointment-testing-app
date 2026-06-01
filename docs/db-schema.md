# Database Schema Specification

## 1. doctors

Stores clinic doctors.

| Column | Type | Required | Notes |
|---|---|---:|---|
| id | integer | yes | Primary key |
| name | string | yes | Example: Dr. Sarah Jenkins |
| slug | string | yes | URL-safe identifier |
| specialty | string | yes | Example: Cardiology |
| title | string | no | Example: Senior Cardiologist |
| rating | float | yes | Example: 4.9 |
| review_count | integer | yes | Example: 128 |
| clinic_name | string | yes | Example: CareNow Central Clinic |
| location | string | yes | City or area |
| address | string | no | Full address |
| fee_min | integer | no | Example: 120 |
| fee_max | integer | no | Example: 200 |
| languages | string | no | Comma-separated for v1 |
| image_url | string | no | Static image path or URL |
| is_active | boolean | yes | Default true |

## 2. doctor_availability

Stores simple available date/time slots.

| Column | Type | Required | Notes |
|---|---|---:|---|
| id | integer | yes | Primary key |
| doctor_id | integer | yes | FK to doctors |
| available_date | date | yes | Appointment date |
| start_time | string | yes | HH:MM format |
| end_time | string | yes | HH:MM format |
| appointment_type | string | yes | IN_PERSON or TELEMEDICINE |
| is_booked | boolean | yes | Default false |

## 3. patients

Stores patient details.

| Column | Type | Required | Notes |
|---|---|---:|---|
| id | integer | yes | Primary key |
| full_name | string | yes | Patient name |
| email | string | yes | Used for confirmation |
| phone | string | no | Optional in v1 |
| created_at | datetime | yes | Creation timestamp |

## 4. appointments

Stores appointments.

| Column | Type | Required | Notes |
|---|---|---:|---|
| id | integer | yes | Primary key |
| confirmation_code | string | yes | Example: CN-99210-XB |
| doctor_id | integer | yes | FK to doctors |
| patient_id | integer | yes | FK to patients |
| availability_id | integer | no | FK to doctor_availability |
| appointment_date | date | yes | Selected date |
| start_time | string | yes | Selected start time |
| end_time | string | no | Optional calculated value |
| appointment_type | string | yes | IN_PERSON or TELEMEDICINE |
| health_description | text | no | Visit reason |
| status | string | yes | CONFIRMED by default |
| created_at | datetime | yes | Creation timestamp |
| cancelled_at | datetime | no | Only for cancellation |

## 5. email_logs

Optional but useful in development.

| Column | Type | Required | Notes |
|---|---|---:|---|
| id | integer | yes | Primary key |
| appointment_id | integer | yes | FK to appointments |
| to_email | string | yes | Recipient |
| subject | string | yes | Email subject |
| status | string | yes | SENT or FAILED or LOGGED |
| error_message | text | no | Failure details |
| created_at | datetime | yes | Timestamp |

## 6. Seed Data

Seed at least four doctors:

```txt
Dr. Sarah Jenkins - Cardiology
Dr. Marcus Chen - General Practice / Pediatrics
Dr. Elena Rodriguez - Dermatology
Dr. James Wilson - Internal Medicine
```

Seed several availability slots for each doctor.

