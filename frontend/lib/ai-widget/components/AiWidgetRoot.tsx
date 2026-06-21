"use client";

import { ChatLauncher } from "@/lib/ai-widget/components/ChatLauncher";
import { ChatWindow } from "@/lib/ai-widget/components/ChatWindow";
import { AiWidgetProvider, useAiWidget } from "@/lib/ai-widget/core";
import { createNoopAiWidgetService } from "@/lib/ai-widget/services/noop-service";
import type { AiWidgetRootProps } from "@/lib/ai-widget/types";
import { cn } from "@/lib/utils";

function AiWidgetFrame({
  adapter,
  service = createNoopAiWidgetService(),
  className,
}: Omit<AiWidgetRootProps, "config">) {
  const { state, dispatch } = useAiWidget();
  const presentation = adapter.getPresentation();
  const quickActions = adapter.getQuickActions?.() ?? [];

  async function handleSubmit() {
    if (!state.draft.trim()) {
      return;
    }

    dispatch({
      type: "setError",
      payload:
        "The chat engine is not connected yet. Wire a service implementation in a later step.",
    });

    void service;
  }

  return (
    <div className={cn("fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4", className)}>
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
