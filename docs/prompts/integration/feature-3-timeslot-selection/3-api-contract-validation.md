Review appointment APIs.

Expected Behaviour:

GET available slots:
Input:
- doctor_id
- date

Output:
{
  "date": "...",
  "doctor_id": "...",
  "available_slots": [...]
}

Availability Calculation:

available_slots =
generated_slots
minus
already_booked_slots

Verify:
- no dependency on availability table
- no dependency on seeded records
- no dependency on future availability generation

Fix API if needed.

Update API documentation.