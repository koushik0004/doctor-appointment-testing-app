import { Doctor } from "@/features/doctors/types";

type DoctorCardProps = {
  doctor: Doctor;
  isSelected: boolean;
  onSelect: (doctorId: string) => void;
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
    <span className="inline-flex h-5 w-5 items-center justify-center text-slate-400">
      {children}
    </span>
  );
}

export function DoctorCard({ doctor, isSelected, onSelect }: DoctorCardProps) {
  return (
    <article
      className={`grid overflow-hidden rounded-[28px] border bg-white transition lg:grid-cols-[minmax(0,1fr)_230px] ${
        isSelected
          ? "border-cyan-300 bg-cyan-50/50 shadow-soft"
          : "border-slate-200 hover:border-cyan-200 hover:shadow-soft"
      }`}
    >
      <div className="grid gap-5 p-6 sm:grid-cols-[104px_minmax(0,1fr)] sm:p-7">
        <div
          className={`flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br ${doctor.avatar.accentClassName} text-2xl font-semibold text-cyan-700 ring-1 ring-cyan-100`}
          role="img"
          aria-label={`${doctor.name} avatar`}
        >
          {doctor.avatar.initials}
        </div>

        <div className="min-w-0">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 className="text-[1.8rem] font-semibold leading-none tracking-tight text-slate-950">
                {doctor.name}
              </h2>
              <p className="mt-3 text-lg font-semibold text-cyan-500">
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

          <p className="mt-4 max-w-xl text-sm leading-7 text-slate-600">
            {doctor.description}
          </p>

          <div className="mt-5 flex flex-wrap gap-x-5 gap-y-3 text-sm text-slate-500">
            <div className="flex items-center gap-2">
              <InfoIcon>
                <svg aria-hidden="true" viewBox="0 0 20 20" className="h-4 w-4">
                  <path
                    d="M5 8.5a5 5 0 1 1 10 0c0 3.5-5 7.5-5 7.5s-5-4-5-7.5Zm5-2.75a2.75 2.75 0 1 0 0 5.5 2.75 2.75 0 0 0 0-5.5Z"
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
                    d="M10 1.75a6.75 6.75 0 0 0-6.75 6.75c0 5.04 6 9.75 6.26 9.95a.75.75 0 0 0 .98 0c.26-.2 6.26-4.91 6.26-9.95A6.75 6.75 0 0 0 10 1.75Zm0 9a2.25 2.25 0 1 1 0-4.5 2.25 2.25 0 0 1 0 4.5Z"
                    fill="currentColor"
                  />
                </svg>
              </InfoIcon>
              <span>
                {doctor.clinic}, {doctor.location}
              </span>
            </div>

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
                ${doctor.feeRange.min} - ${doctor.feeRange.max}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200/80 px-6 py-6 lg:border-l lg:border-t-0 lg:px-7">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Next Available
        </p>
        <p className="mt-3 text-xl font-semibold text-slate-900">
          {doctor.nextAvailable}
        </p>
        <button
          type="button"
          onClick={() => onSelect(doctor.id)}
          className={`mt-6 w-full rounded-2xl px-5 py-3 text-sm font-semibold transition ${
            isSelected
              ? "bg-cyan-500 text-white hover:bg-cyan-600"
              : "border border-slate-200 bg-white text-slate-700 hover:border-cyan-200 hover:text-cyan-700"
          }`}
          aria-pressed={isSelected}
        >
          {isSelected ? "Selected" : "Choose time"}
        </button>
      </div>
    </article>
  );
}
