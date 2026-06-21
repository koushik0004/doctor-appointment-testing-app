import type {
  AiWidgetAvailabilityCardContent,
  AiWidgetAvailabilityMessageContent,
  AiWidgetDoctorCardContent,
  AiWidgetDoctorListMessageContent,
  AiWidgetMessage,
  AiWidgetMessageContent,
  AiWidgetAppointmentHelpMessageContent,
  AiWidgetTextMessageContent,
} from "@/lib/ai-widget/types";
import type {
  AiWidgetChatAvailabilityCard,
  AiWidgetChatDoctorCard,
  AiWidgetChatResponsePayload,
} from "@/lib/ai-widget/types";

function createTextContent(text: string): AiWidgetTextMessageContent {
  return {
    type: "text",
    text,
  };
}

function mapDoctorCard(
  card: AiWidgetChatDoctorCard,
): AiWidgetDoctorCardContent {
  return {
    doctorId: card.doctor_id,
    doctorName: card.doctor_name,
    specialization: card.specialty,
    consultationFeeMin: card.consultation_fee_min,
    consultationFeeMax: card.consultation_fee_max,
    nextAvailableSlot: card.next_available_slot,
    clinicName: card.clinic_name,
    location: card.location,
  };
}

function mapAvailabilityCard(
  card: AiWidgetChatAvailabilityCard,
): AiWidgetAvailabilityCardContent {
  return {
    doctorId: card.doctor_id,
    doctorName: card.doctor_name,
    specialization: card.specialty,
    availableDate: card.available_date,
    availableTime: card.available_time,
  };
}

function isDoctorCard(
  item: AiWidgetChatDoctorCard | AiWidgetChatAvailabilityCard,
): item is AiWidgetChatDoctorCard {
  return "consultation_fee_min" in item;
}

function mapDoctorCards(
  items: AiWidgetChatResponsePayload["data"],
): AiWidgetDoctorCardContent[] {
  return items.filter(isDoctorCard).map(mapDoctorCard);
}

function mapAvailabilityCards(
  items: AiWidgetChatResponsePayload["data"],
): AiWidgetAvailabilityCardContent[] {
  return items.filter((item): item is AiWidgetChatAvailabilityCard => !isDoctorCard(item)).map(mapAvailabilityCard);
}

function createDoctorListContent(
  payload: AiWidgetChatResponsePayload,
): AiWidgetDoctorListMessageContent {
  return {
    type: "doctor_list",
    title:
      payload.intent === "SHOW_DOCTOR_DETAILS"
        ? "Doctor details"
        : "Doctor matches",
    summary: payload.message,
    doctors: mapDoctorCards(payload.data),
  };
}

function createAvailabilityContent(
  payload: AiWidgetChatResponsePayload,
): AiWidgetAvailabilityMessageContent {
  return {
    type: "availability",
    title: "Available appointments",
    summary: payload.message,
    slots: mapAvailabilityCards(payload.data),
  };
}

function createAppointmentHelpContent(
  payload: AiWidgetChatResponsePayload,
): AiWidgetAppointmentHelpMessageContent {
  return {
    type: "appointment_help",
    title: "Appointment help",
    text: payload.message,
  };
}

export function mapChatResponseToContent(
  payload: AiWidgetChatResponsePayload,
): AiWidgetMessageContent {
  switch (payload.intent) {
    case "SHOW_DOCTORS_BY_SPECIALIZATION":
    case "SHOW_DOCTOR_DETAILS":
      return createDoctorListContent(payload);
    case "SHOW_AVAILABLE_DOCTORS":
      return createAvailabilityContent(payload);
    case "APPOINTMENT_HELP":
      return createAppointmentHelpContent(payload);
    case "UNKNOWN":
    default:
      return createTextContent(payload.message);
  }
}

export function createAssistantMessageFromChatResponse(
  payload: AiWidgetChatResponsePayload,
  conversationLength: number,
): AiWidgetMessage {
  return {
    id: `assistant-reply-${conversationLength + 1}`,
    role: "assistant",
    content: mapChatResponseToContent(payload),
    createdAt: new Date().toISOString(),
    metadata: {
      intent: payload.intent,
      response: payload.response ?? payload.message,
    },
  };
}

export function createTextMessageContent(text: string): AiWidgetTextMessageContent {
  return createTextContent(text);
}
