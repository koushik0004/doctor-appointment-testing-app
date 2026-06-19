Update appointment booking UI.

Requirements:

1. Calendar:
   - disable past dates only
   - enable all future dates

2. Selecting a date:
   - fetch available slots

3. Display:
   - morning slots
   - afternoon slots

4. If today is selected:
   - hide past time slots
   - show only future slots

Example:
Current time = 08:00

Show:
10:00
12:00
14:00
16:00
18:00

5. If slot already booked:
   - do not display
   OR
   - show disabled

6. Remove all frontend assumptions about availability records.

Verify end-to-end booking flow.