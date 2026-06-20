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
    <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-white text-base font-semibold text-brand-700 ring-1 ring-brand-100">
      {getInitials(name)}
    </div>
  );
}

function MetaItem({
  label,
  value,
  isSelected = false,
}: {
  label: string;
  value: string;
  isSelected?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-[16px] border px-4 py-3.5 shadow-[0_8px_24px_rgba(15,23,42,0.04)]",
        isSelected
          ? "border-brand-100 bg-white"
          : "border-slate-100 bg-white",
      )}
    >
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
        "cursor-pointer rounded-[22px] border p-5 text-left shadow-[0_12px_30px_rgba(15,23,42,0.04)] transition hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-200 focus-visible:ring-offset-2 sm:p-6",
        isSelected
          ? "border-brand-100 bg-brand-50/65"
          : "border-slate-100 bg-slate-50/80 hover:border-brand-100",
      )}
    >
      <div className="flex items-start gap-4">
        <DoctorAvatar name={appointment.doctor_name} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="text-xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-2xl">
                {appointment.doctor_name}
              </h3>
              <p className="mt-1 text-sm font-medium text-brand-600 sm:text-base">
                {appointment.doctor_specialty}
              </p>
            </div>
            <span
              className={cn(
                "rounded-full px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.14em]",
                statusStyles(appointment.status),
              )}
            >
              {statusLabel(appointment.status)}
            </span>
          </div>
        </div>
      </div>

      <dl className="mt-5 grid gap-3 sm:grid-cols-3">
        <MetaItem
          label="Appointment Date"
          value={formatAppointmentDate(appointment.appointment_date)}
          isSelected={isSelected}
        />
        <MetaItem
          label="Appointment Time"
          value={formatAppointmentTime(appointment.appointment_time)}
          isSelected={isSelected}
        />
        <MetaItem
          label="Appointment Type"
          value={appointmentTypeLabel(appointment.appointment_type)}
          isSelected={isSelected}
        />
      </dl>

      <div className="mt-5 flex flex-col gap-4 border-t border-slate-200 pt-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <p className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Patient Name
          </p>
          <p className="mt-1 truncate text-sm font-medium text-slate-900 sm:text-base">
            {appointment.patient_name}
          </p>
        </div>

        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            onViewDetails?.(appointment.appointment_id);
          }}
          className={cn(
            "inline-flex h-11 items-center justify-center rounded-[14px] px-5 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-200 focus-visible:ring-offset-2",
            isSelected
              ? "bg-brand-600 text-white hover:bg-brand-700"
              : "border border-brand-100 bg-white text-brand-700 hover:bg-brand-50",
          )}
        >
          {isSelected ? "Viewing Details" : "View Details"}
        </button>
      </div>
    </article>
  );
}
