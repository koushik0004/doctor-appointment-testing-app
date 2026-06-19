# Feature 4 Search Performance

## Indexes Added

The appointment search implementation filters through `patients` via joins on:

- `patients.full_name` for partial name matching
- `patients.email` for exact email matching
- `patients.phone` for exact phone matching

The database layer now includes these patient indexes:

- `ix_patients_full_name`
- `ix_patients_email`
- `ix_patients_phone`

`ix_patients_email` already existed through the unique email constraint and `index=True` mapping.

## Expected Query Improvements

- Exact email lookups should use the `patients.email` index and avoid scanning the whole patient table.
- Exact phone lookups should use the `patients.phone` index and reduce lookup cost for repeated searches.
- Name searches should benefit from the new `full_name` index for future prefix-based or planner-assisted searches.

## Query Shape Notes

The current name search uses a case-insensitive contains match:

- `LOWER(patients.full_name) LIKE '%term%'`

That pattern is still useful for user-facing search behavior, but a leading wildcard limits how much a standard B-tree index can help. The new index still keeps the schema aligned with the search feature and gives the database a better path for future query refinements.

