import type {
  AiWidgetChatRequest,
  AiWidgetChatResponse,
  AiWidgetService,
} from "@/lib/ai-widget/types";
import type { AiWidgetChatResponsePayload } from "@/lib/ai-widget/types";
import { createAssistantMessageFromChatResponse } from "@/lib/ai-widget/services/chat-response-mapper";

const MOCK_REPLY_DELAY_MS = 1000;

type MockReplyRule = {
  test: (message: string) => boolean;
  createResponse: (message: string) => AiWidgetChatResponsePayload;
};

const sampleDoctorData = [
  {
    doctor_id: 1,
    doctor_name: "Dr. Sarah Jenkins",
    specialty: "Cardiology",
    consultation_fee_min: 800,
    consultation_fee_max: 1200,
    next_available_slot: "Tomorrow, 10:00 AM",
    clinic_name: "Northside Heart Clinic",
    location: "Koramangala, Bengaluru",
  },
  {
    doctor_id: 2,
    doctor_name: "Dr. Marcus Lee",
    specialty: "Cardiology",
    consultation_fee_min: 900,
    consultation_fee_max: 1500,
    next_available_slot: "Tomorrow, 2:30 PM",
    clinic_name: "City Cardiac Center",
    location: "Indiranagar, Bengaluru",
  },
];

const sampleAvailabilityData = [
  {
    doctor_id: 1,
    doctor_name: "Dr. Sarah Jenkins",
    specialty: "Cardiology",
    available_date: "2026-06-22",
    available_time: "6:00 PM",
  },
  {
    doctor_id: 2,
    doctor_name: "Dr. Marcus Lee",
    specialty: "Cardiology",
    available_date: "2026-06-22",
    available_time: "6:30 PM",
  },
];

const mockReplyRules: MockReplyRule[] = [
  {
    test: (message) =>
      message.includes("available") ||
      message.includes("tomorrow") ||
      message.includes("schedule") ||
      message.includes("after 5 pm") ||
      message.includes("after 5pm"),
    createResponse: () => ({
      intent: "SHOW_AVAILABLE_DOCTORS",
      message: "Here are the doctors with openings after 5 PM tomorrow.",
      data: sampleAvailabilityData,
      search_filters: {
        specialization: "Cardiology",
        gender: "Female",
        date: "2026-06-22",
        time_preference: "After 5:00 PM",
      },
      response: "Here are the doctors with openings after 5 PM tomorrow.",
    }),
  },
  {
    test: (message) => message.includes("cancel"),
    createResponse: () => ({
      intent: "CANCEL_APPOINTMENT_HELP",
      message:
        "Appointment cancellation is not supported through AI chat. Please use the app's existing cancellation flow or contact support for help.",
      data: [],
      help_steps: [
        "Open the existing cancellation flow in the app.",
        "Find your booked appointment details.",
        "Follow the cancellation instructions shown there.",
        "If you cannot access the booking, contact support.",
      ],
      response:
        "Appointment cancellation is not supported through AI chat. Please use the app's existing cancellation flow or contact support for help.",
    }),
  },
  {
    test: (message) => message.includes("appointment") || message.includes("book"),
    createResponse: () => ({
      intent: "APPOINTMENT_HELP",
      message: "Here is how to book an appointment in the app.",
      data: [],
      help_steps: [
        "Choose a doctor.",
        "Select an available date.",
        "Choose a time slot.",
        "Enter patient details.",
        "Confirm the appointment.",
      ],
      response: "Here is how to book an appointment in the app.",
    }),
  },
  {
    test: (message) => message.includes("cardiologist") || message.includes("cardiology"),
    createResponse: () => ({
      intent: "SHOW_DOCTORS_BY_SPECIALIZATION",
      message: "I found 2 cardiologists who can help.",
      data: sampleDoctorData,
      search_filters: {
        specialization: "Cardiology",
      },
      response: "I found 2 cardiologists who can help.",
    }),
  },
];

function sleep(durationMs: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, durationMs);
  });
}

function resolveMockResponse(message: string): AiWidgetChatResponsePayload {
  const normalizedMessage = message.trim().toLowerCase();
  const matchedRule = mockReplyRules.find((rule) => rule.test(normalizedMessage));

  if (matchedRule) {
    return matchedRule.createResponse(normalizedMessage);
  }

  return {
    intent: "UNKNOWN",
    message: "I can help with doctors, schedules, and booking questions.",
    data: [],
    response: "I can help with doctors, schedules, and booking questions.",
  };
}

export function createMockAiWidgetService(): AiWidgetService {
  return {
    async sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse> {
      await sleep(MOCK_REPLY_DELAY_MS);

      const payload = resolveMockResponse(request.message);

      return {
        reply: createAssistantMessageFromChatResponse(payload, request.conversation.length),
      };
    },
  };
}
