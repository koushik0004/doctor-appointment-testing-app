import { ApiError, apiClient } from "@/lib/api-client";
import type {
  AiWidgetChatConversationRequest,
  AiWidgetChatRequest,
  AiWidgetChatResponse,
  AiWidgetConversationContext,
  AiWidgetMessage,
  AiWidgetService,
} from "@/lib/ai-widget/types";
import type { AiWidgetChatResponsePayload } from "@/lib/ai-widget/types";
import { createAssistantMessageFromChatResponse } from "@/lib/ai-widget/services/chat-response-mapper";

function extractMessageText(message: AiWidgetMessage): string {
  switch (message.content.type) {
    case "text":
      return message.content.text;
    case "doctor_list":
      return message.content.summary;
    case "availability":
      return message.content.summary;
    case "appointment_help":
      return message.content.text;
    default:
      return "";
  }
}

function getConversationContext(message: AiWidgetMessage): AiWidgetConversationContext | undefined {
  const metadata = message.metadata;
  if (!metadata || typeof metadata !== "object") {
    return undefined;
  }

  const value = (metadata as Record<string, unknown>).conversation;
  if (!value || typeof value !== "object") {
    return undefined;
  }

  const candidate = value as Partial<AiWidgetConversationContext>;
  if (typeof candidate.conversation_id !== "string" || typeof candidate.routed_to !== "string") {
    return undefined;
  }

  return candidate as AiWidgetConversationContext;
}

function serializeConversation(messages: AiWidgetMessage[]): AiWidgetChatConversationRequest | undefined {
  const context = [...messages].reverse().map(getConversationContext).find(Boolean);
  const history = messages
    .map((message) => {
      const text = extractMessageText(message).trim();
      if (!text) {
        return null;
      }

      const turnContext = getConversationContext(message);
      const metadata = message.metadata as Record<string, unknown> | undefined;
      const intent =
        metadata && typeof metadata.intent === "string" ? metadata.intent : undefined;

      return {
        role: message.role,
        text,
        intent,
        search_filters: turnContext?.active_filters,
        selected_doctor_id: turnContext?.selected_doctor_id,
        selected_doctor_name: turnContext?.selected_doctor_name,
      };
    })
    .filter((item): item is NonNullable<typeof item> => item !== null);

  if (!context && history.length === 0) {
    return undefined;
  }

  return {
    conversation_id: context?.conversation_id,
    context,
    history,
  };
}

export function createApiAiWidgetService(): AiWidgetService {
  return {
    async sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse> {
      try {
        const payload = await apiClient.post<AiWidgetChatResponsePayload>("/chat", {
          message: request.message,
          conversation: serializeConversation(request.conversation),
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
