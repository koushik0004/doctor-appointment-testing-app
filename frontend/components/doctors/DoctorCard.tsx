import Image from "next/image";
import { Doctor } from "@/features/doctors/types";
import { formatCurrencyInr } from "@/lib/formatters";

type DoctorCardProps = {
  doctor: Doctor;
  isSelected: boolean;
  onSelect: (doctorId: string) => void;
  actionLabel?: string;
  selectedActionLabel?: string;
  variant?: "default" | "featured" | "compact";
};

function StarIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-4 w-4 fill-amber-400 text-amber-400"
    >
      <path d="m12 3.5 2.78 5.64 6.22.9-4.5 4.38 1.06 6.2L12 17.7l-5.56 2.92 1.06-6.2-4.5-4.38 6.22-.9L12 3.5Z" />
    </svg>
  );
}

function InfoIcon({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex h-4 w-4 items-center justify-center text-slate-400">
      {children}
    </span>
  );
}

export function DoctorCard({
  doctor,
  isSelected,
  onSelect,
  actionLabel = "Choose time",
  selectedActionLabel = "Selected",
  variant = "default",
}: DoctorCardProps) {
  const hasFeeRange = doctor.feeRange.min > 0 || doctor.feeRange.max > 0;
  const buttonLabel = isSelected ? selectedActionLabel : actionLabel;

  if (variant === "featured") {
    return (
      <article
        className={`overflow-hidden rounded-[24px] border transition ${
          isSelected
            ? "border-sky-300 bg-sky-100"
            : "border-sky-100 bg-[#dff8ff] hover:border-sky-200"
        }`}
      >
        <div className="grid gap-6 p-6 sm:grid-cols-[120px_minmax(0,1fr)] sm:p-7">
          <div className="relative h-28 w-28 overflow-hidden rounded-full bg-white/80 ring-1 ring-sky-100">
            <Image
              src={doctor.avatar.imageSrc}
              alt={doctor.avatar.imageAlt}
              fill
              className="object-cover"
              sizes="112px"
            />
          </div>

          <div className="min-w-0">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-[2rem] font-semibold leading-[1.05] tracking-[-0.04em] text-slate-900">
                  {doctor.name}
                </h2>
                <p className="mt-2 text-[1.05rem] font-semibold leading-tight text-sky-500">
                  {doctor.specialty}
                </p>
              </div>

              <span className="inline-flex h-10 items-center rounded-full bg-sky-400 px-4 text-xs font-semibold uppercase tracking-[0.14em] text-white">
                Next Available
              </span>
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-3 text-[0.95rem] text-slate-600">
              <div className="flex items-center gap-2">
                <StarIcon />
                <span className="font-semibold text-slate-900">
                  {doctor.rating.toFixed(1)}
                </span>
                <span>({doctor.reviewCount} reviews)</span>
              </div>

              <div className="flex items-center gap-2">
                <InfoIcon>
                  <svg aria-hidden="true" viewBox="0 0 20 20" className="h-4 w-4">
                    <path
                      d="M10 1.75a6.75 6.75 0 0 0-6.75 6.75c0 5.04 6 9.75 6.26 9.95a.75.75 0 0 0 .98 0c.26-.2 6.26-4.91 6.26-9.95A6.75 6.75 0 0 0 10 1.75Zm0 9a2.25 2.25 0 1 1 0-4.5 2.25 2.25 0 0 1 0 4.5Z"
                      fill="currentColor"
                    />
                  </svg>
                </InfoIcon>
                <span>
                  {doctor.clinic}, {doctor.location}
                </span>
              </div>
            </div>

            <div className="mt-6 flex flex-col gap-4 rounded-[18px] bg-white/80 p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Earliest Slot
                </p>
                <p className="mt-1 text-[1.35rem] font-semibold tracking-[-0.03em] text-slate-900">
                  {doctor.nextAvailable}
                </p>
              </div>

              <button
                type="button"
                onClick={() => onSelect(doctor.id)}
                className={`inline-flex h-12 items-center justify-center rounded-[14px] px-6 text-sm font-semibold transition sm:min-w-[156px] ${
                  isSelected
                    ? "bg-sky-500 text-white hover:bg-sky-600"
                    : "bg-sky-400 text-white hover:bg-sky-500"
                }`}
                aria-pressed={isSelected}
              >
                {buttonLabel}
              </button>
            </div>
          </div>
        </div>
      </article>
    );
  }

  if (variant === "compact") {
    return (
      <article
        className={`overflow-hidden rounded-[20px] border bg-white transition ${
          isSelected
            ? "border-sky-300 bg-sky-50/50"
            : "border-slate-200 hover:border-sky-200"
        }`}
      >
        <div className="p-5">
          <div className="flex items-start gap-4">
            <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-full bg-sky-50 ring-1 ring-slate-200">
              <Image
                src={doctor.avatar.imageSrc}
                alt={doctor.avatar.imageAlt}
                fill
                className="object-cover"
                sizes="64px"
              />
            </div>

            <div className="min-w-0 flex-1">
              <h3 className="truncate text-[1.55rem] font-semibold leading-tight tracking-[-0.04em] text-slate-900">
                {doctor.name}
              </h3>
              <p className="mt-1 text-base text-slate-600">{doctor.specialty}</p>
              <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-slate-500">
                <div className="flex items-center gap-1.5">
                  <StarIcon />
                  <span className="font-semibold text-slate-900">
                    {doctor.rating.toFixed(1)}
                  </span>
                  <span>({doctor.reviewCount})</span>
                </div>

                {doctor.appointmentTypes.map((type) => (
                  <span
                    key={type}
                    className={`rounded-full px-2.5 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.08em] ${
                      type === "TELEMEDICINE"
                        ? "bg-sky-50 text-sky-500"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {type === "TELEMEDICINE" ? "Telemedicine" : "In-Person"}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between gap-4 border-t border-slate-200 px-5 py-4">
          <div>
            <p className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-slate-400">
              Available
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-900">
              {doctor.nextAvailable}
            </p>
          </div>

          <button
            type="button"
            onClick={() => onSelect(doctor.id)}
            className={`inline-flex h-11 items-center justify-center rounded-[12px] px-5 text-sm font-semibold transition ${
              isSelected
                ? "bg-sky-400 text-white hover:bg-sky-500"
                : "border border-slate-200 bg-white text-slate-700 hover:border-sky-200 hover:text-sky-700"
            }`}
            aria-pressed={isSelected}
          >
            {buttonLabel}
          </button>
        </div>
      </article>
    );
  }

  return (
    <article
      className={`grid overflow-hidden rounded-[20px] border bg-white transition lg:grid-cols-[minmax(0,1fr)_188px] ${
        isSelected
          ? "border-sky-300 bg-sky-50/60"
          : "border-slate-200 hover:border-sky-200"
      }`}
    >
      <div className="grid gap-5 p-5 sm:grid-cols-[104px_minmax(0,1fr)] sm:p-6">
        <div className="relative h-24 w-24 overflow-hidden rounded-full bg-sky-50 ring-1 ring-slate-200">
          <Image
            src={doctor.avatar.imageSrc}
            alt={doctor.avatar.imageAlt}
            fill
            className="object-cover"
            sizes="96px"
          />
        </div>

        <div className="min-w-0">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 className="text-[2rem] font-semibold leading-[1.05] tracking-[-0.04em] text-slate-900">
                {doctor.name}
              </h2>
              <p className="mt-2 text-[1.05rem] font-semibold leading-tight text-sky-500">
                {doctor.specialty}
              </p>
            </div>

            <div className="flex items-start gap-1 text-sm text-slate-500">
              <StarIcon />
              <span className="font-semibold text-amber-500">
                {doctor.rating.toFixed(1)}
              </span>
              <span>({doctor.reviewCount} reviews)</span>
            </div>
          </div>

          <p className="mt-4 max-w-xl text-[0.95rem] leading-7 text-slate-600">
            {doctor.description}
          </p>

          <div className="mt-4 flex flex-wrap gap-x-4 gap-y-3 text-[0.92rem] text-slate-500">
            <div className="flex items-center gap-2">
              <InfoIcon>
                <svg aria-hidden="true" viewBox="0 0 20 20" className="h-4 w-4">
                  <path
                    d="M10 1.75a6.75 6.75 0 0 0-6.75 6.75c0 5.04 6 9.75 6.26 9.95a.75.75 0 0 0 .98 0c.26-.2 6.26-4.91 6.26-9.95A6.75 6.75 0 0 0 10 1.75Zm0 9a2.25 2.25 0 1 1 0-4.5 2.25 2.25 0 0 1 0 4.5Z"
                    fill="currentColor"
                  />
                </svg>
              </InfoIcon>
              <span>{doctor.languages.join(", ")}</span>
            </div>

            <div className="flex items-center gap-2">
              <InfoIcon>
                <svg aria-hidden="true" viewBox="0 0 20 20" className="h-4 w-4">
                  <path
                    d="M4.5 4.25a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v11.5a1 1 0 0 1-1 1h-9a1 1 0 0 1-1-1V4.25Zm3 1.5a.75.75 0 0 0 0 1.5h5a.75.75 0 0 0 0-1.5h-5Zm0 3a.75.75 0 0 0 0 1.5h5a.75.75 0 0 0 0-1.5h-5Zm0 3a.75.75 0 0 0 0 1.5H11a.75.75 0 0 0 0-1.5H7.5Z"
                    fill="currentColor"
                  />
                </svg>
              </InfoIcon>
              <span>
                {doctor.clinic}, {doctor.location}
              </span>
            </div>

            {hasFeeRange ? (
              <div className="flex items-center gap-2">
                <InfoIcon>
                  <svg aria-hidden="true" viewBox="0 0 20 20" className="h-4 w-4">
                    <path
                      d="M5 3.25A.75.75 0 0 0 4.25 4v12A.75.75 0 0 0 5 16.75h10a.75.75 0 0 0 .75-.75V4a.75.75 0 0 0-.75-.75H5Zm3.5 2.5a.75.75 0 0 1 1.5 0V9.5H13a.75.75 0 0 1 0 1.5h-3V14a.75.75 0 0 1-1.5 0v-3H5.5a.75.75 0 0 1 0-1.5h3V5.75Z"
                      fill="currentColor"
                    />
                  </svg>
                </InfoIcon>
                <span>
                  {formatCurrencyInr(doctor.feeRange.min)} - {formatCurrencyInr(doctor.feeRange.max)}
                </span>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200 px-6 py-6 lg:border-l lg:border-t-0 lg:px-5">
        <p className="text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
          Next Available
        </p>
        <p className="mt-2 text-[1.05rem] font-semibold text-slate-900">
          {doctor.nextAvailable}
        </p>
        <button
          type="button"
          onClick={() => onSelect(doctor.id)}
          className={`mt-5 w-full rounded-[12px] px-4 py-3 text-sm font-semibold transition ${
            isSelected
              ? "bg-sky-400 text-white hover:bg-sky-500"
              : "border border-slate-200 bg-white text-slate-700 hover:border-sky-200 hover:text-sky-700"
          }`}
          aria-pressed={isSelected}
        >
          {buttonLabel}
        </button>
      </div>
    </article>
  );
}
