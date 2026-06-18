import { format, isValid, parse } from "date-fns";

import type { AvailabilitySlot } from "@/features/appointments/types";

export function formatAppointmentDate(date: Date) {
  return format(date, "EEEE, MMMM d, yyyy");
}

export function formatAppointmentTime(time: string) {
  const parsedTime = parse(time, "HH:mm", new Date());
  if (!isValid(parsedTime)) {
    return time;
  }

  return format(parsedTime, "hh:mm a");
}

export function createDateKey(date: Date) {
  return format(date, "yyyy-MM-dd");
}

export function groupAvailabilitySlots(slots: AvailabilitySlot[]) {
  const morningSlots: AvailabilitySlot[] = [];
  const afternoonSlots: AvailabilitySlot[] = [];

  for (const slot of slots) {
    const hour = Number(slot.startTime.slice(0, 2));
    if (Number.isNaN(hour) || hour < 12) {
      morningSlots.push(slot);
    } else {
      afternoonSlots.push(slot);
    }
  }

  return { morningSlots, afternoonSlots };
}
