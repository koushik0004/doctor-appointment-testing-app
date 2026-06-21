import type {
  AiWidgetChatRequest,
  AiWidgetChatResponse,
  AiWidgetService,
} from "@/lib/ai-widget/types";

export function createNoopAiWidgetService(): AiWidgetService {
  return {
    async sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse> {
      void request;

      throw new Error(
        "AI widget service is not implemented yet. Provide a concrete service in a later step.",
      );
    },
  };
}
