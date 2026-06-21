"use client";

import { format, parseISO } from "date-fns";
import { useRouter } from "next/navigation";

import { buildAppointmentBookingUrl } from "@/lib/ai-widget/services/appointment-navigation";
import type { AiWidgetAvailabilityCardContent } from "@/lib/ai-widget/types";
import { cn } from "@/lib/utils";

type AvailabilityMessageProps = {
  slot: AiWidgetAvailabilityCardContent;
  onBookAppointment?: (doctorId: number) => void;
};

function TimeIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 8.5v4l2.5 1.5" />
    </svg>
  );
}

export function AvailabilityMessage({
  slot,
  onBookAppointment,
}: AvailabilityMessageProps) {
  const router = useRouter();
  const formattedDate = format(parseISO(slot.availableDate), "EEEE, MMMM d, yyyy");
  const isBookableDoctor = Number.isFinite(slot.doctorId) && slot.doctorId > 0;

  function handleBookAppointment() {
    if (!isBookableDoctor) {
      return;
    }

    onBookAppointment?.(slot.doctorId);
    router.push(buildAppointmentBookingUrl(slot.doctorId));
  }

  return (
    <article className="rounded-[22px] border border-slate-200 bg-white p-4 shadow-[0_12px_32px_rgba(15,23,42,0.08)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Doctor Name
          </p>
          <h3 className="mt-1 text-base font-semibold tracking-[-0.02em] text-slate-950">
            {slot.doctorName}
          </h3>
          <p className="mt-1 text-sm text-slate-500">{slot.specialization}</p>
        </div>

        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
          <TimeIcon />
          Available
        </span>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-[16px] bg-slate-50 p-4">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Available Date
          </p>
          <p className="mt-2 text-sm font-medium text-slate-900">
            {formattedDate}
          </p>
        </div>

        <div className="rounded-[16px] bg-slate-50 p-4">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Available Time
          </p>
          <p className="mt-2 text-sm font-medium text-slate-900">
            {slot.availableTime}
          </p>
        </div>
      </div>

      <div className="mt-4 border-t border-slate-100 pt-4">
        <button
          type="button"
          onClick={handleBookAppointment}
          disabled={!isBookableDoctor}
          className={cn(
            "inline-flex w-full items-center justify-center rounded-full bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800",
            !isBookableDoctor && "cursor-not-allowed bg-slate-300 text-slate-500 hover:bg-slate-300",
          )}
        >
          Book Appointment
        </button>
      </div>
    </article>
  );
}
