"use client";

import {
  appointmentTypeOptions,
  type AppointmentType,
  specialtyOptions,
} from "@/features/doctors/types";

type DoctorFiltersProps = {
  selectedSpecialty: string;
  selectedAppointmentType: AppointmentType | "ALL";
  onSelectSpecialty: (specialty: string) => void;
  onSelectAppointmentType: (appointmentType: AppointmentType | "ALL") => void;
};

function FilterIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-4 w-4 text-slate-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M4 5h16l-6 7v5l-4 2v-7L4 5Z" />
    </svg>
  );
}

function FilterGroupLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
      {children}
    </h2>
  );
}

export function DoctorFilters({
  selectedSpecialty,
  selectedAppointmentType,
  onSelectSpecialty,
  onSelectAppointmentType,
}: DoctorFiltersProps) {
  return (
    <aside className="rounded-none border-r border-slate-200 bg-slate-50 px-6 py-8">
      <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
        <FilterIcon />
        <span>Filters</span>
      </div>

      <div className="mt-8">
        <FilterGroupLabel>Specialty</FilterGroupLabel>
        <nav className="mt-4 flex flex-col gap-1" aria-label="Specialty filters">
          {specialtyOptions.map((specialty) => {
            const isActive = specialty === selectedSpecialty;

            return (
              <button
                key={specialty}
                type="button"
                onClick={() => onSelectSpecialty(specialty)}
                className={`rounded-lg px-2 py-2 text-left text-[0.98rem] transition ${
                  isActive
                    ? "font-semibold text-slate-900"
                    : "text-slate-700 hover:text-slate-900"
                }`}
                aria-pressed={isActive}
              >
                {specialty}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="mt-8">
        <FilterGroupLabel>Appointment Type</FilterGroupLabel>
        <nav className="mt-4 flex flex-col gap-1" aria-label="Appointment type filters">
          {appointmentTypeOptions.map((option) => {
            const isActive = option.value === selectedAppointmentType;

            return (
              <button
                key={option.value}
                type="button"
                onClick={() => onSelectAppointmentType(option.value)}
                className={`rounded-lg px-2 py-2 text-left text-[0.98rem] transition ${
                  isActive
                    ? "font-semibold text-slate-900"
                    : "text-slate-700 hover:text-slate-900"
                }`}
                aria-pressed={isActive}
              >
                {option.label}
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
