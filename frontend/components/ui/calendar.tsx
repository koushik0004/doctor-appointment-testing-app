"use client";

import * as React from "react";
import { DayPicker, getDefaultClassNames } from "react-day-picker";

import { cn } from "@/lib/utils";

export type CalendarProps = React.ComponentProps<typeof DayPicker>;

export function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: CalendarProps) {
  const defaultClassNames = getDefaultClassNames();

  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-3", className)}
      classNames={{
        ...defaultClassNames,
        months: "flex flex-col gap-4 sm:flex-row",
        month: "space-y-4",
        month_caption: "flex items-center justify-between gap-4 px-2 pb-4",
        caption_label: "text-base font-semibold tracking-[-0.03em]",
        nav: "flex items-center gap-2",
        button_previous:
          "inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 transition hover:border-brand-200 hover:text-brand-500",
        button_next:
          "inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 transition hover:border-brand-200 hover:text-brand-500",
        month_grid: "w-full border-collapse space-y-1",
        weekday:
          "h-10 w-12 text-center text-xs font-semibold uppercase tracking-[0.12em] text-slate-500",
        day: "h-12 w-12 p-0",
        day_button:
          "h-12 w-12 rounded-[14px] text-base font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-300 focus-visible:ring-offset-2",
        selected:
          "bg-brand-500 text-white shadow-[0_12px_24px_rgba(6,182,212,0.32)] hover:bg-brand-500 hover:text-white",
        today: "border border-brand-200 bg-brand-50 text-brand-700",
        outside: "text-slate-300 opacity-50",
        disabled: "cursor-not-allowed text-slate-300 opacity-40",
        hidden: "invisible",
        ...classNames,
      }}
      components={{
        Chevron: ({ ...chevronProps }) => (
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...chevronProps}
          >
            <path d="m9 18 6-6-6-6" />
          </svg>
        ),
      }}
      {...props}
    />
  );
}
