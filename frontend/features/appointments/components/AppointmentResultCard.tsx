import type { ReactNode } from "react";

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
    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-brand-50 to-brand-100 text-lg font-semibold text-brand-700 ring-1 ring-slate-200">
      {getInitials(name)}
    </div>
  );
}

function SectionTitle({ children }: { children: string }) {
  return (
    <h4 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
      {children}
    </h4>
  );
}

function InfoList({
  children,
}: {
  children: ReactNode;
}) {
  return <dl className="grid gap-3 text-sm text-slate-600 sm:grid-cols-2">{children}</dl>;
}

function InfoItem({
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
      <dd className={cn("mt-1 font-medium text-slate-900", truncate ? "truncate" : "")}>
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
        "grid cursor-pointer overflow-hidden rounded-[24px] border bg-white shadow-soft transition hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
        isSelected
          ? "border-brand-200 ring-1 ring-brand-100 focus-visible:ring-brand-200"
          : "border-slate-200 hover:border-brand-200 focus-visible:ring-brand-200",
      )}
    >
      <div className="grid gap-5 p-5 sm:grid-cols-[72px_minmax(0,1fr)] sm:p-6">
        <DoctorAvatar name={appointment.doctor_name} />

        <div className="min-w-0">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <h3 className="mt-3 text-2xl font-semibold leading-tight tracking-[-0.04em] text-slate-950">
                {appointment.doctor_name}
              </h3>
              <p className="mt-1 text-sm font-medium text-brand-600">
                {appointment.doctor_specialty}
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

          <div className="mt-5 space-y-5">
            <div>
              <SectionTitle>Appointment Information</SectionTitle>
              <InfoList>
                <InfoItem label="Appointment ID" value={`#${appointment.appointment_id}`} />
                <InfoItem
                  label="Appointment Date"
                  value={formatAppointmentDate(appointment.appointment_date)}
                />
                <InfoItem
                  label="Appointment Time"
                  value={formatAppointmentTime(appointment.appointment_time)}
                />
                <InfoItem
                  label="Appointment Type"
                  value={appointmentTypeLabel(appointment.appointment_type)}
                />
              </InfoList>
            </div>

            <div>
              <SectionTitle>Patient Information</SectionTitle>
              <InfoList>
                <InfoItem label="Patient Name" value={appointment.patient_name} />
                <InfoItem
                  label="Patient Email"
                  value={appointment.patient_email}
                  truncate
                />
                <InfoItem
                  label="Patient Phone"
                  value={appointment.patient_phone ?? "Not provided"}
                />
              </InfoList>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200 px-5 py-4 sm:px-6">
        <div className="flex justify-end">
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
      </div>
    </article>
  );
}
