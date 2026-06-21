"use client";

import type { AiWidgetPresentation, AiWidgetQuickAction } from "@/lib/ai-widget/types";
import type { AiWidgetState } from "@/lib/ai-widget/types";
import { MessageComposer } from "@/lib/ai-widget/components/MessageComposer";
import { MessageList } from "@/lib/ai-widget/components/MessageList";
import { aiWidgetClassNames } from "@/lib/ai-widget/styles";
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
        aiWidgetClassNames.panel,
        className,
      )}
    >
      <header className="relative flex items-start justify-between gap-4 overflow-hidden border-b border-slate-100 bg-[linear-gradient(135deg,rgba(14,116,144,0.1),rgba(15,23,42,0.02)_52%,rgba(249,115,22,0.12))] px-5 py-4">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-white/80" />
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
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/70 bg-white/80 text-slate-500 backdrop-blur transition hover:border-slate-300 hover:text-slate-800"
        >
          <span className="sr-only">Close chat widget</span>
          ×
        </button>
      </header>

      <div className="flex h-[32rem] flex-col px-4 py-4 sm:px-5">
        {quickActions.length > 0 ? (
          <div className="mb-4 flex flex-wrap gap-2">
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

        <div className="min-h-0 flex-1">
          <MessageList
            messages={state.messages}
            emptyStateLabel={presentation.emptyStateLabel}
          />
        </div>

        {state.status === "sending" ? (
          <p className="mb-4 mt-4 text-sm text-slate-500" aria-live="polite">
            Assistant is replying...
          </p>
        ) : null}

        {state.errorMessage ? (
          <p
            className="mb-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700"
            aria-live="polite"
          >
            {state.errorMessage}
          </p>
        ) : null}

        <MessageComposer
          value={state.draft}
          placeholder={presentation.inputPlaceholder}
          disabled={state.status === "sending"}
          isSending={state.status === "sending"}
          onChange={onDraftChange}
          onSubmit={onSubmit}
        />
      </div>
    </section>
  );
}
