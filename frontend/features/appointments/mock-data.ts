import { addDays } from "date-fns";

import { doctors } from "@/features/doctors/mock-doctors";

import type { AppointmentSlot } from "@/features/appointments/types";
import type { AppointmentFormValues } from "@/features/appointments/schema";

export const appointmentBookingDoctor = doctors[0];

export const appointmentAvailableDates = Array.from({ length: 12 }, (_, index) =>
  addDays(new Date(2024, 9, 20), index),
);

export const appointmentAvailableSlots: AppointmentSlot[] = [
  { time: "09:00 AM", available: true },
  { time: "09:30 AM", available: true },
  { time: "10:00 AM", available: true },
  { time: "10:30 AM", available: true },
  { time: "11:00 AM", available: true },
  { time: "11:30 AM", available: true },
  { time: "02:00 PM", available: true },
  { time: "02:30 PM", available: true },
  { time: "03:00 PM", available: true },
  { time: "03:30 PM", available: true },
  { time: "04:00 PM", available: true },
];

export const appointmentFormMockValues: AppointmentFormValues = {
  appointment_type: "IN_PERSON",
  full_name: "Ava Thompson",
  email: "ava.thompson@example.com",
  phone: "",
  health_description:
    "Recurring chest tightness during exercise and a family history review.",
};
