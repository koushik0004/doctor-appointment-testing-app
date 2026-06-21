"use client";

import { useRouter } from "next/navigation";

import { formatCurrencyInr } from "@/lib/formatters";
import { buildAppointmentBookingUrl } from "@/lib/ai-widget/services/appointment-navigation";
import { cn } from "@/lib/utils";
import type { AiWidgetDoctorCardContent } from "@/lib/ai-widget/types";

type DoctorCardMessageProps = {
  doctor: AiWidgetDoctorCardContent;
  onBookAppointment?: (doctorId: number) => void;
};

function DoctorBadgeIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3v18" />
      <path d="M3 12h18" />
      <path d="M7 7h10v10H7z" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 10.5v5" />
      <path d="M12 7.5h.01" />
    </svg>
  );
}

export function DoctorCardMessage({
  doctor,
  onBookAppointment,
}: DoctorCardMessageProps) {
  const router = useRouter();
  const isBookableDoctor = Number.isFinite(doctor.doctorId) && doctor.doctorId > 0;

  function handleBookAppointment() {
    if (!isBookableDoctor) {
      return;
    }

    onBookAppointment?.(doctor.doctorId);
    router.push(buildAppointmentBookingUrl(doctor.doctorId));
  }

  return (
    <article className="overflow-hidden rounded-[24px] border border-slate-200 bg-white shadow-[0_14px_36px_rgba(15,23,42,0.08)]">
      <div className="border-b border-slate-100 bg-[linear-gradient(135deg,rgba(14,116,144,0.08),rgba(249,115,22,0.08))] px-4 py-4">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-slate-500">
              Doctor Name
            </p>
            <h3 className="mt-1 text-lg font-semibold tracking-[-0.03em] text-slate-950">
              {doctor.doctorName}
            </h3>
            <p className="mt-1 text-sm text-slate-600">{doctor.clinicName}</p>
          </div>

          <span className="inline-flex items-center gap-1 rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">
            <DoctorBadgeIcon />
            {doctor.specialization}
          </span>
        </div>
      </div>

      <div className="grid gap-3 px-4 py-4 sm:grid-cols-2">
        <div className="rounded-[18px] bg-slate-50 p-4">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Specialization
          </p>
          <p className="mt-2 text-sm font-medium text-slate-900">
            {doctor.specialization}
          </p>
        </div>

        <div className="rounded-[18px] bg-slate-50 p-4">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Consultation Fee
          </p>
          <p className="mt-2 text-sm font-medium text-slate-900">
            {formatCurrencyInr(doctor.consultationFeeMin)} -{" "}
            {formatCurrencyInr(doctor.consultationFeeMax)}
          </p>
        </div>

        <div className="rounded-[18px] bg-slate-50 p-4">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Next Available Slot
          </p>
          <p className="mt-2 text-sm font-medium text-slate-900">
            {doctor.nextAvailableSlot}
          </p>
        </div>

        <div className="rounded-[18px] bg-slate-50 p-4">
          <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Clinic Location
          </p>
          <p className="mt-2 text-sm font-medium text-slate-900">
            {doctor.location}
          </p>
        </div>
      </div>

      <div className="border-t border-slate-100 px-4 py-4">
        <button
          type="button"
          onClick={handleBookAppointment}
          disabled={!isBookableDoctor}
          className={cn(
            "inline-flex w-full items-center justify-center gap-2 rounded-full bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800",
            !isBookableDoctor && "cursor-not-allowed bg-slate-300 text-slate-500 hover:bg-slate-300",
          )}
        >
          <InfoIcon />
          Book Appointment
        </button>
      </div>
    </article>
  );
}
