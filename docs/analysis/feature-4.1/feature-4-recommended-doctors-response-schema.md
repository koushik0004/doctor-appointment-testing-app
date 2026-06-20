# Feature 4.1 Recommended Doctors Response Schemas

## Scope

This document defines the response schemas only for the recommended-doctors endpoint.

No service logic, route logic, or repository logic is included here.

## Schema Models

### `RecommendedDoctorResponse`

This model represents one recommended doctor item.

Fields:

- `doctor_id: int`
- `doctor_name: str`
- `specialty: str`
- `rating: float`
- `review_count: int`
- `next_available_date: date`
- `next_available_slot: str`
- `profile_image: str`
- `clinic_name: str`
- `recommendation_reason: RecommendationReason`

### `RecommendationReason`

Enum values:

- `same_specialty`
- `related_specialty`

Notes:

- `doctor_id` should map to the doctor primary key
- `doctor_name` should map to the doctor display name
- `rating` and `review_count` are used for ranking and should be returned as numeric values
- `next_available_date` should be serialized as an ISO date
- `next_available_slot` should be returned as a user-facing time label or slot string
- `profile_image` should contain the avatar or image path used by the UI

### `RecommendedDoctorsResponse`

This model represents the full response for the endpoint.

Fields:

- `appointment_id: int`
- `specialty: str`
- `recommended_doctors: list[RecommendedDoctorResponse]`

## Response Shape

```json
{
  "appointment_id": 123,
  "specialty": "General Physician",
  "recommended_doctors": [
    {
      "doctor_id": 45,
      "doctor_name": "Dr. Aisha Khan",
      "specialty": "General Practice",
      "rating": 4.9,
      "review_count": 171,
      "next_available_date": "2026-06-20",
      "next_available_slot": "06:15 PM",
      "profile_image": "/avatars/doctor-sarah.svg",
      "clinic_name": "Riverside Family Clinic",
      "recommendation_reason": "same_specialty"
    }
  ]
}
```

## Validation Expectations

These schemas should support the following response guarantees:

- `appointment_id` is always present for successful responses
- `specialty` is always present for successful responses
- `recommended_doctors` is always present, even when empty
- each recommended doctor item must contain all listed fields

## Design Notes

- Keep the response schema flat and explicit.
- Do not introduce extra wrapper objects.
- Do not include appointment details beyond the appointment id and specialty.
- Keep this schema separate from any future request schema, since this endpoint is path-driven.
