"use client";

import { appointmentTypeOptions, specialtyOptions } from "@/features/doctors/mock-doctors";
import { AppointmentType } from "@/features/doctors/types";

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
    <aside className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
        <FilterIcon />
        <span>Filters</span>
      </div>

      <div className="mt-8">
        <FilterGroupLabel>Specialty</FilterGroupLabel>
        <div className="mt-4 flex flex-col gap-2">
          {specialtyOptions.map((specialty) => {
            const isActive = specialty === selectedSpecialty;

            return (
              <button
                key={specialty}
                type="button"
                onClick={() => onSelectSpecialty(specialty)}
                className={`rounded-2xl px-4 py-3 text-left text-sm transition ${
                  isActive
                    ? "bg-cyan-50 font-semibold text-cyan-800 ring-1 ring-cyan-200"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`}
                aria-pressed={isActive}
              >
                {specialty}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-8">
        <FilterGroupLabel>Appointment Type</FilterGroupLabel>
        <div className="mt-4 flex flex-col gap-2">
          {appointmentTypeOptions.map((option) => {
            const isActive = option.value === selectedAppointmentType;

            return (
              <button
                key={option.value}
                type="button"
                onClick={() => onSelectAppointmentType(option.value)}
                className={`rounded-2xl px-4 py-3 text-left text-sm transition ${
                  isActive
                    ? "bg-cyan-50 font-semibold text-cyan-800 ring-1 ring-cyan-200"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`}
                aria-pressed={isActive}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
