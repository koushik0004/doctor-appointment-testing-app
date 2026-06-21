"use client";

import type { AiWidgetSearchFilterChip } from "@/lib/ai-widget/types";
import { cn } from "@/lib/utils";

type SearchFilterSummaryProps = {
  countLabel?: string;
  filters: AiWidgetSearchFilterChip[];
  className?: string;
};

export function SearchFilterSummary({
  countLabel,
  filters,
  className,
}: SearchFilterSummaryProps) {
  if (!countLabel && filters.length === 0) {
    return null;
  }

  return (
    <div
      className={cn(
        "rounded-[20px] border border-cyan-100 bg-cyan-50/70 px-4 py-3",
        className,
      )}
    >
      {countLabel ? (
        <p className="text-sm font-semibold tracking-[-0.01em] text-cyan-950">
          {countLabel}
        </p>
      ) : null}

      {filters.length > 0 ? (
        <div className={cn("mt-3 flex flex-wrap gap-2", !countLabel && "mt-0")}>
          {filters.map((filter) => (
            <div
              key={`${filter.label}-${filter.value}`}
              className="min-w-[7rem] rounded-2xl border border-cyan-100 bg-white px-3 py-2 shadow-sm"
            >
              <p className="text-[0.65rem] font-semibold uppercase tracking-[0.18em] text-cyan-700">
                {filter.label}
              </p>
              <p className="mt-1 text-sm font-medium text-slate-950">
                {filter.value}
              </p>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
