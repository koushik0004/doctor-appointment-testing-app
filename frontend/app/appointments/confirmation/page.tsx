"use client";

export const dynamic = "force-dynamic";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { parseISO } from "date-fns";
import { Suspense, useEffect, useMemo, useState } from "react";

import { AppointmentSummary } from "@/features/appointments/components/AppointmentSummary";
import { getAppointmentConfirmation } from "@/features/appointments/api";
import type {
  AppointmentConfirmationResponse,
  BookingPatientDetails,
} from "@/features/appointments/types";
import { appointmentTypeLabels } from "@/features/appointments/schema";
import { getDoctor } from "@/features/doctors/api";
import type { Doctor } from "@/features/doctors/types";
import { ApiError } from "@/lib/api-client";
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

function LoadingState() {
  return (
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-5xl rounded-[28px] border border-slate-100 bg-white p-8 shadow-soft">
        <div className="h-14 w-56 animate-pulse rounded-full bg-slate-100" />
        <div className="mt-8 h-[420px] animate-pulse rounded-[24px] bg-slate-50" />
      </div>
    </section>
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
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-3xl rounded-[24px] border border-rose-200 bg-rose-50 px-6 py-10 text-center">
        <h1 className="text-3xl font-semibold tracking-[-0.05em] text-rose-950">
          We could not load the confirmation
        </h1>
        <p className="mt-3 text-sm leading-6 text-rose-700">{message}</p>
        <button
          type="button"
          onClick={onRetry}
          className="mt-6 rounded-[12px] bg-rose-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-rose-700"
        >
          Try Again
        </button>
      </div>
    </section>
  );
}

function MissingBookingState() {
  return (
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-3xl rounded-[24px] border border-slate-100 bg-white p-8 shadow-soft">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
          Confirmation
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] text-slate-950">
          No booking was found
        </h1>
        <p className="mt-4 text-base leading-7 text-slate-600">
          Open this page from the booking flow so we can load the live
          confirmation details.
        </p>
        <Link
          href="/doctors"
          className="mt-6 inline-flex h-12 items-center justify-center rounded-[12px] bg-brand-500 px-5 text-sm font-semibold text-white transition hover:bg-brand-600"
        >
          Browse Doctors
        </Link>
      </div>
    </section>
  );
}

function AppointmentConfirmationContent() {
  const searchParams = useSearchParams();
  const queryAppointmentId = searchParams.get("appointmentId");
  const queryDoctorId = searchParams.get("doctorId");

  const storedAppointmentId = useBookingStore((state) => state.appointmentId);
  const storedDoctorId = useBookingStore((state) => state.selectedDoctorId);
  const storedConfirmationCode = useBookingStore(
    (state) => state.confirmationCode,
  );
  const storedSelectedDate = useBookingStore((state) => state.selectedDate);
  const storedSelectedTime = useBookingStore((state) => state.selectedTime);
  const storedAppointmentType = useBookingStore(
    (state) => state.appointmentType,
  );
  const storedPatientDetails = useBookingStore((state) => state.patientDetails);
  const resetBooking = useBookingStore((state) => state.resetBooking);

  const effectiveAppointmentId =
    queryAppointmentId ?? storedAppointmentId?.toString() ?? null;
  const effectiveDoctorId =
    queryDoctorId ??
    (storedDoctorId && /^\d+$/.test(storedDoctorId) ? storedDoctorId : null);

  const [confirmation, setConfirmation] =
    useState<AppointmentConfirmationResponse | null>(null);
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let isActive = true;
    const controller = new AbortController();

    async function loadConfirmation() {
      if (!effectiveAppointmentId || !effectiveDoctorId) {
        setConfirmation(null);
        setDoctor(null);
        setLoadError(null);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setLoadError(null);

      try {
        const [confirmationResponse, doctorResponse] = await Promise.all([
          getAppointmentConfirmation(effectiveAppointmentId, {
            signal: controller.signal,
          }),
          getDoctor(effectiveDoctorId, { signal: controller.signal }),
        ]);

        if (!isActive) {
          return;
        }

        setConfirmation(confirmationResponse);
        setDoctor(doctorResponse);
      } catch (error) {
        if (!isActive) {
          return;
        }

        setConfirmation(null);
        setDoctor(null);
        setLoadError(
          error instanceof ApiError
            ? error.message
            : "Unable to load the confirmation details right now.",
        );
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadConfirmation();

    return () => {
      isActive = false;
      controller.abort();
    };
  }, [effectiveAppointmentId, effectiveDoctorId, reloadKey]);

  const parsedAppointmentDate = useMemo(() => {
    if (!confirmation) {
      return storedSelectedDate ? parseISO(storedSelectedDate) : null;
    }

    return parseISO(confirmation.appointment_date);
  }, [confirmation, storedSelectedDate]);

  const resolvedPatient: BookingPatientDetails = useMemo(() => {
    if (confirmation) {
      return {
        full_name: confirmation.patient.full_name,
        email: confirmation.patient.email,
        phone: confirmation.patient.phone ?? "",
        health_description: confirmation.health_description ?? "",
      };
    }

    return (
      storedPatientDetails ?? {
        full_name: "",
        email: "",
        phone: "",
        health_description: "",
      }
    );
  }, [confirmation, storedPatientDetails]);

  if (!effectiveAppointmentId || !effectiveDoctorId) {
    return <MissingBookingState />;
  }

  if (isLoading && !confirmation) {
    return <LoadingState />;
  }

  if (loadError) {
    return (
      <ErrorState
        message={loadError}
        onRetry={() => setReloadKey((value) => value + 1)}
      />
    );
  }

  if (!confirmation || !doctor || !parsedAppointmentDate) {
    return <MissingBookingState />;
  }

  const resolvedConfirmationCode =
    confirmation.confirmation_code ?? storedConfirmationCode ?? "Pending";
  const resolvedAppointmentType =
    confirmation.appointment_type ?? storedAppointmentType ?? "IN_PERSON";
  const resolvedAppointmentTime = confirmation.start_time ?? storedSelectedTime ?? "";

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
                {resolvedConfirmationCode}
              </p>
            </div>
          </div>

          <div className="mt-8">
            <AppointmentSummary
              doctor={doctor}
              appointmentDate={parsedAppointmentDate}
              appointmentTime={resolvedAppointmentTime}
              appointmentType={resolvedAppointmentType}
              patient={resolvedPatient}
              visitReason={confirmation.health_description ?? undefined}
            />
          </div>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link
              href={`/appointments?doctorId=${doctor.backendId}`}
              className="inline-flex h-12 items-center justify-center rounded-[12px] bg-brand-500 px-5 text-sm font-semibold text-white transition hover:bg-brand-600"
            >
              Modify Appointment
            </Link>
            <button
              type="button"
              onClick={() => resetBooking()}
              className="inline-flex h-12 items-center justify-center rounded-[12px] border border-slate-200 bg-white px-5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-950"
            >
              Reset Booking
            </button>
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

export default function AppointmentConfirmationPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <AppointmentConfirmationContent />
    </Suspense>
  );
}
