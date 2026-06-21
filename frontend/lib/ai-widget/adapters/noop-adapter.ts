import type { AiWidgetAdapter } from "@/lib/ai-widget/types";

export function createNoopAiWidgetAdapter(): AiWidgetAdapter {
  return {
    getPresentation() {
      return {
        title: "AI Assistant",
        subtitle: "Reusable widget foundation",
        launcherLabel: "Open assistant",
        inputPlaceholder: "Chat input will be enabled in a later step.",
        emptyStateLabel: "No conversation yet. Connect an adapter and service to continue.",
      };
    },
    getQuickActions() {
      return [];
    },
  };
}
