"use client";

import * as React from "react";
import { isBefore, startOfDay } from "date-fns";

import { Calendar } from "@/components/ui/calendar";

type AppointmentCalendarProps = {
  selectedDate: Date | undefined;
  onDateSelect: (date: Date | undefined) => void;
  month?: Date;
  onMonthChange?: (date: Date) => void;
  referenceDate?: Date;
};

export function AppointmentCalendar({
  selectedDate,
  onDateSelect,
  month,
  onMonthChange,
  referenceDate = new Date(),
}: AppointmentCalendarProps) {
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
      disabled={(date) => isBefore(date, minimumSelectableDate)}
    />
  );
}
