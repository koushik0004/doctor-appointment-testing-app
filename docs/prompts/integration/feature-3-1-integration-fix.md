TASK: Feature 3 Integration Fixes (No New Feature Development)

CONTEXT

This Doctor Appointment Application already has:
- Doctor Listing
- Doctor Details
- Appointment Booking
- Appointment Confirmation
- Backend Appointment APIs
- Frontend Booking UI

Current task is ONLY to fix integration issues discovered during testing.

IMPORTANT RULES

- Do NOT redesign UI.
- Do NOT introduce new libraries unless absolutely required.
- Reuse existing date/calendar implementation.
- Reuse existing currency formatting utilities if present.
- Make minimal, production-safe changes.
- Preserve all existing functionality.
- Follow existing project architecture and coding conventions.

--------------------------------------------------
ISSUE 1: Currency Localization
--------------------------------------------------

Current behavior:
- Appointment booking related screens display USD ($).

Expected behavior:
- Application must use INR (₹) everywhere for appointment related pricing.

Tasks:

1. Identify all places where appointment fee currency is displayed:
   - Doctor cards
   - Doctor details page
   - Booking page
   - Confirmation page
   - API responses (if currency hardcoded)

2. Replace USD formatting with INR formatting.

3. Prefer centralized formatter if project already has:
   - currency utility
   - formatter utility
   - localization helper

4. Format examples:

₹500
₹1,000
₹1,500

5. Avoid hardcoded string duplication.

--------------------------------------------------
ISSUE 2: Appointment Calendar Logic
--------------------------------------------------

Current issue:

Calendar allows invalid date behavior.

Observed:
- Some future dates are disabled incorrectly.
- Same-day booking behavior is inconsistent.
- Date selection logic does not correctly follow current date.

Expected behavior:

RULE 1
Past dates must always be disabled.

Example:

Today = June 19, 2026

Disabled:
June 18 and earlier

RULE 2
Today must be selectable.

Example:

Browser local date = June 19

June 19 should remain enabled.

RULE 3
All future dates must be selectable.

June 20+
June 21+
etc.

RULE 4
Calendar logic must use browser local timezone.

Use browser current date.

Do NOT use:
- hardcoded date
- server date
- static mock date

RULE 5
When user selects today's date:

Show only remaining available slots.

Example:

Current time = 2:15 PM

Hide or disable:
10:00 AM
11:00 AM
1:00 PM

Keep enabled:
3:00 PM
4:00 PM
5:00 PM

RULE 6
For future dates:

Show all configured available slots.

RULE 7
Prevent booking of already elapsed slots.

Validation should exist both:
- UI level
- booking submission level

--------------------------------------------------
ANALYSIS REQUIRED
--------------------------------------------------

Before coding:

1. Locate:
   - Calendar component
   - Booking page
   - Slot generation logic
   - Date utility functions
   - Currency formatter

2. Produce a short implementation plan.

3. Identify exact files requiring modification.

--------------------------------------------------
IMPLEMENTATION
--------------------------------------------------

Apply fixes.

Then verify:

Scenario A
Today selected before first slot
→ all slots visible

Scenario B
Today selected after some slots passed
→ only future slots visible

Scenario C
Future date selected
→ all slots visible

Scenario D
Past date
→ cannot be selected

Scenario E
Appointment pricing
→ INR shown consistently

--------------------------------------------------
DELIVERABLE
--------------------------------------------------

Create:

docs/feature-3-integration-fix-report.md

Include:

- Files modified
- Currency fix summary
- Calendar fix summary
- Timezone handling approach
- Validation added
- Test scenarios executed
- Risks and follow-up items

Only complete when all acceptance criteria pass.