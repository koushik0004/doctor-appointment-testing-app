export type AiWidgetActor = "assistant" | "user" | "system";

export type AiWidgetMessageStatus = "idle" | "streaming" | "failed";

export type AiWidgetMessage = {
  id: string;
  role: AiWidgetActor;
  content: string;
  createdAt: string;
  status?: AiWidgetMessageStatus;
  metadata?: Record<string, unknown>;
};

export type AiWidgetQuickAction = {
  id: string;
  label: string;
  prompt: string;
};
