import Image from "next/image";
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
      <aside className="rounded-[16px] border border-slate-200 bg-white p-6">
        <div className="flex items-start gap-3">
          <CalendarIcon />
          <div>
            <h2 className="text-[2rem] font-semibold tracking-[-0.04em] text-slate-900">
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
      <aside className="rounded-[16px] border border-slate-200 bg-white p-6">
        <div className="flex items-start gap-3">
          <CalendarIcon />
          <div>
            <h2 className="text-[2rem] font-semibold tracking-[-0.04em] text-slate-900">
              Booking Summary
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              Secure your appointment in seconds.
            </p>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-3 rounded-[14px] border border-slate-200 bg-slate-50 px-3 py-3">
          <div className="relative h-11 w-11 overflow-hidden rounded-full bg-sky-50 ring-1 ring-slate-200">
            <Image
              src={doctor.avatar.imageSrc}
              alt={doctor.avatar.imageAlt}
              fill
              className="object-cover"
              sizes="44px"
            />
          </div>
          <div>
            <p className="font-semibold text-slate-900">{doctor.name}</p>
            <p className="text-sm text-slate-500">Senior {doctor.specialty}</p>
          </div>
        </div>

        <dl className="mt-6 space-y-4 text-sm">
          <div className="flex items-center justify-between gap-4">
            <dt className="text-slate-500">Fee Range</dt>
            <dd className="font-semibold text-slate-900">
              ${doctor.feeRange.min} - ${doctor.feeRange.max}
            </dd>
          </div>
          <div className="flex items-center justify-between gap-4">
            <dt className="text-slate-500">Next Available</dt>
            <dd className="font-semibold text-slate-900">{doctor.nextAvailable}</dd>
          </div>
          <div className="flex items-center justify-between gap-4 border-t border-slate-200 pt-4">
            <dt className="text-xl font-semibold text-slate-900">Starting From</dt>
            <dd className="text-2xl font-semibold text-cyan-500">
              ${doctor.feeRange.min}
            </dd>
          </div>
        </dl>

        <Link
          href={
            doctor ? `/appointments?doctorId=${doctor.backendId}` : "/appointments"
          }
          className="mt-6 inline-flex w-full items-center justify-center rounded-[12px] bg-sky-400 px-5 py-4 text-sm font-semibold text-white transition hover:bg-sky-500"
        >
          Proceed to Booking
        </Link>

        <p className="mt-5 text-center text-xs text-slate-400">
          No payment required until after your consultation.
        </p>
      </aside>

      <aside className="rounded-[16px] border border-sky-100 bg-sky-50/70 p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-500">
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
