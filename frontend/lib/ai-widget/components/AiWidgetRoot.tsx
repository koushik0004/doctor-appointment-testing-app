"use client";

import { useId } from "react";

import { ChatLauncher } from "@/lib/ai-widget/components/ChatLauncher";
import { ChatWindow } from "@/lib/ai-widget/components/ChatWindow";
import { AiWidgetProvider, useAiWidget } from "@/lib/ai-widget/core";
import { createMockAiWidgetService } from "@/lib/ai-widget/services";
import { aiWidgetClassNames } from "@/lib/ai-widget/styles";
import type { AiWidgetMessage, AiWidgetRootProps } from "@/lib/ai-widget/types";
import { cn } from "@/lib/utils";

function AiWidgetFrame({
  adapter,
  className,
  service,
}: Omit<AiWidgetRootProps, "config">) {
  const { state, dispatch } = useAiWidget();
  const presentation = adapter.getPresentation();
  const quickActions = adapter.getQuickActions?.() ?? [];
  const messageId = useId();
  const chatService = service ?? createMockAiWidgetService();

  async function handleSubmit() {
    const nextMessage = state.draft.trim();

    if (!nextMessage) {
      return;
    }

    const userMessage: AiWidgetMessage = {
      id: `user-${messageId}-${state.messages.length + 1}`,
      role: "user",
      content: nextMessage,
      createdAt: new Date().toISOString(),
    };

    dispatch({
      type: "startSend",
      payload: userMessage,
    });

    try {
      const response = await chatService.sendMessage({
        message: nextMessage,
        conversation: [...state.messages, userMessage],
      });

      dispatch({
        type: "appendMessage",
        payload: response.reply,
      });
    } catch (error) {
      dispatch({
        type: "setError",
        payload:
          error instanceof Error
            ? error.message
            : "The assistant could not reply. Please try again in a moment.",
      });
    }
  }

  return (
    <div className={cn(aiWidgetClassNames.root, className)}>
      {state.isOpen ? (
        <ChatWindow
          presentation={presentation}
          quickActions={quickActions}
          state={state}
          onClose={() => dispatch({ type: "close" })}
          onDraftChange={(value) => dispatch({ type: "setDraft", payload: value })}
          onSubmit={handleSubmit}
        />
      ) : null}

      <ChatLauncher
        isOpen={state.isOpen}
        label={presentation.launcherLabel}
        onClick={() => dispatch({ type: "toggle" })}
      />
    </div>
  );
}

export function AiWidgetRoot({
  config,
  adapter,
  service,
  className,
}: AiWidgetRootProps) {
  return (
    <AiWidgetProvider config={config}>
      <AiWidgetFrame
        adapter={adapter}
        service={service}
        className={className}
      />
    </AiWidgetProvider>
  );
}
