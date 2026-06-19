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
      return "bg-brand-50 text-brand-700 ring-1 ring-brand-100";
    case "completed":
      return "bg-slate-100 text-slate-700 ring-1 ring-slate-200";
    case "cancelled":
      return "bg-rose-50 text-rose-700 ring-1 ring-rose-100";
  }
}

function appointmentTypeLabel(
  appointmentType: AppointmentSearchResult["appointment_type"],
) {
  return appointmentType === "IN_PERSON" ? "In-Person" : "Telemedicine";
}

function formatAppointmentDate(value: string) {
  try {
    return format(parseISO(value), "EEE, MMM d, yyyy");
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

function getInitials(name: string) {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");

  return initials || "DR";
}

function DoctorAvatar({ name }: { name: string }) {
  return (
    <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-brand-50 text-base font-semibold text-brand-700 ring-1 ring-brand-100">
      {getInitials(name)}
    </div>
  );
}

function MetaItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[14px] border border-slate-100 bg-white px-4 py-3">
      <dt className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
        {label}
      </dt>
      <dd className="mt-1 text-sm font-medium text-slate-900">{value}</dd>
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
      role="button"
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
      aria-label={`Appointment ${appointment.appointment_id} with ${appointment.doctor_name}`}
      aria-pressed={isSelected}
      className={cn(
        "cursor-pointer rounded-[20px] border p-5 text-left shadow-soft transition hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-200 focus-visible:ring-offset-2 sm:p-6",
        isSelected
          ? "border-brand-100 bg-brand-50/60"
          : "border-slate-100 bg-white hover:border-brand-100",
      )}
    >
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-4">
          <DoctorAvatar name={appointment.doctor_name} />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <h3 className="text-2xl font-semibold tracking-[-0.04em] text-slate-950">
                {appointment.doctor_name}
              </h3>
              <span
                className={cn(
                  "rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em]",
                  statusStyles(appointment.status),
                )}
              >
                {statusLabel(appointment.status)}
              </span>
            </div>
            <p className="mt-1 text-base text-brand-600">
              {appointment.doctor_specialty}
            </p>
            <p className="mt-3 text-sm text-slate-500">
              Patient:{" "}
              <span className="font-medium text-slate-900">
                {appointment.patient_name}
              </span>
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            onViewDetails?.(appointment.appointment_id);
          }}
          className="inline-flex h-11 items-center justify-center rounded-[14px] border border-slate-200 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-brand-200 hover:text-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-200 focus-visible:ring-offset-2"
        >
          View Details
        </button>
      </div>

      <dl className="mt-5 grid gap-3 sm:grid-cols-3">
        <MetaItem
          label="Appointment Date"
          value={formatAppointmentDate(appointment.appointment_date)}
        />
        <MetaItem
          label="Appointment Time"
          value={formatAppointmentTime(appointment.appointment_time)}
        />
        <MetaItem
          label="Appointment Type"
          value={appointmentTypeLabel(appointment.appointment_type)}
        />
      </dl>
    </article>
  );
}
