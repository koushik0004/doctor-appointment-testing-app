"use client";

import { AiWidgetRoot } from "@/lib/ai-widget/components";
import { createNoopAiWidgetAdapter } from "@/lib/ai-widget/adapters";
import { createApiAiWidgetService } from "@/lib/ai-widget/services";

export function GlobalAiWidget() {
  return (
    <AiWidgetRoot
      adapter={createNoopAiWidgetAdapter()}
      service={createApiAiWidgetService()}
    />
  );
}
