"use client";

import { format } from "date-fns";

import { cn } from "@/lib/utils";
import type { AvailabilitySlot } from "@/features/appointments/types";
import { formatAppointmentTime } from "@/features/appointments/utils";

type AppointmentAvailabilityProps = {
  selectedDate: Date | undefined;
  selectedSlotId: number | null;
  availableSlots: AvailabilitySlot[];
  onSlotSelect: (slot: AvailabilitySlot) => void;
};

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
  selectedSlotId,
  availableSlots,
  onSlotSelect,
}: AppointmentAvailabilityProps) {
  const morningSlots = availableSlots.filter(
    (slot) => Number(slot.startTime.slice(0, 2)) < 12,
  );
  const afternoonSlots = availableSlots.filter(
    (slot) => Number(slot.startTime.slice(0, 2)) >= 12,
  );

  if (!selectedDate) {
    return (
      <section className="rounded-[20px] border border-slate-100 bg-white p-6 shadow-soft">
        <div className="flex items-start gap-3">
          <TimeSlotIcon />
          <div>
            <h2 className="text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              Appointment Availability
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Select a date to see available appointment times.
            </p>
          </div>
        </div>
      </section>
    );
  }

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
        {[
          { label: "Morning", heading: "MORNING", slots: morningSlots },
          { label: "Afternoon", heading: "AFTERNOON", slots: afternoonSlots },
        ].map((group) => (
          <div key={group.label}>
            <h3 className="mb-4 text-lg font-semibold tracking-[-0.03em] text-slate-600">
              {group.heading}
            </h3>
            {group.slots.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {group.slots.map((slot) => {
                  const isSelected = selectedSlotId === slot.id;
                  const isBooked = slot.isBooked;
                  const timeLabel = formatAppointmentTime(slot.startTime);

                  return (
                    <button
                      key={slot.id}
                      type="button"
                      onClick={() => {
                        if (!isBooked) {
                          onSlotSelect(slot);
                        }
                      }}
                      disabled={isBooked}
                      aria-pressed={isSelected}
                      className={cn(
                        "relative h-12 rounded-[12px] border px-4 text-base font-semibold transition",
                        isSelected && !isBooked
                          ? "border-brand-500 bg-brand-500 text-white shadow-[0_10px_22px_rgba(6,182,212,0.24)]"
                          : isBooked
                            ? "cursor-not-allowed border-slate-200 bg-slate-50 text-slate-300"
                            : "border-slate-200 bg-white text-slate-900 hover:border-brand-100 hover:bg-brand-50/60",
                      )}
                    >
                      <span>{timeLabel}</span>
                      {isBooked ? (
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-300">
                          Booked
                        </span>
                      ) : null}
                    </button>
                  );
                })}
              </div>
            ) : (
              <p className="rounded-[14px] border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500">
                No {group.label.toLowerCase()} slots are available for the selected date.
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
