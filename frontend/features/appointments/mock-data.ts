import { addDays } from "date-fns";

import { doctors } from "@/features/doctors/mock-doctors";

import type { AvailabilitySlot } from "@/features/appointments/types";
import type { AppointmentFormValues } from "@/features/appointments/schema";

export const appointmentBookingDoctor = doctors[0];

export const appointmentAvailableDates = Array.from({ length: 12 }, (_, index) =>
  addDays(new Date(2024, 9, 20), index),
);

export const appointmentAvailableSlots: AvailabilitySlot[] = [
  {
    id: 1,
    startTime: "09:00",
    endTime: "09:30",
    isBooked: false,
  },
  {
    id: 2,
    startTime: "09:30",
    endTime: "10:00",
    isBooked: false,
  },
  {
    id: 3,
    startTime: "10:00",
    endTime: "10:30",
    isBooked: false,
  },
  {
    id: 4,
    startTime: "10:30",
    endTime: "11:00",
    isBooked: false,
  },
  {
    id: 5,
    startTime: "11:00",
    endTime: "11:30",
    isBooked: false,
  },
  {
    id: 6,
    startTime: "11:30",
    endTime: "12:00",
    isBooked: false,
  },
  {
    id: 7,
    startTime: "14:00",
    endTime: "14:30",
    isBooked: false,
  },
  {
    id: 8,
    startTime: "14:30",
    endTime: "15:00",
    isBooked: false,
  },
  {
    id: 9,
    startTime: "15:00",
    endTime: "15:30",
    isBooked: false,
  },
  {
    id: 10,
    startTime: "15:30",
    endTime: "16:00",
    isBooked: false,
  },
  {
    id: 11,
    startTime: "16:00",
    endTime: "16:30",
    isBooked: false,
  },
];

export const appointmentFormMockValues: AppointmentFormValues = {
  appointment_type: "IN_PERSON",
  full_name: "Ava Thompson",
  email: "ava.thompson@example.com",
  phone: "",
  health_description:
    "Recurring chest tightness during exercise and a family history review.",
};
