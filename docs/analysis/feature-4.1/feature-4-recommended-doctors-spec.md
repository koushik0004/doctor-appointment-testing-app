# Feature 4.1 Recommended Doctors Backend Specification

## Goal

When a user views an appointment, the backend should return a small list of recommended doctors based on the specialty of the appointment doctor.

## Business Requirement

Given an `appointment_id`, the backend must:

- identify the appointment
- identify the appointment doctor
- read the doctor specialty
- return up to 5 recommended doctors

Recommended doctors must:

- have the same specialty as the appointment doctor
- be active
- be available for booking

Recommended doctors must be sorted by:

1. highest rating
2. most reviews
3. doctor name

The currently selected doctor must be excluded.

## API Contract

### Endpoint

```txt
GET /api/appointments/{appointment_id}/recommended-doctors
```

### Path Parameters

- `appointment_id` - required integer identifier of the appointment being viewed

### Success Response

```json
{
  "appointment_id": 123,
  "specialty": "General Practice",
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

### Empty Result Response

If no recommendations are available, the API should still return `200 OK` with an empty list.

```json
{
  "appointment_id": 123,
  "specialty": "General Practice",
  "recommended_doctors": []
}
```

## Response Structure

### Top-Level Fields

- `appointment_id` - the appointment being viewed
- `specialty` - specialty of the appointment doctor
- `recommended_doctors` - list of recommended doctor records

### Recommended Doctor Fields

- `doctor_id` - doctor primary key
- `doctor_name` - doctor display name
- `specialty` - doctor specialty
- `rating` - doctor rating used for ranking
- `review_count` - doctor review count used for tie-breaking
- `next_available_date` - first available booking date, if available
- `next_available_slot` - first available booking slot label, if available
- `profile_image` - doctor avatar or profile image path
- `clinic_name` - clinic display name
- `recommendation_reason` - `same_specialty` or `related_specialty`

## Validation Rules

- `appointment_id` must be a positive integer
- if the appointment does not exist, return `404`
- if the appointment exists but its doctor cannot be loaded, return `404`
- if the source doctor is inactive, the request should still resolve the appointment, but recommendations should be based on the appointment doctor record only when it can be loaded
- whitespace trimming is not needed for the path parameter
- no query parameters are required for this endpoint

## Availability Rules

The recommendation list must include only doctors that are available for booking.

In the current backend, availability should be determined by the booking schedule path rather than the `next_available_slot` text field alone.

Recommended availability rule:

- a doctor is eligible only if the backend can resolve at least one future bookable slot for that doctor
- the implementation should reuse the existing availability/service layer instead of inventing a new availability source

If the system cannot determine future availability for a doctor, that doctor should be excluded from the recommendation list.

## Sorting and Limiting Rules

After all filters are applied, sort candidates by:

1. `rating DESC`
2. `review_count DESC`
3. `doctor_name ASC`

Then limit the response to at most 5 doctors.

## Edge Cases

- appointment not found
- appointment doctor not found
- appointment doctor specialty is empty or invalid
- no other active doctors share the same specialty
- all same-specialty doctors are currently unavailable for booking
- only the current doctor matches the specialty
- fewer than 5 eligible doctors exist
- duplicate rating and review count values require deterministic name-based ordering

## Reusable Backend Inputs

The feature should reuse existing backend data and services:

- appointment lookup by id
- doctor lookup by id
- doctor specialty field
- doctor rating and review count fields
- active doctor filtering
- availability/service logic used by booking flow

## Non-Goals

- do not change the appointment creation workflow
- do not add AI-based recommendation logic
- do not add related-specialty fallback in v1
- do not change existing doctor list or availability endpoints

## Implementation Notes

- keep recommendation logic in the service layer
- keep route logic thin
- avoid duplicating doctor lookup logic in the API layer
- use the appointment as the entry point for recommendation resolution
- return an empty list rather than an error when there are simply no eligible recommendations
