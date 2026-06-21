import type { AiWidgetAdapter } from "@/lib/ai-widget/types";

export function createNoopAiWidgetAdapter(): AiWidgetAdapter {
  return {
    getPresentation() {
      return {
        title: "Doctor Appointment Assistant",
        subtitle: "Ask about doctors, schedules, and bookings.",
        launcherLabel: "Open assistant",
        inputPlaceholder: "Type your message here...",
        emptyStateLabel: "Start the conversation with the assistant.",
      };
    },
    getQuickActions() {
      return [];
    },
  };
}
