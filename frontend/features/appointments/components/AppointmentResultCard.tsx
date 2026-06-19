import { format, parse, parseISO } from "date-fns";

import type { AppointmentSearchResult } from "@/features/appointments/types";
import { cn } from "@/lib/utils";

type AppointmentResultCardProps = {
  appointment: AppointmentSearchResult;
  isSelected?: boolean;
  onViewDetails?: (appointmentId: number) => void;
};

function statusLabel(status: AppointmentSearchResult["status"]) {
  switch (status) {
    case "booked":
      return "Booked";
    case "completed":
      return "Completed";
    case "cancelled":
      return "Cancelled";
  }
}

function statusStyles(status: AppointmentSearchResult["status"]) {
  switch (status) {
    case "booked":
      return "bg-sky-50 text-sky-700 ring-1 ring-sky-100";
    case "completed":
      return "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100";
    case "cancelled":
      return "bg-rose-50 text-rose-700 ring-1 ring-rose-100";
  }
}

function appointmentTypeLabel(appointmentType: AppointmentSearchResult["appointment_type"]) {
  return appointmentType === "IN_PERSON" ? "In Person" : "Telemedicine";
}

function formatAppointmentDate(value: string) {
  try {
    return format(parseISO(value), "MMM d, yyyy");
  } catch {
    return value;
  }
}

function formatAppointmentTime(value: string) {
  try {
    return format(parse(value, "HH:mm", new Date()), "h:mm a");
  } catch {
    return value;
  }
}

function PatientAvatar({ name }: { name: string }) {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");

  return (
    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-sky-100 to-cyan-200 text-lg font-semibold text-sky-800 ring-1 ring-slate-200">
      {initials || "AP"}
    </div>
  );
}

export function AppointmentResultCard({
  appointment,
  isSelected = false,
  onViewDetails,
}: AppointmentResultCardProps) {
  return (
    <article
      tabIndex={onViewDetails ? 0 : undefined}
      onClick={() => onViewDetails?.(appointment.appointment_id)}
      onKeyDown={(event) => {
        if (!onViewDetails) {
          return;
        }

        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onViewDetails(appointment.appointment_id);
        }
      }}
      aria-label={`Appointment ${appointment.appointment_id} for ${appointment.patient_name}`}
      aria-pressed={isSelected}
      className={cn(
        "grid cursor-pointer overflow-hidden rounded-[24px] border bg-white shadow-soft transition hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-200 focus-visible:ring-offset-2",
        isSelected ? "border-sky-200 ring-1 ring-sky-100" : "border-slate-200 hover:border-sky-200",
      )}
    >
      <div className="grid gap-5 p-5 sm:grid-cols-[72px_minmax(0,1fr)] sm:p-6">
        <PatientAvatar name={appointment.patient_name} />

        <div className="min-w-0">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <div className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-slate-600">
                Appointment #{appointment.appointment_id}
              </div>
              <h3 className="mt-3 text-2xl font-semibold leading-tight tracking-[-0.04em] text-slate-950">
                {appointment.patient_name}
              </h3>
              <p className="mt-1 text-sm font-medium text-sky-500">
                {appointment.doctor_name}
              </p>
            </div>

            <span
              className={cn(
                "inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em]",
                statusStyles(appointment.status),
              )}
            >
              {statusLabel(appointment.status)}
            </span>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700 ring-1 ring-cyan-100">
              {appointment.doctor_specialty}
            </span>
            <span className="rounded-full bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600 ring-1 ring-slate-200">
              {appointmentTypeLabel(appointment.appointment_type)}
            </span>
          </div>

          <dl className="mt-5 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
            <div>
              <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
                Appointment Date
              </dt>
              <dd className="mt-1 font-medium text-slate-900">
                {formatAppointmentDate(appointment.appointment_date)}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
                Appointment Time
              </dt>
              <dd className="mt-1 font-medium text-slate-900">
                {formatAppointmentTime(appointment.appointment_time)}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
                Patient Email
              </dt>
              <dd className="mt-1 truncate font-medium text-slate-900">
                {appointment.patient_email}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
                Patient Phone
              </dt>
              <dd className="mt-1 font-medium text-slate-900">
                {appointment.patient_phone ?? "Not provided"}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="border-t border-slate-200 px-5 py-4 sm:px-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-slate-500">
            Doctor specialty:{" "}
            <span className="font-semibold text-slate-900">
              {appointment.doctor_specialty}
            </span>
          </p>
          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              onViewDetails?.(appointment.appointment_id);
            }}
            className="inline-flex h-11 items-center justify-center rounded-[14px] border border-slate-200 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-sky-200 hover:text-sky-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-200 focus-visible:ring-offset-2"
          >
            View Details
          </button>
        </div>
      </div>
    </article>
  );
}
