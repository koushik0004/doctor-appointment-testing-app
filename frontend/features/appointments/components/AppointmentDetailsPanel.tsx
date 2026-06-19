"use client";

import { format, parse, parseISO } from "date-fns";

import { useAppointmentDetails } from "@/features/appointments/hooks/use-appointment-details";
import type {
  AppointmentDetailsResponse,
  AppointmentStatus,
} from "@/features/appointments/types";
import { cn } from "@/lib/utils";

function appointmentTypeLabel(
  appointmentType: AppointmentDetailsResponse["appointment_type"],
) {
  return appointmentType === "IN_PERSON" ? "In Person" : "Telemedicine";
}

function statusLabel(status: AppointmentStatus) {
  switch (status) {
    case "PENDING":
      return "Pending";
    case "CONFIRMED":
      return "Confirmed";
    case "CANCELLED":
      return "Cancelled";
  }
}

function statusStyles(status: AppointmentStatus) {
  switch (status) {
    case "PENDING":
      return "bg-slate-100 text-slate-700 ring-1 ring-slate-200";
    case "CONFIRMED":
      return "bg-brand-50 text-brand-700 ring-1 ring-brand-100";
    case "CANCELLED":
      return "bg-rose-50 text-rose-700 ring-1 ring-rose-100";
  }
}

function formatAppointmentDate(value: string) {
  try {
    return format(parseISO(value), "EEEE, MMM d, yyyy");
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

function CalendarIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      className="h-5 w-5"
    >
      <path d="M8 3v4M16 3v4M4 8h16" />
      <rect x="4" y="5" width="16" height="16" rx="3" />
    </svg>
  );
}

function DetailBlock({
  title,
  rows,
}: {
  title: string;
  rows: Array<{ label: string; value: string }>;
}) {
  return (
    <section className="rounded-[18px] border border-slate-100 bg-slate-50/70 p-5">
      <h4 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
        {title}
      </h4>
      <dl className="mt-4 space-y-3">
        {rows.map((row) => (
          <div
            key={row.label}
            className="flex items-start justify-between gap-4 border-b border-slate-100 pb-3 last:border-b-0 last:pb-0"
          >
            <dt className="text-sm text-slate-500">{row.label}</dt>
            <dd className="max-w-[60%] text-right text-sm font-medium text-slate-900">
              {row.value}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function EmptyState() {
  return (
    <div className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft">
      <div className="border-b border-slate-100 pb-5">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 text-brand-500 ring-1 ring-brand-100">
            <CalendarIcon />
          </span>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
              Your Booking
            </p>
            <h3 className="mt-1 text-2xl font-semibold tracking-[-0.05em] text-slate-950">
              No appointment selected
            </h3>
          </div>
        </div>
      </div>

      <div className="flex flex-col items-center justify-center px-4 py-10 text-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-slate-50 ring-1 ring-slate-100">
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            className="h-9 w-9 text-slate-300"
          >
            <path d="M12 8v5l3 2" />
            <circle cx="12" cy="12" r="9" />
          </svg>
        </div>
        <p className="mt-5 max-w-xs text-sm leading-6 text-slate-500">
          Select an appointment to review the doctor, patient, and schedule
          details here.
        </p>
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft">
      <div className="h-4 w-36 animate-pulse rounded-full bg-slate-100" />
      <div className="mt-5 h-8 w-56 animate-pulse rounded-full bg-slate-100" />
      <div className="mt-8 space-y-3">
        <div className="h-20 animate-pulse rounded-[18px] bg-slate-50" />
        <div className="h-20 animate-pulse rounded-[18px] bg-slate-50" />
        <div className="h-20 animate-pulse rounded-[18px] bg-slate-50" />
      </div>
    </div>
  );
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="rounded-[28px] border border-rose-200 bg-rose-50 p-6 text-rose-800 shadow-soft">
      <p className="text-sm font-semibold uppercase tracking-[0.18em]">
        Could not load
      </p>
      <h3 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-rose-950">
        Appointment details unavailable
      </h3>
      <p className="mt-3 text-sm leading-6">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-6 inline-flex h-11 items-center justify-center rounded-[14px] bg-rose-600 px-5 text-sm font-semibold text-white transition hover:bg-rose-700"
      >
        Try again
      </button>
    </div>
  );
}

export function AppointmentDetailsPanel({
  appointmentId,
}: {
  appointmentId: number | null;
}) {
  const { data, error, isLoading, refetch } = useAppointmentDetails(appointmentId);

  if (appointmentId === null) {
    return <EmptyState />;
  }

  if (isLoading && !data) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={refetch} />;
  }

  if (!data) {
    return <EmptyState />;
  }

  return (
    <section
      className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft"
      aria-live="polite"
    >
      <div className="border-b border-slate-100 pb-5">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 text-brand-500 ring-1 ring-brand-100">
            <CalendarIcon />
          </span>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
              Your Booking
            </p>
            <h3 className="mt-1 text-2xl font-semibold tracking-[-0.05em] text-slate-950">
              Appointment #{data.appointment_id}
            </h3>
          </div>
        </div>
      </div>

      <div className="mt-6 space-y-5">
        <section className="rounded-[20px] border border-brand-100 bg-brand-50/60 p-5">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-white text-base font-semibold text-brand-700 ring-1 ring-brand-100">
              {getInitials(data.doctor.name)}
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-3">
                <h4 className="text-2xl font-semibold tracking-[-0.04em] text-slate-950">
                  {data.doctor.name}
                </h4>
                <span
                  className={cn(
                    "rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em]",
                    statusStyles(data.status),
                  )}
                >
                  {statusLabel(data.status)}
                </span>
              </div>
              <p className="mt-1 text-base text-brand-600">
                {data.doctor.specialty}
              </p>
              <p className="mt-2 text-sm text-slate-600">
                {data.doctor.clinic_name}
              </p>
            </div>
          </div>
        </section>

        <DetailBlock
          title="Appointment Information"
          rows={[
            {
              label: "Date",
              value: formatAppointmentDate(data.appointment_date),
            },
            {
              label: "Time",
              value: formatAppointmentTime(data.appointment_time),
            },
            {
              label: "Type",
              value: appointmentTypeLabel(data.appointment_type),
            },
            {
              label: "Status",
              value: statusLabel(data.status),
            },
          ]}
        />

        <DetailBlock
          title="Patient Information"
          rows={[
            { label: "Name", value: data.patient.full_name },
            { label: "Email", value: data.patient.email },
            {
              label: "Phone",
              value: data.patient.phone ?? "Not provided",
            },
          ]}
        />
      </div>
    </section>
  );
}
