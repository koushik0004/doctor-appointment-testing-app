export type AiWidgetChatIntent =
  | "SHOW_DOCTORS_BY_SPECIALIZATION"
  | "SHOW_AVAILABLE_DOCTORS"
  | "SHOW_DOCTOR_DETAILS"
  | "APPOINTMENT_HELP"
  | "CANCEL_APPOINTMENT_HELP"
  | "UNKNOWN";

export type AiWidgetChatDoctorCard = {
  doctor_id: number;
  doctor_name: string;
  specialty: string;
  consultation_fee_min: number;
  consultation_fee_max: number;
  next_available_slot: string;
  clinic_name: string;
  location: string;
};

export type AiWidgetChatSearchFilters = {
  specialization?: string;
  gender?: string;
  minimum_fee?: number;
  maximum_fee?: number;
  date?: string;
  time_preference?: string;
  clinic_location?: string;
};

export type AiWidgetChatAvailabilityCard = {
  doctor_id: number;
  doctor_name: string;
  specialty: string;
  available_date: string;
  available_time: string;
};

export type AiWidgetChatResponsePayload = {
  intent: AiWidgetChatIntent;
  message: string;
  data: Array<AiWidgetChatDoctorCard | AiWidgetChatAvailabilityCard>;
  search_filters?: AiWidgetChatSearchFilters;
  help_steps?: string[];
  response?: string;
};
