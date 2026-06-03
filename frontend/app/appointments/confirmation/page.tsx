"use client";

import Link from "next/link";

import { parse } from "date-fns";

import { AppointmentSummary } from "@/features/appointments/components/AppointmentSummary";
import {
  appointmentAvailableDates,
  appointmentFormMockValues,
  appointmentBookingDoctor,
} from "@/features/appointments/mock-data";
import type { AppointmentType, BookingPatientDetails } from "@/features/appointments/types";
import { appointmentTypeLabels } from "@/features/appointments/schema";
import { doctors } from "@/features/doctors/mock-doctors";
import { useBookingStore } from "@/stores/booking-store";

function CheckIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-8 w-8 text-brand-500"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.25"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="m8.5 12 2.5 2.5L15.5 9.5" />
    </svg>
  );
}

export default function AppointmentConfirmationPage() {
  const selectedDoctorId = useBookingStore((state) => state.selectedDoctorId);
  const selectedDate = useBookingStore((state) => state.selectedDate);
  const selectedTime = useBookingStore((state) => state.selectedTime);
  const appointmentType = useBookingStore((state) => state.appointmentType);
  const patientDetails = useBookingStore((state) => state.patientDetails);
  const confirmationId = useBookingStore((state) => state.confirmationId);

  const doctor =
    doctors.find((entry) => entry.id === selectedDoctorId) ??
    appointmentBookingDoctor;
  const parsedDate = selectedDate
    ? parse(selectedDate, "yyyy-MM-dd", new Date())
    : appointmentAvailableDates[4];
  const resolvedTime = selectedTime ?? "10:30 AM";
  const resolvedAppointmentType: AppointmentType =
    appointmentType ?? appointmentFormMockValues.appointment_type;
  const resolvedPatient: BookingPatientDetails =
    patientDetails ?? {
      full_name: appointmentFormMockValues.full_name,
      email: appointmentFormMockValues.email,
      phone: appointmentFormMockValues.phone,
      health_description: appointmentFormMockValues.health_description,
    };
  const resolvedConfirmationId =
    confirmationId ??
    `CA-${selectedDate ? selectedDate.replaceAll("-", "") : "20241024"}-${resolvedTime
      .replace(/[^0-9]/g, "")
      .slice(0, 4)}`;

  return (
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-5xl">
        <div className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft sm:p-8">
          <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-50">
                <CheckIcon />
              </div>
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
                  Appointment Confirmed
                </p>
                <h1 className="mt-2 text-4xl font-semibold tracking-[-0.05em] text-slate-950 sm:text-5xl">
                  Your visit is booked
                </h1>
              </div>
            </div>

            <div className="rounded-[16px] border border-brand-100 bg-brand-50/70 px-4 py-3 text-left">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">
                Confirmation ID
              </p>
              <p className="mt-1 text-lg font-semibold tracking-[0.08em] text-slate-950">
                {resolvedConfirmationId}
              </p>
            </div>
          </div>

          <div className="mt-8">
            <AppointmentSummary
              doctor={doctor}
              appointmentDate={parsedDate}
              appointmentTime={resolvedTime}
              appointmentType={resolvedAppointmentType}
              patient={resolvedPatient}
              visitReason={resolvedPatient.health_description}
            />
          </div>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/appointments"
              className="inline-flex h-12 items-center justify-center rounded-[12px] bg-brand-500 px-5 text-sm font-semibold text-white transition hover:bg-brand-600"
            >
              Modify Appointment
            </Link>
            <Link
              href="/doctors"
              className="inline-flex h-12 items-center justify-center rounded-[12px] border border-slate-200 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-950"
            >
              Cancel Appointment
            </Link>
          </div>

          <p className="mt-6 text-sm leading-6 text-slate-600">
            {appointmentTypeLabels[resolvedAppointmentType]} consultations are
            typically ready a few minutes before your scheduled time.
          </p>
        </div>
      </div>
    </section>
  );
}
