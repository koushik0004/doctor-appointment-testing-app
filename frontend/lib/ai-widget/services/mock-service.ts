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
    available_time: "10:00 AM",
  },
  {
    doctor_id: 2,
    doctor_name: "Dr. Marcus Lee",
    specialty: "Cardiology",
    available_date: "2026-06-22",
    available_time: "2:30 PM",
  },
];

const mockReplyRules: MockReplyRule[] = [
  {
    test: (message) => message.includes("appointment") || message.includes("book"),
    createResponse: () => ({
      intent: "APPOINTMENT_HELP",
      message:
        "I can help you book an appointment by checking doctor availability, selecting a time, and confirming the visit details.",
      data: [],
      response:
        "I can help you book an appointment by checking doctor availability, selecting a time, and confirming the visit details.",
    }),
  },
  {
    test: (message) =>
      message.includes("available") || message.includes("tomorrow") || message.includes("schedule"),
    createResponse: () => ({
      intent: "SHOW_AVAILABLE_DOCTORS",
      message: "Here are the doctors with openings for tomorrow.",
      data: sampleAvailabilityData,
      response: "Here are the doctors with openings for tomorrow.",
    }),
  },
  {
    test: (message) => message.includes("cardiologist") || message.includes("cardiology"),
    createResponse: () => ({
      intent: "SHOW_DOCTORS_BY_SPECIALIZATION",
      message: "I found 2 cardiologists who can help.",
      data: sampleDoctorData,
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
