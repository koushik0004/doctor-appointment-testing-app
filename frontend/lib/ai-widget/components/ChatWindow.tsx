"use client";

import type { AiWidgetPresentation, AiWidgetQuickAction } from "@/lib/ai-widget/types";
import type { AiWidgetState } from "@/lib/ai-widget/types";
import { MessageComposer } from "@/lib/ai-widget/components/MessageComposer";
import { MessageList } from "@/lib/ai-widget/components/MessageList";
import { cn } from "@/lib/utils";

type ChatWindowProps = {
  presentation: AiWidgetPresentation;
  quickActions: AiWidgetQuickAction[];
  state: AiWidgetState;
  className?: string;
  onClose: () => void;
  onDraftChange: (value: string) => void;
  onSubmit: () => void;
};

export function ChatWindow({
  presentation,
  quickActions,
  state,
  className,
  onClose,
  onDraftChange,
  onSubmit,
}: ChatWindowProps) {
  return (
    <section
      aria-label={presentation.title}
      className={cn(
        "flex w-full max-w-sm flex-col overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-[0_24px_80px_rgba(15,23,42,0.18)]",
        className,
      )}
    >
      <header className="flex items-start justify-between gap-4 border-b border-slate-100 px-5 py-4">
        <div>
          <p className="text-base font-semibold text-slate-950">
            {presentation.title}
          </p>
          {presentation.subtitle ? (
            <p className="mt-1 text-sm text-slate-500">{presentation.subtitle}</p>
          ) : null}
        </div>
        <button
          type="button"
          onClick={onClose}
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition hover:border-slate-300 hover:text-slate-800"
        >
          <span className="sr-only">Close chat widget</span>
          ×
        </button>
      </header>

      <div className="flex flex-col gap-5 px-5 py-4">
        {quickActions.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {quickActions.map((action) => (
              <button
                key={action.id}
                type="button"
                disabled
                className="rounded-full border border-slate-200 px-3 py-2 text-xs font-medium text-slate-500"
              >
                {action.label}
              </button>
            ))}
          </div>
        ) : null}

        <MessageList
          messages={state.messages}
          emptyStateLabel={presentation.emptyStateLabel}
        />

        {state.errorMessage ? (
          <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {state.errorMessage}
          </p>
        ) : null}

        <MessageComposer
          value={state.draft}
          placeholder={presentation.inputPlaceholder}
          disabled
          onChange={onDraftChange}
          onSubmit={onSubmit}
        />
      </div>
    </section>
  );
}
