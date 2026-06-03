export type AppointmentType = "IN_PERSON" | "TELEMEDICINE";

export type AppointmentSlot = {
  time: string;
  available: boolean;
};

export type BookingPatientDetails = {
  full_name: string;
  email: string;
  phone?: string;
  health_description?: string;
};
