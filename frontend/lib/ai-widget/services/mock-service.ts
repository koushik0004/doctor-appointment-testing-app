import type {
  AiWidgetChatRequest,
  AiWidgetChatResponse,
  AiWidgetMessage,
  AiWidgetService,
} from "@/lib/ai-widget/types";

const MOCK_REPLY_DELAY_MS = 1000;

type MockReplyRule = {
  test: (message: string) => boolean;
  reply: string;
};

const mockReplyRules: MockReplyRule[] = [
  {
    test: (message) => message.includes("cardiologist"),
    reply: "I can help you find a cardiologist.",
  },
  {
    test: (message) => message.includes("dermatologist"),
    reply: "I can help you find a dermatologist.",
  },
  {
    test: (message) => message.includes("pediatrician"),
    reply: "I can help you find a pediatrician.",
  },
  {
    test: (message) => message.includes("book") || message.includes("appointment"),
    reply: "I can help you book an appointment with an available doctor.",
  },
  {
    test: (message) => message.includes("schedule") || message.includes("time"),
    reply: "I can help you check available schedules and appointment times.",
  },
];

function sleep(durationMs: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, durationMs);
  });
}

function resolveMockReply(message: string) {
  const normalizedMessage = message.trim().toLowerCase();
  const matchedRule = mockReplyRules.find((rule) => rule.test(normalizedMessage));

  return (
    matchedRule?.reply ??
    "I can help with doctors, schedules, and booking questions."
  );
}

function createAssistantReply(content: string, conversationLength: number): AiWidgetMessage {
  return {
    id: `assistant-reply-${conversationLength + 1}`,
    role: "assistant",
    content,
    createdAt: new Date().toISOString(),
  };
}

export function createMockAiWidgetService(): AiWidgetService {
  return {
    async sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse> {
      await sleep(MOCK_REPLY_DELAY_MS);

      return {
        reply: createAssistantReply(
          resolveMockReply(request.message),
          request.conversation.length,
        ),
      };
    },
  };
}
