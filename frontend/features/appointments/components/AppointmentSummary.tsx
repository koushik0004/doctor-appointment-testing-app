"use client";

import Image from "next/image";

import { format } from "date-fns";

import type { Doctor } from "@/features/doctors/types";
import { cn } from "@/lib/utils";
import { formatCurrencyInr } from "@/lib/formatters";

import type {
  AppointmentType,
  BookingPatientDetails,
} from "@/features/appointments/types";
import { appointmentTypeLabels } from "@/features/appointments/schema";
import { formatAppointmentTime } from "@/features/appointments/utils";

type AppointmentSummaryProps = {
  doctor: Doctor;
  appointmentDate: Date;
  appointmentTime: string;
  appointmentType: AppointmentType;
  patient: BookingPatientDetails;
  visitReason?: string;
  className?: string;
};

function SectionHeading({ children }: { children: string }) {
  return (
    <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
      {children}
    </h3>
  );
}

function InfoRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-3 last:border-b-0 last:pb-0">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="max-w-[65%] text-sm font-medium text-slate-900 text-right">
        {value}
      </dd>
    </div>
  );
}

export function AppointmentSummary({
  doctor,
  appointmentDate,
  appointmentTime,
  appointmentType,
  patient,
  visitReason,
  className,
}: AppointmentSummaryProps) {
  return (
    <article
      className={cn(
        "rounded-[24px] border border-slate-100 bg-white p-6 shadow-soft sm:p-8",
        className,
      )}
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex items-center gap-4">
          <div className="relative h-16 w-16 overflow-hidden rounded-full bg-slate-200 ring-1 ring-slate-200">
            <Image
              src={doctor.avatar.imageSrc}
              alt={doctor.avatar.imageAlt}
              fill
              sizes="64px"
              className="object-cover"
            />
          </div>

          <div>
            <SectionHeading>Doctor Information</SectionHeading>
            <p className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              {doctor.name}
            </p>
            <p className="mt-1 text-sm text-slate-600">
              {doctor.specialty} specialist at {doctor.clinic}
            </p>
          </div>
        </div>

        <div className="rounded-[16px] bg-brand-50/70 px-4 py-3 text-sm text-brand-900">
          <p className="font-semibold">Appointment Type</p>
          <p className="mt-1">{appointmentTypeLabels[appointmentType]}</p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section className="rounded-[18px] border border-slate-100 bg-slate-50/60 p-5">
          <SectionHeading>Appointment Date &amp; Time</SectionHeading>
          <dl className="mt-4 space-y-3">
            <InfoRow
              label="Date"
              value={format(appointmentDate, "EEEE, MMMM d, yyyy")}
            />
            <InfoRow label="Time" value={formatAppointmentTime(appointmentTime)} />
            <InfoRow label="Duration" value={`${doctor.durationMinutes} minutes`} />
          </dl>
        </section>

        <section className="rounded-[18px] border border-slate-100 bg-slate-50/60 p-5">
          <SectionHeading>Location Information</SectionHeading>
          <dl className="mt-4 space-y-3">
            <InfoRow label="Clinic" value={doctor.clinic} />
            <InfoRow label="Location" value={doctor.location} />
            <InfoRow
              label="Consultation Fee"
              value={formatCurrencyInr(doctor.consultationFee)}
            />
          </dl>
        </section>

        <section className="rounded-[18px] border border-slate-100 bg-slate-50/60 p-5">
          <SectionHeading>Patient Information</SectionHeading>
          <dl className="mt-4 space-y-3">
            <InfoRow label="Full Name" value={patient.full_name} />
            <InfoRow label="Email" value={patient.email} />
            <InfoRow label="Phone" value={patient.phone || "Not provided"} />
          </dl>
        </section>

        <section className="rounded-[18px] border border-slate-100 bg-slate-50/60 p-5">
          <SectionHeading>Visit Reason</SectionHeading>
          <p className="mt-4 text-sm leading-7 text-slate-700">
            {visitReason || "No additional details were provided."}
          </p>
        </section>
      </div>
    </article>
  );
}
