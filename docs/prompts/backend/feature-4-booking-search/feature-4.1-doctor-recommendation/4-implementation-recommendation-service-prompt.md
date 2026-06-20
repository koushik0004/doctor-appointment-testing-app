TASK: Implement Recommended Doctors Service

Create service layer only.

Input:

appointment_id

Flow:

1. Load appointment
2. Load doctor
3. Get specialty
4. Find doctors with same specialty
5. Exclude current doctor
6. Return top 5 recommendations

Sorting:

rating DESC
review_count DESC
doctor_name ASC

Requirements:

- reusable service
- unit-testable
- no API route yet

If specialty contains fewer than 3 doctors:

fallback to related specialties.

Example:

General Physician
→ Family Medicine
→ Internal Medicine

Return maximum 5 doctors.

Mark response field:

"recommendation_reason":
"same_specialty" | "related_specialty"

Return empty list when no recommendations exist.