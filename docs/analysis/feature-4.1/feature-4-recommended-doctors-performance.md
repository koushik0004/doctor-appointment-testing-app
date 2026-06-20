# Feature 4.1 Recommended Doctors Performance

## Scope

This note records the query optimization work for the recommended-doctors flow.

## Indexes Added

The doctor table now has the following recommendation-related indexes in the model and schema:

- `specialty` - already present before this step
- `rating` - added for ranking support
- `is_active` - added for active-doctor filtering

Implementation details:

- `backend/app/models/doctor.py` now marks `rating` and `is_active` as indexed columns
- `backend/alembic/versions/20260620_0003_doctor_recommendation_indexes.py` adds the physical SQLite indexes for existing databases

## Query Improvements

The recommendation service now orders candidate doctors in the database instead of sorting them in Python after fetch:

- filters still use `specialty`, `is_active`, and the exclusion of the source doctor
- ordering is now applied with `rating DESC`, `review_count DESC`, and `name ASC` in the SQL statement
- the service still performs availability checks in Python because bookable-slot resolution depends on the scheduling flow, not a doctor-table field

This keeps the recommendation logic unchanged while reducing in-memory work and giving SQLite a better chance to use the new indexes during candidate selection and ordering.

## Expected Performance Impact

- faster candidate lookup for active doctors in the same specialty
- less Python-side work because the result set arrives in ranked order
- better scalability as the doctor table grows, especially for recommendation-heavy pages
- no breaking schema changes and no change to the API contract

