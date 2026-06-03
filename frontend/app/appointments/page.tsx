"use client";

import { addMonths, format, startOfMonth } from "date-fns";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AppointmentAvailability } from "@/features/appointments/components/AppointmentAvailability";
import { AppointmentCalendar } from "@/features/appointments/components/AppointmentCalendar";
import { DoctorSummaryCard } from "@/features/appointments/components/DoctorSummaryCard";
import { PatientDetailsForm } from "@/features/appointments/components/PatientDetailsForm";
import {
  appointmentAvailableDates,
  appointmentAvailableSlots,
  appointmentBookingDoctor,
} from "@/features/appointments/mock-data";
import type { AppointmentFormValues } from "@/features/appointments/schema";
import { useBookingStore } from "@/stores/booking-store";

export default function AppointmentsPage() {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(
    appointmentAvailableDates[4],
  );
  const [selectedSlot, setSelectedSlot] = useState<string | null>("10:30 AM");
  const [visibleMonth, setVisibleMonth] = useState<Date>(
    startOfMonth(appointmentAvailableDates[0]),
  );
  const [bookingError, setBookingError] = useState<string | null>(null);

  const setSelectedDoctorId = useBookingStore(
    (state) => state.setSelectedDoctorId,
  );
  const setSelectedAvailabilityId = useBookingStore(
    (state) => state.setSelectedAvailabilityId,
  );
  const setSelectedDateStore = useBookingStore((state) => state.setSelectedDate);
  const setSelectedTime = useBookingStore((state) => state.setSelectedTime);
  const setAppointmentType = useBookingStore(
    (state) => state.setAppointmentType,
  );
  const setPatientDetails = useBookingStore(
    (state) => state.setPatientDetails,
  );
  const setConfirmationId = useBookingStore(
    (state) => state.setConfirmationId,
  );

  const handleSubmit = (values: AppointmentFormValues) => {
    if (!selectedDate || !selectedSlot) {
      setBookingError("Select a date and time before confirming the booking.");
      return;
    }

    const selectedDateKey = format(selectedDate, "yyyy-MM-dd");
    const confirmationId = `CA-${format(selectedDate, "yyyyMMdd")}-${selectedSlot
      .replace(/[^0-9]/g, "")
      .slice(0, 4)}`;

    setBookingError(null);
    setSelectedDoctorId(appointmentBookingDoctor.id);
    setSelectedAvailabilityId(`${selectedDateKey}-${selectedSlot}`);
    setSelectedDateStore(selectedDateKey);
    setSelectedTime(selectedSlot);
    setAppointmentType(values.appointment_type);
    setPatientDetails({
      full_name: values.full_name,
      email: values.email,
      phone: values.phone,
      health_description: values.health_description,
    });
    setConfirmationId(confirmationId);

    router.push("/appointments/confirmation");
  };

  return (
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 max-w-3xl">
          <h1 className="text-4xl font-semibold tracking-[-0.05em] text-slate-950 sm:text-5xl">
            Book Your Appointment
          </h1>
          <p className="mt-4 text-lg leading-8 text-slate-600">
            Select a convenient time and provide a few details to confirm your
            visit.
          </p>
        </div>

        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.45fr)_minmax(380px,0.95fr)]">
          <div className="space-y-8">
            <section>
              <div className="mb-4 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="inline-flex h-6 w-6 items-center justify-center text-brand-500">
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 24 24"
                      className="h-6 w-6"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <rect x="3" y="4" width="18" height="18" rx="3" />
                      <path d="M8 2v4M16 2v4M3 10h18" />
                    </svg>
                  </span>
                  <h2 className="text-xl font-semibold tracking-[-0.03em] text-slate-950">
                    Select Date
                  </h2>
                </div>

                <div className="flex items-center gap-4 text-slate-700">
                  <button
                    type="button"
                    onClick={() =>
                      setVisibleMonth((current) => addMonths(current, -1))
                    }
                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 transition hover:border-brand-200 hover:text-brand-500"
                    aria-label="Previous month"
                  >
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 24 24"
                      className="h-4 w-4"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M15 18 9 12l6-6" />
                    </svg>
                  </button>
                  <span className="min-w-[160px] text-center text-base font-semibold tracking-[0.14em] text-slate-700">
                    {format(visibleMonth, "MMMM yyyy").toUpperCase()}
                  </span>
                  <button
                    type="button"
                    onClick={() =>
                      setVisibleMonth((current) => addMonths(current, 1))
                    }
                    className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 transition hover:border-brand-200 hover:text-brand-500"
                    aria-label="Next month"
                  >
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 24 24"
                      className="h-4 w-4"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="m9 18 6-6-6-6" />
                    </svg>
                  </button>
                </div>
              </div>

              <AppointmentCalendar
                selectedDate={selectedDate}
                availableDates={appointmentAvailableDates}
                onDateSelect={(date) => {
                  setSelectedDate(date);
                  setBookingError(null);
                }}
                month={visibleMonth}
                onMonthChange={setVisibleMonth}
              />
            </section>

            <AppointmentAvailability
              selectedDate={selectedDate}
              selectedSlot={selectedSlot}
              availableSlots={appointmentAvailableSlots}
              onSlotSelect={(slot) => {
                setSelectedSlot(slot);
                setBookingError(null);
              }}
            />
          </div>

          <div className="space-y-6">
            <DoctorSummaryCard doctor={appointmentBookingDoctor} />

            <aside className="rounded-[20px] border border-slate-100 bg-white p-6 shadow-soft">
              <div className="flex items-start gap-3">
                <span className="mt-1 text-brand-500">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    className="h-6 w-6"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </span>
                <div>
                  <h2 className="text-2xl font-semibold tracking-[-0.04em] text-slate-950">
                    Patient Details
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    Please enter your contact information for appointment
                    updates.
                  </p>
                </div>
              </div>

              {bookingError ? (
                <p className="mt-6 rounded-[12px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                  {bookingError}
                </p>
              ) : null}

              <div className="mt-6">
                <PatientDetailsForm
                  isBookingReady={Boolean(selectedDate && selectedSlot)}
                  onSubmit={handleSubmit}
                />
              </div>
            </aside>

            <p className="text-center text-sm leading-6 text-slate-600">
              By confirming, you agree to CareNow&apos;s{" "}
              <span className="font-medium underline decoration-slate-300 underline-offset-2">
                Terms of Service
              </span>{" "}
              and{" "}
              <span className="font-medium underline decoration-slate-300 underline-offset-2">
                Privacy Policy
              </span>
              . Cancellation is free up to 24 hours before the appointment.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
