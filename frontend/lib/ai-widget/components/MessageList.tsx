"use client";

import { MessageContentRenderer } from "@/lib/ai-widget/components/MessageContentRenderer";
import type { AiWidgetMessage } from "@/lib/ai-widget/types";

type MessageListProps = {
  messages: AiWidgetMessage[];
  emptyStateLabel: string;
  onBookAppointment?: (doctorId: number) => void;
};

export function MessageList({
  messages,
  emptyStateLabel,
  onBookAppointment,
}: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
        {emptyStateLabel}
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-3 overflow-y-auto pr-1">
      {messages.map((message) => {
        return (
          <div
            key={message.id}
            className={message.role === "user" ? "self-end" : "self-start"}
          >
            <MessageContentRenderer
              message={message}
              onBookAppointment={onBookAppointment}
            />
          </div>
        );
      })}
    </div>
  );
}
