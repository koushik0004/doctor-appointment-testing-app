import type { AiWidgetMessage } from "@/lib/ai-widget/types/message";
import type { AiWidgetConfig, AiWidgetState } from "@/lib/ai-widget/types/widget";
import { createTextMessageContent } from "@/lib/ai-widget/services/chat-response-mapper";

export type AiWidgetAction =
  | { type: "toggle" }
  | { type: "open" }
  | { type: "close" }
  | { type: "setDraft"; payload: string }
  | { type: "startSend"; payload: AiWidgetMessage }
  | { type: "appendMessage"; payload: AiWidgetMessage }
  | { type: "setError"; payload: string | null }
  | { type: "reset"; payload?: AiWidgetConfig };

function createWelcomeMessage(): AiWidgetMessage {
  return {
    id: "welcome-message",
    role: "assistant",
    content: createTextMessageContent(
      "Hello, I am your Doctor Appointment Assistant. How can I help you today?",
    ),
    createdAt: new Date().toISOString(),
  };
}

export function createInitialAiWidgetState(
  config: AiWidgetConfig = {},
): AiWidgetState {
  return {
    isOpen: config.initialOpen ?? false,
    status: "idle",
    messages: config.initialMessages ?? [createWelcomeMessage()],
    draft: "",
    errorMessage: null,
  };
}

export function aiWidgetReducer(
  state: AiWidgetState,
  action: AiWidgetAction,
): AiWidgetState {
  switch (action.type) {
    case "toggle":
      return {
        ...state,
        isOpen: !state.isOpen,
      };
    case "open":
      return {
        ...state,
        isOpen: true,
      };
    case "close":
      return {
        ...state,
        isOpen: false,
      };
    case "setDraft":
      return {
        ...state,
        draft: action.payload,
      };
    case "startSend":
      return {
        ...state,
        status: "sending",
        messages: [...state.messages, action.payload],
        draft: "",
        errorMessage: null,
      };
    case "appendMessage":
      return {
        ...state,
        status: "idle",
        messages: [...state.messages, action.payload],
      };
    case "setError":
      return {
        ...state,
        status: action.payload ? "error" : "idle",
        errorMessage: action.payload,
      };
    case "reset":
      return createInitialAiWidgetState(action.payload);
    default:
      return state;
  }
}
