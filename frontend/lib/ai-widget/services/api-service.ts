import { ApiError, apiClient } from "@/lib/api-client";
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
      try {
        const payload = await apiClient.post<ChatApiResponse>("/chat", {
          message: request.message,
        });

        return {
          reply: createAssistantReply(payload.response, request.conversation.length),
        };
      } catch (error) {
        if (error instanceof ApiError) {
          if (error.status >= 500) {
            throw new Error(
              "The assistant is unavailable right now. Please try again in a moment.",
            );
          }

          throw new Error(
            "Your message could not be sent. Please review it and try again.",
          );
        }

        throw new Error(
          "We could not reach the assistant. Please check the connection and try again.",
        );
      }
    },
  };
}
