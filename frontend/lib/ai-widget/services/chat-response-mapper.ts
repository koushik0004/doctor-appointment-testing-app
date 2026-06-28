import type {
  AiWidgetAvailabilityCardContent,
  AiWidgetAvailabilityMessageContent,
  AiWidgetDoctorCardContent,
  AiWidgetDoctorListMessageContent,
  AiWidgetSearchFilterChip,
  AiWidgetSearchSummary,
  AiWidgetMessage,
  AiWidgetMessageContent,
  AiWidgetAppointmentHelpMessageContent,
  AiWidgetTextMessageContent,
} from "@/lib/ai-widget/types";
import type {
  AiWidgetChatAvailabilityCard,
  AiWidgetChatDoctorCard,
  AiWidgetChatSearchFilters,
  AiWidgetChatResponsePayload,
} from "@/lib/ai-widget/types";
import { addDays, format, isSameDay, parseISO, startOfDay } from "date-fns";

import { formatCurrencyInr } from "@/lib/formatters";

function createTextContent(text: string): AiWidgetTextMessageContent {
  return {
    type: "text",
    text,
  };
}

function countUniqueDoctors(
  items: AiWidgetChatResponsePayload["data"],
): number {
  return new Set(items.map((item) => item.doctor_id)).size;
}

function formatSearchDate(value: string): string {
  const parsedDate = parseISO(value);
  if (Number.isNaN(parsedDate.getTime())) {
    return value;
  }

  const today = startOfDay(new Date());
  const tomorrow = addDays(today, 1);

  if (isSameDay(parsedDate, today)) {
    return "Today";
  }

  if (isSameDay(parsedDate, tomorrow)) {
    return "Tomorrow";
  }

  return format(parsedDate, "MMM d, yyyy");
}

function formatFeeRange(
  minimumFee?: number,
  maximumFee?: number,
): string | null {
  if (minimumFee == null && maximumFee == null) {
    return null;
  }

  if (minimumFee != null && maximumFee != null) {
    return `${formatCurrencyInr(minimumFee)} - ${formatCurrencyInr(maximumFee)}`;
  }

  if (minimumFee != null) {
    return `From ${formatCurrencyInr(minimumFee)}`;
  }

  return `Up to ${formatCurrencyInr(maximumFee ?? 0)}`;
}

function buildSearchFilters(
  filters?: AiWidgetChatSearchFilters,
): AiWidgetSearchFilterChip[] {
  if (!filters) {
    return [];
  }

  const chips: AiWidgetSearchFilterChip[] = [];
  const feeRange = formatFeeRange(filters.minimum_fee, filters.maximum_fee);

  if (filters.specialization) {
    chips.push({
      label: "Specialization",
      value: filters.specialization,
    });
  }

  if (filters.gender) {
    chips.push({
      label: "Gender",
      value: filters.gender,
    });
  }

  if (feeRange) {
    chips.push({
      label: "Fee",
      value: feeRange,
    });
  }

  if (filters.date) {
    chips.push({
      label: "Date",
      value: formatSearchDate(filters.date),
    });
  }

  if (filters.time_preference) {
    chips.push({
      label: "Time",
      value: filters.time_preference,
    });
  }

  if (filters.clinic_location) {
    chips.push({
      label: "Location",
      value: filters.clinic_location,
    });
  }

  return chips;
}

function buildSearchSummary(
  payload: AiWidgetChatResponsePayload,
  itemLabel: string,
): AiWidgetSearchSummary | undefined {
  const filters = buildSearchFilters(payload.search_filters);
  const count = countUniqueDoctors(payload.data);

  if (count === 0 && filters.length === 0) {
    return undefined;
  }

  return {
    countLabel: `Found ${count} ${itemLabel}${count === 1 ? "" : "s"}.`,
    filters,
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
  const searchSummary =
    payload.intent === "SHOW_DOCTOR_DETAILS"
      ? undefined
      : buildSearchSummary(payload, "matching doctor");

  return {
    type: "doctor_list",
    title:
      payload.intent === "SHOW_DOCTOR_DETAILS"
        ? "Doctor details"
        : "Doctor matches",
    summary: payload.message,
    doctors: mapDoctorCards(payload.data),
    searchSummary,
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
    searchSummary: buildSearchSummary(payload, "matching doctor"),
  };
}

function createAppointmentHelpContent(
  payload: AiWidgetChatResponsePayload,
): AiWidgetAppointmentHelpMessageContent {
  return {
    type: "appointment_help",
    title:
      payload.intent === "CANCEL_APPOINTMENT_HELP"
        ? "Cancellation help"
        : "Appointment help",
    text: payload.message,
    steps: payload.help_steps,
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
    case "CANCEL_APPOINTMENT_HELP":
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
      conversation: payload.conversation,
    },
  };
}

export function createTextMessageContent(text: string): AiWidgetTextMessageContent {
  return createTextContent(text);
}
