"use client";

import type { AiWidgetAppointmentHelpMessageContent } from "@/lib/ai-widget/types";

type AppointmentHelpMessageProps = {
  content: AiWidgetAppointmentHelpMessageContent;
};

function HelpIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5 text-amber-600" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3a9 9 0 1 0 9 9" />
      <path d="M12 8.5v4" />
      <path d="M12 16.5h.01" />
    </svg>
  );
}

export function AppointmentHelpMessage({ content }: AppointmentHelpMessageProps) {
  return (
    <article className="rounded-[22px] border border-amber-100 bg-amber-50/70 p-4 text-amber-950 shadow-[0_12px_32px_rgba(180,83,9,0.08)]">
      <div className="flex items-start gap-3">
        <HelpIcon />
        <div className="min-w-0">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-amber-700">
            {content.title}
          </p>
          <p className="mt-2 text-sm leading-6 text-amber-950">{content.text}</p>
        </div>
      </div>
    </article>
  );
}
