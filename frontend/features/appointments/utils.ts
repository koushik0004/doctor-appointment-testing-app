import { format, isBefore, isValid, parse, startOfDay } from "date-fns";

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

export function getLocalDateTime(date: Date, time: string) {
  const parsedTime = parse(time, "HH:mm", date);
  if (!isValid(parsedTime)) {
    return null;
  }

  return parsedTime;
}

export function isPastAppointmentDate(
  date: Date,
  referenceDate: Date = new Date(),
) {
  return isBefore(startOfDay(date), startOfDay(referenceDate));
}

export function isElapsedAppointmentSlot(
  date: Date,
  startTime: string,
  referenceDate: Date = new Date(),
) {
  const slotDateTime = getLocalDateTime(date, startTime);
  if (!slotDateTime) {
    return false;
  }

  return slotDateTime.getTime() <= referenceDate.getTime();
}

export function filterBookableSlotsForDate(
  slots: AvailabilitySlot[],
  selectedDate: Date,
  referenceDate: Date = new Date(),
) {
  return slots.filter((slot) => {
    if (slot.isBooked) {
      return false;
    }

    if (isPastAppointmentDate(selectedDate, referenceDate)) {
      return false;
    }

    return !isElapsedAppointmentSlot(selectedDate, slot.startTime, referenceDate);
  });
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
