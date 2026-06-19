"use client";

import * as React from "react";
import { format, isBefore, startOfDay } from "date-fns";

import { Calendar } from "@/components/ui/calendar";

type AppointmentCalendarProps = {
  selectedDate: Date | undefined;
  availableDates: Date[];
  onDateSelect: (date: Date | undefined) => void;
  month?: Date;
  onMonthChange?: (date: Date) => void;
  referenceDate?: Date;
};

function toDateKey(date: Date) {
  return format(date, "yyyy-MM-dd");
}

export function AppointmentCalendar({
  selectedDate,
  availableDates,
  onDateSelect,
  month,
  onMonthChange,
  referenceDate = new Date(),
}: AppointmentCalendarProps) {
  const availableDateKeys = React.useMemo(() => {
    return new Set(availableDates.map(toDateKey));
  }, [availableDates]);

  const minimumSelectableDate = React.useMemo(() => {
    return startOfDay(referenceDate);
  }, [referenceDate]);

  return (
    <Calendar
      mode="single"
      selected={selectedDate}
      onSelect={onDateSelect}
      month={month}
      onMonthChange={onMonthChange}
      required
      className="w-full rounded-[20px] border border-slate-200 bg-white p-6 shadow-soft"
      classNames={{
        months: "flex flex-col gap-4",
        month: "space-y-4",
        month_caption: "hidden",
        caption_label: "hidden",
        nav: "hidden",
        button_previous: "hidden",
        button_next: "hidden",
        month_grid: "w-full border-collapse space-y-1",
        weekday: "h-10 w-12 text-center text-sm font-semibold text-slate-500",
        day: "h-12 w-12 p-0",
        day_button:
          "h-12 w-12 rounded-[14px] text-base font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-300 focus-visible:ring-offset-2",
        selected:
          "bg-brand-500 text-white shadow-[0_12px_24px_rgba(6,182,212,0.32)] hover:bg-brand-500 hover:text-white",
        today: "border border-brand-200 bg-brand-50 text-brand-700",
        outside: "text-slate-300 opacity-40",
        disabled: "cursor-not-allowed text-slate-300 opacity-35",
        hidden: "invisible",
      }}
      modifiers={{
        available: (date) => availableDateKeys.has(toDateKey(date)),
      }}
      modifiersClassNames={{
        available:
          "border border-brand-200 bg-brand-50 text-brand-600 font-semibold shadow-[0_8px_18px_rgba(6,182,212,0.08)]",
      }}
      disabled={(date) =>
        isBefore(date, minimumSelectableDate) ||
        !availableDateKeys.has(toDateKey(date))
      }
    />
  );
}
