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
      return "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100";
    case "cancelled":
      return "bg-rose-50 text-rose-700 ring-1 ring-rose-100";
  }
}

function appointmentTypeLabel(appointmentType: AppointmentSearchResult["appointment_type"]) {
  return appointmentType === "IN_PERSON" ? "In-Person" : "Telemedicine";
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

function getInitials(name: string) {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");

  return initials || "AP";
}

function DoctorAvatar({ name }: { name: string }) {
  return (
    <div className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-brand-50 to-brand-100 text-base font-semibold text-brand-700 ring-1 ring-slate-200">
      {getInitials(name)}
    </div>
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

function CalendarIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-5 w-5 text-brand-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="4" width="18" height="18" rx="3" />
      <path d="M8 2v4" />
      <path d="M16 2v4" />
      <path d="M3 10h18" />
    </svg>
  );
}

function UserIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-5 w-5 text-brand-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20a8 8 0 0 1 16 0" />
    </svg>
  );
}

function DetailRow({
  label,
  value,
  truncate = false,
}: {
  label: string;
  value: string;
  truncate?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
        {label}
      </dt>
      <dd className={cn("mt-1 text-sm font-medium text-slate-900", truncate ? "truncate" : "")}>
        {value}
      </dd>
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
        "cursor-pointer overflow-hidden rounded-[20px] border border-slate-100 bg-slate-50/80 p-5 text-left shadow-[0_12px_30px_rgba(15,23,42,0.04)] transition hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-200 focus-visible:ring-offset-2",
        isSelected ? "ring-1 ring-brand-100" : "",
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-center gap-4">
          <DoctorAvatar name={appointment.doctor_name} />

          <div className="min-w-0">
            <h3 className="text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              {appointment.doctor_name}
            </h3>
            <p className="mt-1 flex items-center gap-2 text-base text-slate-600">
              <StethoscopeIcon />
              <span>{appointment.doctor_specialty}</span>
            </p>
          </div>
        </div>

        <span
          className={cn(
            "rounded-full px-3 py-1 text-sm font-semibold",
            statusStyles(appointment.status),
          )}
        >
          {statusLabel(appointment.status)}
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-[14px] bg-white p-4 shadow-[0_8px_22px_rgba(15,23,42,0.04)]">
          <div className="flex items-start gap-3">
            <CalendarIcon />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-slate-950">Appointment Details</p>
              <dl className="mt-4 grid gap-4 sm:grid-cols-2">
                <DetailRow label="Appointment ID" value={`#${appointment.appointment_id}`} />
                <DetailRow
                  label="Appointment Date"
                  value={formatAppointmentDate(appointment.appointment_date)}
                />
                <DetailRow
                  label="Appointment Time"
                  value={formatAppointmentTime(appointment.appointment_time)}
                />
                <DetailRow
                  label="Appointment Type"
                  value={appointmentTypeLabel(appointment.appointment_type)}
                />
              </dl>
            </div>
          </div>
        </div>

        <div className="rounded-[14px] bg-white p-4 shadow-[0_8px_22px_rgba(15,23,42,0.04)]">
          <div className="flex items-start gap-3">
            <UserIcon />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-slate-950">Patient Details</p>
              <dl className="mt-4 grid gap-4">
                <DetailRow label="Patient Name" value={appointment.patient_name} />
                <DetailRow
                  label="Patient Email"
                  value={appointment.patient_email}
                  truncate
                />
                <DetailRow
                  label="Patient Phone"
                  value={appointment.patient_phone ?? "Not provided"}
                />
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 flex justify-end">
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
    </article>
  );
}
