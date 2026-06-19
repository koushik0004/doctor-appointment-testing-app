TASK: Diagnose why appointment calendar disables all dates.

DO NOT FIX ANYTHING YET.

Current behavior:
- Every date appears disabled.
- User cannot select any date.
- Time slots never become available.

Required investigation:

1. Locate:
   - Calendar component
   - Date picker component
   - Booking page
   - Date utility functions
   - Slot generation logic

2. Trace exact logic responsible for:
   - disabled dates
   - selected dates
   - minimum selectable date

3. Identify:

   A. What value is being used as "today"

   B. What value is being passed to:
      - minDate
      - disabledDates
      - isDateDisabled
      - filterDate
      - disableDay
      - any equivalent callback

   C. Whether dates are:
      - Date objects
      - strings
      - ISO strings
      - UTC dates

4. Determine why ALL dates become disabled.

5. Produce:

docs/calendar-root-cause-analysis.md

Include:

- exact file names
- exact code block causing issue
- root cause explanation
- proposed fix

DO NOT IMPLEMENT.