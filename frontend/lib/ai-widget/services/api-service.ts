import { ApiError, apiClient } from "@/lib/api-client";
import type {
  AiWidgetChatRequest,
  AiWidgetChatResponse,
  AiWidgetService,
} from "@/lib/ai-widget/types";
import type { AiWidgetChatResponsePayload } from "@/lib/ai-widget/types";
import { createAssistantMessageFromChatResponse } from "@/lib/ai-widget/services/chat-response-mapper";

export function createApiAiWidgetService(): AiWidgetService {
  return {
    async sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse> {
      try {
        const payload = await apiClient.post<AiWidgetChatResponsePayload>("/chat", {
          message: request.message,
        });

        return {
          reply: createAssistantMessageFromChatResponse(
            payload,
            request.conversation.length,
          ),
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
