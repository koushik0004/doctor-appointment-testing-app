"use client";

import { format } from "date-fns";

import { cn } from "@/lib/utils";
import type { AppointmentSlot } from "@/features/appointments/types";

type AppointmentAvailabilityProps = {
  selectedDate: Date | undefined;
  selectedSlot: string | null;
  availableSlots: AppointmentSlot[];
  onSlotSelect: (slot: string) => void;
};

const slotGroups = [
  {
    label: "Morning",
    heading: "MORNING",
    times: ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM"],
  },
  {
    label: "Afternoon",
    heading: "AFTERNOON",
    times: ["02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM"],
  },
] as const;

function TimeSlotIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-6 w-6 text-brand-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="8" />
      <path d="M12 8v4l3 2" />
    </svg>
  );
}

export function AppointmentAvailability({
  selectedDate,
  selectedSlot,
  availableSlots,
  onSlotSelect,
}: AppointmentAvailabilityProps) {
  const availableSlotMap = new Map(
    availableSlots.map((slot) => [slot.time, slot.available]),
  );

  return (
    <section className="rounded-[20px] border border-slate-100 bg-white p-6 shadow-soft">
      <div className="flex items-start gap-3">
        <TimeSlotIcon />
        <div>
          <h2 className="text-2xl font-semibold tracking-[-0.04em] text-slate-950">
            Appointment Availability
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Select an open time slot for{" "}
            <span className="font-medium text-slate-900">
              {selectedDate
                ? format(selectedDate, "EEEE, MMMM d, yyyy")
                : "the selected date"}
            </span>
            .
          </p>
        </div>
      </div>

      <div className="mt-8 space-y-8">
        {slotGroups.map((group) => (
          <div key={group.label}>
            <h3 className="mb-4 text-lg font-semibold tracking-[-0.03em] text-slate-600">
              {group.heading}
            </h3>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {group.times.map((time) => {
                const isAvailable = availableSlotMap.get(time) ?? false;
                const isSelected = selectedSlot === time;
                const isBooked = !isAvailable;

                return (
                  <button
                    key={time}
                    type="button"
                    onClick={() => {
                      if (isAvailable) {
                        onSlotSelect(time);
                      }
                    }}
                    disabled={isBooked}
                    aria-pressed={isSelected}
                    className={cn(
                      "relative h-12 rounded-[12px] border px-4 text-base font-semibold transition",
                      isSelected && isAvailable
                        ? "border-brand-500 bg-brand-500 text-white shadow-[0_10px_22px_rgba(6,182,212,0.24)]"
                        : isBooked
                          ? "cursor-not-allowed border-slate-200 bg-slate-50 text-slate-300"
                          : "border-slate-200 bg-white text-slate-900 hover:border-brand-100 hover:bg-brand-50/60",
                    )}
                  >
                    <span>{time}</span>
                    {isBooked ? (
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-300">
                        Booked
                      </span>
                    ) : null}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

