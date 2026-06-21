import type { AiWidgetQuickAction } from "@/lib/ai-widget/types/message";

export type AiWidgetPresentation = {
  title: string;
  subtitle?: string;
  launcherLabel: string;
  inputPlaceholder: string;
  emptyStateLabel: string;
};

export interface AiWidgetAdapter {
  getPresentation(): AiWidgetPresentation;
  getQuickActions?(): AiWidgetQuickAction[];
}
