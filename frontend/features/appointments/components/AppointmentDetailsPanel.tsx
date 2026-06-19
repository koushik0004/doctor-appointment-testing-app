"use client";

import { format, parse, parseISO } from "date-fns";

import { useAppointmentDetails } from "@/features/appointments/hooks/use-appointment-details";
import type {
  AppointmentDetailsResponse,
  AppointmentStatus,
} from "@/features/appointments/types";
import { cn } from "@/lib/utils";

function appointmentTypeLabel(appointmentType: AppointmentDetailsResponse["appointment_type"]) {
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
      return "bg-amber-50 text-amber-700 ring-1 ring-amber-100";
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

function formatBookingDate(value: string) {
  try {
    return format(parseISO(value), "MMM d, yyyy 'at' h:mm a");
  } catch {
    return value;
  }
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[16px] bg-slate-50 px-4 py-3 ring-1 ring-slate-100">
      <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
        {label}
      </dt>
      <dd className="mt-1 text-sm font-medium leading-6 text-slate-900">{value}</dd>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-[420px] flex-col items-center justify-center rounded-[28px] border border-slate-100 bg-white p-6 text-center shadow-soft">
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
      <h3 className="mt-5 text-xl font-semibold tracking-[-0.04em] text-slate-950">
        No appointment selected
      </h3>
      <p className="mt-2 max-w-xs text-sm leading-6 text-slate-500">
        Select an appointment to inspect the patient, doctor, and booking
        details here.
      </p>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="rounded-[28px] border border-brand-100 bg-white p-6 shadow-soft">
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
      <p className="text-sm font-semibold uppercase tracking-[0.18em]">Could not load</p>
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
      className="rounded-[28px] border border-slate-100 bg-white shadow-soft"
      aria-live="polite"
    >
      <div className="border-b border-slate-100 px-6 py-5">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 text-brand-500 ring-1 ring-brand-100">
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

      <div className="space-y-6 px-6 py-6">
        <div className="rounded-[24px] bg-brand-50/60 px-4 py-3 ring-1 ring-brand-100">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-700/80">
                Current Status
              </p>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {data.patient.full_name} with {data.doctor.name}
              </p>
            </div>
            <span
              className={cn(
                "inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em]",
                statusStyles(data.status),
              )}
            >
              {statusLabel(data.status)}
            </span>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
            Patient Information
          </h4>
          <dl className="mt-3 grid gap-3">
            <DetailRow label="Name" value={data.patient.full_name} />
            <DetailRow label="Email" value={data.patient.email} />
            <DetailRow label="Phone" value={data.patient.phone ?? "Not provided"} />
          </dl>
        </div>

        <div>
          <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
            Doctor Information
          </h4>
          <dl className="mt-3 grid gap-3">
            <DetailRow label="Name" value={data.doctor.name} />
            <DetailRow label="Specialty" value={data.doctor.specialty} />
            <DetailRow label="Clinic" value={data.doctor.clinic_name} />
          </dl>
        </div>

        <div>
          <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
            Appointment Information
          </h4>
          <dl className="mt-3 grid gap-3">
            <DetailRow label="Date" value={formatAppointmentDate(data.appointment_date)} />
            <DetailRow label="Time" value={formatAppointmentTime(data.appointment_time)} />
            <DetailRow
              label="Appointment Type"
              value={appointmentTypeLabel(data.appointment_type)}
            />
            <DetailRow label="Status" value={statusLabel(data.status)} />
            <DetailRow label="Booking Date" value={formatBookingDate(data.created_at)} />
          </dl>
        </div>
      </div>
    </section>
  );
}
