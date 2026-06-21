import type { ReactNode } from "react";

import type { AiWidgetAdapter } from "@/lib/ai-widget/types/adapter";
import type { AiWidgetMessage } from "@/lib/ai-widget/types/message";
import type { AiWidgetService } from "@/lib/ai-widget/types/service";

export type AiWidgetStatus = "idle" | "sending" | "error";

export type AiWidgetState = {
  isOpen: boolean;
  status: AiWidgetStatus;
  messages: AiWidgetMessage[];
  draft: string;
  errorMessage: string | null;
};

export type AiWidgetConfig = {
  id?: string;
  initialOpen?: boolean;
  initialMessages?: AiWidgetMessage[];
};

export type AiWidgetProviderProps = {
  children: ReactNode;
  config?: AiWidgetConfig;
};

export type AiWidgetRootProps = {
  config?: AiWidgetConfig;
  adapter: AiWidgetAdapter;
  service?: AiWidgetService;
  className?: string;
  onBookAppointment?: (doctorId: number) => void;
};
