"use client";

import { AiWidgetRoot } from "@/lib/ai-widget/components";
import { createNoopAiWidgetAdapter } from "@/lib/ai-widget/adapters";

export function GlobalAiWidget() {
  return <AiWidgetRoot adapter={createNoopAiWidgetAdapter()} />;
}
