"use client";

import { cn } from "@/lib/utils";
import type { AiWidgetMessage } from "@/lib/ai-widget/types";

type MessageListProps = {
  messages: AiWidgetMessage[];
  emptyStateLabel: string;
};

export function MessageList({
  messages,
  emptyStateLabel,
}: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
        {emptyStateLabel}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {messages.map((message) => {
        const isUser = message.role === "user";

        return (
          <article
            key={message.id}
            className={cn(
              "max-w-[85%] rounded-3xl px-4 py-3 text-sm leading-6 shadow-sm",
              isUser
                ? "self-end bg-slate-950 text-white"
                : "self-start bg-slate-100 text-slate-700",
            )}
          >
            <p>{message.content}</p>
          </article>
        );
      })}
    </div>
  );
}
