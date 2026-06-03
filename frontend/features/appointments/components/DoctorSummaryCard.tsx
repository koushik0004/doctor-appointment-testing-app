import Image from "next/image";
import type { Doctor } from "@/features/doctors/types";

type DoctorSummaryCardProps = {
  doctor: Doctor;
  waitTimeLabel?: string;
  ratingLabel?: string;
};

function LocationIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="mt-0.5 h-4 w-4 text-brand-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 21s7-4.35 7-10a7 7 0 1 0-14 0c0 5.65 7 10 7 10Z" />
      <circle cx="12" cy="11" r="2.5" />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="mt-0.5 h-4 w-4 text-brand-500"
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

function StethoscopeIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-5 w-5 text-slate-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 3v5a3 3 0 0 0 6 0V3" />
      <path d="M12 8v4a5 5 0 0 0 10 0v-1" />
      <path d="M18 15v2a4 4 0 0 1-8 0v-1" />
      <circle cx="6" cy="20" r="1.5" />
      <circle cx="18" cy="15" r="1.5" />
    </svg>
  );
}

export function DoctorSummaryCard({
  doctor,
  waitTimeLabel = "15 min avg. wait",
  ratingLabel,
}: DoctorSummaryCardProps) {
  const displayedRatingLabel = ratingLabel ?? "Highly Rated";

  return (
    <aside className="rounded-[20px] border border-slate-100 bg-slate-50/80 p-5 shadow-[0_12px_30px_rgba(15,23,42,0.04)]">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="relative h-14 w-14 overflow-hidden rounded-full bg-slate-200 ring-1 ring-slate-200">
            <Image
              src={doctor.avatar.imageSrc}
              alt={doctor.avatar.imageAlt}
              fill
              sizes="56px"
              className="object-cover"
            />
          </div>
          <div>
            <h2 className="text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              {doctor.name}
            </h2>
            <p className="mt-1 flex items-center gap-2 text-base text-slate-600">
              <StethoscopeIcon />
              <span>{doctor.specialty} Specialist</span>
            </p>
          </div>
        </div>

        <span className="rounded-full bg-brand-100 px-3 py-1 text-sm font-semibold text-brand-600">
          {displayedRatingLabel}
        </span>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div className="rounded-[14px] bg-white p-4 shadow-[0_8px_22px_rgba(15,23,42,0.04)]">
          <div className="flex items-start gap-2 text-slate-600">
            <LocationIcon />
            <p className="text-sm leading-6">
              {doctor.clinic}
              <br />
              {doctor.location}
            </p>
          </div>
        </div>

        <div className="rounded-[14px] bg-white p-4 shadow-[0_8px_22px_rgba(15,23,42,0.04)]">
          <div className="flex items-start gap-2 text-slate-600">
            <ClockIcon />
            <p className="text-sm leading-6">{waitTimeLabel}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
