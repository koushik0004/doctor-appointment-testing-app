import { z } from "zod";

import type { AppointmentType } from "@/features/appointments/types";

export const appointmentTypeValues = ["IN_PERSON", "TELEMEDICINE"] as const;

export const appointmentTypeLabels: Record<AppointmentType, string> = {
  IN_PERSON: "In Person",
  TELEMEDICINE: "Telemedicine",
};

export const appointmentFormSchema = z.object({
  appointment_type: z.enum(appointmentTypeValues, {
    required_error: "Select an appointment type.",
  }),
  full_name: z
    .string()
    .trim()
    .min(2, "Full name must be at least 2 characters."),
  email: z.string().trim().email("Enter a valid email address."),
  phone: z.string().trim().optional(),
  health_description: z
    .string()
    .trim()
    .max(500, "Health description must be 500 characters or less.")
    .optional(),
});

export type AppointmentFormValues = z.infer<typeof appointmentFormSchema>;

export const appointmentFormDefaults: AppointmentFormValues = {
  appointment_type: "IN_PERSON",
  full_name: "",
  email: "",
  phone: "",
  health_description: "",
};
