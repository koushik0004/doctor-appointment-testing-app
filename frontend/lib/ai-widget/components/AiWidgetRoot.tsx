"use client";

import { useId } from "react";

import { ChatLauncher } from "@/lib/ai-widget/components/ChatLauncher";
import { ChatWindow } from "@/lib/ai-widget/components/ChatWindow";
import { AiWidgetProvider, useAiWidget } from "@/lib/ai-widget/core";
import { aiWidgetClassNames } from "@/lib/ai-widget/styles";
import type { AiWidgetRootProps } from "@/lib/ai-widget/types";
import { cn } from "@/lib/utils";

function AiWidgetFrame({
  adapter,
  className,
}: Omit<AiWidgetRootProps, "config" | "service">) {
  const { state, dispatch } = useAiWidget();
  const presentation = adapter.getPresentation();
  const quickActions = adapter.getQuickActions?.() ?? [];
  const messageId = useId();

  async function handleSubmit() {
    const nextMessage = state.draft.trim();

    if (!nextMessage) {
      return;
    }

    dispatch({
      type: "startSend",
      payload: {
        id: `user-${messageId}-${state.messages.length + 1}`,
        role: "user",
        content: nextMessage,
        createdAt: new Date().toISOString(),
      },
    });
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
  className,
}: AiWidgetRootProps) {
  return (
    <AiWidgetProvider config={config}>
      <AiWidgetFrame
        adapter={adapter}
        className={className}
      />
    </AiWidgetProvider>
  );
}
