# Calendar Root Cause Analysis

## Problem

The appointment calendar shows every date as disabled, so the user cannot pick a date and the slot list never populates.

## Files Inspected

- `frontend/features/appointments/components/AppointmentCalendar.tsx`
- `frontend/app/appointments/page.tsx`
- `frontend/features/appointments/api.ts`
- `frontend/features/appointments/utils.ts`
- `backend/app/db/seed.py`
- `backend/app/services/availability_service.py`
- `backend/app/repositories/availability_repository.py`

## Root Cause

The calendar is not broken by a `minDate` prop or a date-picker library bug. The disabling behavior is driven by two layers:

1. The frontend disables any date that is not present in the backend `availableDates` list.
2. The backend seed data only contains availability from `2026-06-09` through `2026-06-18`.

In the current environment, the browser date is `2026-06-19`, so every seeded availability date is already in the past. That means:

- `isBefore(date, minimumSelectableDate)` disables dates before today.
- `!availableDateKeys.has(toDateKey(date))` disables dates that do not exist in the backend availability list.

Because the seeded availability ends on June 18, there are no selectable dates left for June 19 or later, and the whole calendar appears disabled.

## Exact Code Paths

### 1) Frontend calendar disable logic

`frontend/features/appointments/components/AppointmentCalendar.tsx`

```tsx
const minimumSelectableDate = React.useMemo(() => {
  return startOfDay(referenceDate);
}, [referenceDate]);

<Calendar
  ...
  disabled={(date) =>
    isBefore(date, minimumSelectableDate) ||
    !availableDateKeys.has(toDateKey(date))
  }
/>
```

This is the gate that disables every date not in the backend availability set.

### 2) Frontend available-date filtering

`frontend/app/appointments/page.tsx`

```tsx
const allSlots = [...availability.morningSlots, ...availability.afternoonSlots];
const filteredSlots = allSlots.filter(
  (slot) =>
    !slot.isBooked && slot.appointmentType === selectedAppointmentType,
);
const availableDates = availability.availableDates.filter((date) =>
  filteredSlots.some((slot) => slot.availableDate === createDateKey(date)),
);
```

Only dates that have at least one unbooked slot of the selected appointment type are passed to the calendar.

### 3) Backend seed data is stale relative to today

`backend/app/db/seed.py`

```py
DOCTOR_AVAILABILITY_SEED_DATA = {
    "Dr. Sarah Jenkins": [
        {
            "available_date": date(2026, 6, 9),
            "start_time": "10:30",
            "end_time": "11:00",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 9),
            "start_time": "15:00",
            "end_time": "15:30",
            "appointment_type": "TELEMEDICINE",
        },
    ],
    ...
    "Dr. Sofia Martinez": [
        {
            "available_date": date(2026, 6, 18),
            "start_time": "10:00",
            "end_time": "10:30",
            "appointment_type": "IN_PERSON",
        },
        {
            "available_date": date(2026, 6, 18),
            "start_time": "14:30",
            "end_time": "15:00",
            "appointment_type": "TELEMEDICINE",
        },
    ],
}
```

This seed only provides past dates relative to `2026-06-19`.

## Data Types

- `backend/app/services/availability_service.py` returns `available_dates` as ISO date strings.
- `frontend/features/appointments/api.ts` converts those strings to `Date` objects with `parseISO`.
- `frontend/app/appointments/page.tsx` converts selected dates back to `yyyy-MM-dd` keys with `createDateKey`.
- Slot dates remain strings, and comparisons are done with formatted date keys.

This type flow is consistent. It is not the source of the bug.

## Why Current And Future Dates Should Be Available

Current date availability comes from the frontend rule:

- `minimumSelectableDate = startOfDay(referenceDate)`
- the browser-local `referenceDate` is passed from `currentDateTime`
- today is not disabled by the `isBefore` check

Future date availability comes from backend data:

- if a future date exists in `availability.availableDates`
- and it has at least one unbooked slot for the selected appointment type
- then it is included in `availableDates` and remains selectable

In this repo snapshot, no such future dates exist in the seed data.

## Proposed Fix

1. Replace the static June 2026 availability seed with rolling future dates, or regenerate seed data relative to `date.today()`.
2. Keep the frontend calendar rule that disables past dates only.
3. Preserve the backend-to-frontend availability filter so only dates with real unbooked slots stay selectable.

## Conclusion

The calendar is disabled everywhere because the backend seed data is outdated relative to the current date. The frontend logic is functioning as written, but it only has past availability to work with.
