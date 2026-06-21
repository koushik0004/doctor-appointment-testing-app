import { apiClient } from "@/lib/api-client";
import type {
  AiWidgetChatRequest,
  AiWidgetChatResponse,
  AiWidgetMessage,
  AiWidgetService,
} from "@/lib/ai-widget/types";

type ChatApiResponse = {
  response: string;
};

function createAssistantReply(
  content: string,
  conversationLength: number,
): AiWidgetMessage {
  return {
    id: `assistant-reply-${conversationLength + 1}`,
    role: "assistant",
    content,
    createdAt: new Date().toISOString(),
  };
}

export function createApiAiWidgetService(): AiWidgetService {
  return {
    async sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse> {
      const payload = await apiClient.post<ChatApiResponse>("/chat", {
        message: request.message,
      });

      return {
        reply: createAssistantReply(payload.response, request.conversation.length),
      };
    },
  };
}
