Perform end-to-end verification.

Scenario 1:
Today = 19 June
Select 20 June
Expected:
All generated slots visible.

Scenario 2:
Today = 19 June 08:00
Select today.
Expected:
Only future slots visible.

Scenario 3:
Book doctor A on 20 June 10:00.
Expected:
Appointment saved.

Scenario 4:
Refresh page.
Expected:
20 June 10:00 no longer available for doctor A.

Scenario 5:
Doctor B on same date and time.
Expected:
Still available.

Scenario 6:
No availability records exist in database.
Expected:
Calendar still works.

Create scheduling-verification-report.md.