"use client";

import Image from "next/image";

import { format, parse, parseISO } from "date-fns";

import { DoctorSummaryCard } from "@/features/appointments/components/DoctorSummaryCard";
import { useAppointmentDetails } from "@/features/appointments/hooks/use-appointment-details";
import type {
  AppointmentDetailsResponse,
  AppointmentStatus,
} from "@/features/appointments/types";
import { doctors } from "@/features/doctors/mock-doctors";
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

function resolveDoctorAvatar(name: string) {
  return doctors.find((doctor) => doctor.name === name)?.avatar ?? null;
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

function StethoscopeIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4 text-slate-400"
    >
      <path d="M6 3v5a3 3 0 0 0 6 0V3" />
      <path d="M12 8v4a5 5 0 0 0 10 0v-1" />
      <path d="M18 15v2a4 4 0 0 1-8 0v-1" />
      <circle cx="6" cy="20" r="1.5" />
      <circle cx="18" cy="15" r="1.5" />
    </svg>
  );
}

function ClinicIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4 text-slate-400"
    >
      <path d="M4 21V7a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v14" />
      <path d="M16 11h2a2 2 0 0 1 2 2v8" />
      <path d="M8 9h4" />
      <path d="M10 7v4" />
    </svg>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <p className="text-sm font-semibold uppercase tracking-[0.16em] text-brand-600">
      {children}
    </p>
  );
}

function InfoTile({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[16px] border border-brand-100 bg-white px-4 py-4 shadow-[0_8px_24px_rgba(15,23,42,0.04)]">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold leading-6 text-slate-950">
        {value}
      </p>
    </div>
  );
}

function PatientRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-[16px] border border-slate-100 bg-white px-4 py-4">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="max-w-[62%] text-right text-sm font-semibold leading-6 text-slate-950">
        {value}
      </dd>
    </div>
  );
}

function buildAvailableDoctors(currentDoctorName: string) {
  const matchedDoctors = doctors.filter((doctor) => doctor.name !== currentDoctorName);

  return matchedDoctors.slice(0, 3);
}

function DoctorAvatar({ doctorName }: { doctorName: string }) {
  const avatar = resolveDoctorAvatar(doctorName);

  if (avatar) {
    return (
      <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-full bg-white ring-1 ring-brand-100">
        <Image
          src={avatar.imageSrc}
          alt={avatar.imageAlt}
          fill
          sizes="64px"
          className="object-cover"
        />
      </div>
    );
  }

  return (
    <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-white text-base font-semibold text-brand-700 ring-1 ring-brand-100">
      {getInitials(doctorName)}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft">
      <div className="flex items-center gap-3 border-b border-slate-100 pb-5">
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

      <div className="mt-6 rounded-[22px] border border-brand-100 bg-brand-50/60 px-5 py-8 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white text-brand-500 ring-1 ring-brand-100">
          <CalendarIcon />
        </div>
        <p className="mt-5 text-lg font-semibold tracking-[-0.03em] text-slate-950">
          Choose a result to preview the booking
        </p>
        <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-slate-600">
          Select an appointment card to review the doctor summary, appointment
          information, and patient details in this panel.
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
      <div className="mt-6 h-28 animate-pulse rounded-[22px] bg-brand-50/60" />
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="h-24 animate-pulse rounded-[16px] bg-slate-50" />
        <div className="h-24 animate-pulse rounded-[16px] bg-slate-50" />
        <div className="h-24 animate-pulse rounded-[16px] bg-slate-50" />
        <div className="h-24 animate-pulse rounded-[16px] bg-slate-50" />
      </div>
      <div className="mt-5 h-44 animate-pulse rounded-[22px] bg-slate-50" />
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

  const availableDoctors = buildAvailableDoctors(data.doctor.name);

  return (
    <section
      className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft"
      aria-live="polite"
    >
      <div className="flex items-center gap-3 border-b border-slate-100 pb-5">
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

      <div className="mt-6 space-y-5">
        <section className="rounded-[22px] border border-brand-100 bg-brand-50/60 p-5">
          <SectionLabel>Doctor Summary</SectionLabel>
          <div className="mt-4 flex items-start gap-4">
            <DoctorAvatar doctorName={data.doctor.name} />

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-3">
                <h4 className="text-[1.75rem] font-semibold tracking-[-0.04em] text-slate-950">
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

              <div className="mt-2 flex items-center gap-2 text-sm text-slate-600">
                <StethoscopeIcon />
                <span>{data.doctor.specialty}</span>
              </div>
              <div className="mt-2 flex items-center gap-2 text-sm text-slate-600">
                <ClinicIcon />
                <span>{data.doctor.clinic_name}</span>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-[22px] border border-brand-100 bg-brand-50/40 p-5">
          <SectionLabel>Appointment Information</SectionLabel>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <InfoTile
              label="Date"
              value={formatAppointmentDate(data.appointment_date)}
            />
            <InfoTile
              label="Time"
              value={formatAppointmentTime(data.appointment_time)}
            />
            <InfoTile
              label="Type"
              value={appointmentTypeLabel(data.appointment_type)}
            />
            <InfoTile label="Status" value={statusLabel(data.status)} />
          </div>
        </section>

        <section className="rounded-[22px] border border-slate-100 bg-slate-50/80 p-5">
          <SectionLabel>Patient Information</SectionLabel>
          <dl className="mt-4 space-y-3">
            <PatientRow label="Name" value={data.patient.full_name} />
            <PatientRow label="Email" value={data.patient.email} />
            <PatientRow
              label="Phone"
              value={data.patient.phone ?? "Not provided"}
            />
          </dl>
        </section>

        <section className="rounded-[22px] border border-slate-100 bg-slate-50/80 p-5">
          <SectionLabel>Available Doctors</SectionLabel>
          <div className="mt-4 grid gap-4">
            {availableDoctors.map((doctor) => (
              <DoctorSummaryCard
                key={doctor.id}
                doctor={doctor}
                ratingLabel="Available"
                waitTimeLabel={doctor.nextAvailable}
              />
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
