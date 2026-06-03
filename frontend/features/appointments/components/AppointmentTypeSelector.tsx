"use client";

import { cn } from "@/lib/utils";

import type { AppointmentType } from "@/features/appointments/types";

type AppointmentTypeSelectorProps = {
  value: AppointmentType;
  onChange: (value: AppointmentType) => void;
  name?: string;
  className?: string;
};

const options: Array<{
  value: AppointmentType;
  label: string;
  description: string;
}> = [
  {
    value: "IN_PERSON",
    label: "In Person",
    description: "Visit the clinic at your selected time.",
  },
  {
    value: "TELEMEDICINE",
    label: "Telemedicine",
    description: "Join a secure video consultation.",
  },
];

function InPersonIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14 9V5a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v14a3 3 0 0 0 3 3h5a3 3 0 0 0 3-3v-4" />
      <path d="M21 12h-6" />
      <path d="M18 9l3 3-3 3" />
    </svg>
  );
}

function TelemedicineIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="6" width="14" height="12" rx="2" />
      <path d="M17 10l4-2v8l-4-2" />
    </svg>
  );
}

export function AppointmentTypeSelector({
  value,
  onChange,
  name = "appointment_type",
  className,
}: AppointmentTypeSelectorProps) {
  return (
    <fieldset className={cn("space-y-3", className)}>
      <legend className="text-sm font-semibold text-slate-900">
        Appointment Type
      </legend>

      <div className="grid gap-3 sm:grid-cols-2">
        {options.map((option) => {
          const checked = value === option.value;

          return (
            <label
              key={option.value}
              htmlFor={`${name}-${option.value}`}
              className={cn(
                "group flex cursor-pointer items-start gap-3 rounded-[14px] border px-4 py-4 transition",
                checked
                  ? "border-brand-200 bg-brand-50/70 shadow-[0_8px_20px_rgba(6,182,212,0.10)]"
                  : "border-slate-200 bg-white hover:border-brand-100 hover:bg-brand-50/40",
              )}
            >
              <input
                id={`${name}-${option.value}`}
                name={name}
                type="radio"
                value={option.value}
                checked={checked}
                onChange={() => onChange(option.value)}
                className="sr-only"
              />

              <span
                className={cn(
                  "mt-0.5 inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition",
                  checked ? "bg-brand-500 text-white" : "bg-slate-100 text-slate-500",
                )}
              >
                {option.value === "IN_PERSON" ? (
                  <InPersonIcon />
                ) : (
                  <TelemedicineIcon />
                )}
              </span>

              <span className="min-w-0">
                <span className="block text-sm font-semibold text-slate-950">
                  {option.label}
                </span>
                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  {option.description}
                </span>
              </span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
