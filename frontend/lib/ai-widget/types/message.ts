export type AiWidgetActor = "assistant" | "user" | "system";

export type AiWidgetMessageStatus = "idle" | "streaming" | "failed";

export type AiWidgetTextMessageContent = {
  type: "text";
  text: string;
};

export type AiWidgetDoctorCardContent = {
  doctorId: number;
  doctorName: string;
  specialization: string;
  consultationFeeMin: number;
  consultationFeeMax: number;
  nextAvailableSlot: string;
  clinicName: string;
  location: string;
};

export type AiWidgetAvailabilityCardContent = {
  doctorId: number;
  doctorName: string;
  specialization: string;
  availableDate: string;
  availableTime: string;
};

export type AiWidgetSearchFilterChip = {
  label: string;
  value: string;
};

export type AiWidgetSearchSummary = {
  countLabel: string;
  filters: AiWidgetSearchFilterChip[];
};

export type AiWidgetDoctorListMessageContent = {
  type: "doctor_list";
  title: string;
  summary: string;
  doctors: AiWidgetDoctorCardContent[];
  searchSummary?: AiWidgetSearchSummary;
};

export type AiWidgetAvailabilityMessageContent = {
  type: "availability";
  title: string;
  summary: string;
  slots: AiWidgetAvailabilityCardContent[];
  searchSummary?: AiWidgetSearchSummary;
};

export type AiWidgetAppointmentHelpMessageContent = {
  type: "appointment_help";
  title: string;
  text: string;
  steps?: string[];
};

export type AiWidgetMessageContent =
  | AiWidgetTextMessageContent
  | AiWidgetDoctorListMessageContent
  | AiWidgetAvailabilityMessageContent
  | AiWidgetAppointmentHelpMessageContent;

export type AiWidgetMessage = {
  id: string;
  role: AiWidgetActor;
  content: AiWidgetMessageContent;
  createdAt: string;
  status?: AiWidgetMessageStatus;
  metadata?: Record<string, unknown>;
};

export type AiWidgetQuickAction = {
  id: string;
  label: string;
  prompt: string;
};
