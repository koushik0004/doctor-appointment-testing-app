import type { AiWidgetMessage } from "@/lib/ai-widget/types/message";

export type AiWidgetChatRequest = {
  message: string;
  conversation: AiWidgetMessage[];
};

export type AiWidgetChatResponse = {
  reply: AiWidgetMessage;
};

export interface AiWidgetService {
  sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse>;
}
