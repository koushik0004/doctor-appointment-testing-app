Create an AppointmentCalendar component using the official shadcn/ui Calendar component (react-day-picker based).

Important:

Do NOT build a custom calendar from scratch.

Use:

- shadcn/ui Calendar
- react-day-picker

Requirements:

Reference Design:

- Large calendar displayed inline on the page
- Month navigation arrows
- Calendar grid
- Selected date highlighting
- Available date highlighting
- Disabled date support
- Healthcare themed styling

Project Constraints:

- Next.js 15
- TypeScript
- Tailwind CSS
- Existing shadcn/ui setup

Component Responsibilities:

- Render the calendar
- Show available dates
- Disable unavailable dates
- Allow selecting a single appointment date

Props:

selectedDate: Date | undefined
availableDates: Date[]
onDateSelect: (date: Date | undefined) => void

Implementation Requirements:

- Reuse shadcn/ui Calendar component
- Do not recreate calendar logic manually
- Keep component wrapper clean and reusable
- Support future backend integration

Return:

- AppointmentCalendar.tsx
- Any helper utility functions if required

Do not generate installation commands.
Assume shadcn/ui Calendar is already available in the project.