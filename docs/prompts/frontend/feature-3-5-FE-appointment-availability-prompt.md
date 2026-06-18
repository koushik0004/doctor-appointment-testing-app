Create a reusable AppointmentAvailability component.

Context:

The application already uses a separate AppointmentCalendar component based on shadcn/ui Calendar.

The selected date will be passed into this component.

This component is responsible only for displaying and selecting available appointment slots for the currently selected date.

Reference Design:

Display slots grouped by time period:

Morning
- 09:00 AM
- 09:30 AM
- 10:00 AM
- 10:30 AM
- 11:00 AM
- 11:30 AM

Afternoon
- 02:00 PM
- 02:30 PM
- 03:00 PM
- 03:30 PM
- 04:00 PM

Requirements:

- Show available slots for the selected date
- Highlight selected slot
- Support unavailable/booked slots
- Disable booked slots from selection
- Responsive grid layout
- Healthcare application styling
- TypeScript
- Tailwind CSS

Component Props:

selectedDate: Date | undefined

selectedSlot: string | null

availableSlots: {
  time: string;
  available: boolean;
}[]

onSlotSelect: (slot: string) => void

Implementation Notes:

- Do not build calendar functionality here
- This component works together with AppointmentCalendar
- Keep component reusable for future backend integration
- Future API data should be easy to plug in

Return:

- AppointmentAvailability.tsx
- Associated TypeScript types if needed