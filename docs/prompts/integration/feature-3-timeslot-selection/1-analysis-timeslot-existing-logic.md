Analyze the current appointment scheduling implementation.

Goal:
Remove the dependency on pre-created doctor availability dates stored in the database.

Tasks:
1. Identify all backend files involved in:
   - doctor availability generation
   - appointment slot generation
   - calendar date enable/disable logic
   - appointment booking validation

2. Trace the complete flow:
   - frontend calendar request
   - backend API
   - database tables queried
   - response returned

3. Find every location where:
   - doctor availability records are required
   - future dates are filtered
   - dates become disabled when availability records do not exist

4. Produce a report:
   - files to modify
   - functions to modify
   - functions that can be deleted
   - database tables no longer required

DO NOT change code.
Planning only.
Create docs/reports/feature-3/scheduling-refactor-plan.md.