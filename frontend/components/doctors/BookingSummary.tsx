import Link from "next/link";
import { Doctor } from "@/features/doctors/types";

type BookingSummaryProps = {
  doctor: Doctor | null;
};

function CalendarIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-5 w-5 text-cyan-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="5" width="18" height="16" rx="3" />
      <path d="M16 3v4M8 3v4M3 10h18" />
    </svg>
  );
}

export function BookingSummary({ doctor }: BookingSummaryProps) {
  if (!doctor) {
    return (
      <aside className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
        <div className="flex items-start gap-3">
          <CalendarIcon />
          <div>
            <h2 className="text-2xl font-semibold tracking-tight text-slate-950">
              Booking Summary
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              Select a doctor to preview the consultation details.
            </p>
          </div>
        </div>
      </aside>
    );
  }

  return (
    <div className="space-y-5">
      <aside className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
        <div className="flex items-start gap-3">
          <CalendarIcon />
          <div>
            <h2 className="text-2xl font-semibold tracking-tight text-slate-950">
              Booking Summary
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              Secure your appointment in seconds.
            </p>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-4 rounded-3xl bg-slate-50 p-4">
          <div
            className={`flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br ${doctor.avatar.accentClassName} text-lg font-semibold text-cyan-700`}
            aria-hidden="true"
          >
            {doctor.avatar.initials}
          </div>
          <div>
            <p className="font-semibold text-slate-900">{doctor.name}</p>
            <p className="text-sm text-slate-500">{doctor.specialty}</p>
          </div>
        </div>

        <dl className="mt-6 space-y-4 text-sm">
          <div className="flex items-center justify-between gap-4">
            <dt className="text-slate-500">Consultation Fee</dt>
            <dd className="font-semibold text-slate-900">
              ${doctor.consultationFee}
            </dd>
          </div>
          <div className="flex items-center justify-between gap-4">
            <dt className="text-slate-500">Est. Duration</dt>
            <dd className="font-semibold text-slate-900">
              {doctor.durationMinutes} mins
            </dd>
          </div>
          <div className="flex items-center justify-between gap-4 border-t border-slate-200 pt-4">
            <dt className="text-xl font-semibold text-slate-900">
              Total Estimate
            </dt>
            <dd className="text-2xl font-semibold text-cyan-500">
              ${doctor.consultationFee}
            </dd>
          </div>
        </dl>

        <Link
          href="/appointments"
          className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-cyan-500 px-5 py-4 text-sm font-semibold text-white transition hover:bg-cyan-600"
        >
          Proceed to Booking
        </Link>

        <p className="mt-5 text-center text-xs text-slate-400">
          No payment required until after your consultation.
        </p>
      </aside>

      <aside className="rounded-[28px] border border-cyan-100 bg-cyan-50 p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-500">
          CareNow Guarantee
        </p>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          All doctors on CareNow are board-certified and vetted for quality
          patient care.
        </p>
      </aside>
    </div>
  );
}
