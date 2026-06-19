"use client";

export const dynamic = "force-dynamic";

import { addMonths, format, parseISO, startOfMonth } from "date-fns";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";

import { AppointmentAvailability } from "@/features/appointments/components/AppointmentAvailability";
import { AppointmentCalendar } from "@/features/appointments/components/AppointmentCalendar";
import { DoctorSummaryCard } from "@/features/appointments/components/DoctorSummaryCard";
import { PatientDetailsForm } from "@/features/appointments/components/PatientDetailsForm";
import {
  createAppointment,
  getDoctorAvailability,
} from "@/features/appointments/api";
import type {
  AppointmentFormValues,
} from "@/features/appointments/schema";
import type {
  AppointmentType,
  AvailabilitySlot,
  DoctorAvailability,
} from "@/features/appointments/types";
import {
  createDateKey,
  filterBookableSlotsForDate,
  isElapsedAppointmentSlot,
} from "@/features/appointments/utils";
import type { Doctor } from "@/features/doctors/types";
import { ApiError } from "@/lib/api-client";
import { useBookingStore } from "@/stores/booking-store";

function LoadingState() {
  return (
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.45fr)_minmax(380px,0.95fr)]">
          <div className="space-y-8">
            <div className="h-12 w-80 animate-pulse rounded-full bg-slate-100" />
            <div className="space-y-4 rounded-[20px] border border-slate-100 bg-white p-6 shadow-soft">
              <div className="h-6 w-40 animate-pulse rounded-full bg-slate-100" />
              <div className="h-[420px] animate-pulse rounded-[20px] bg-slate-50" />
            </div>
            <div className="h-[360px] animate-pulse rounded-[20px] border border-slate-100 bg-white shadow-soft" />
          </div>
          <div className="space-y-6">
            <div className="h-[220px] animate-pulse rounded-[20px] border border-slate-100 bg-white shadow-soft" />
            <div className="h-[360px] animate-pulse rounded-[20px] border border-slate-100 bg-white shadow-soft" />
          </div>
        </div>
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
          We could not load the booking details
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

function NoDoctorState() {
  return (
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-3xl rounded-[24px] border border-slate-100 bg-white p-8 shadow-soft">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
          Booking flow
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] text-slate-950">
          Select a doctor first
        </h1>
        <p className="mt-4 text-base leading-7 text-slate-600">
          This page needs a selected doctor so it can load live availability and
          submit a valid booking request.
        </p>
        <a
          href="/doctors"
          className="mt-6 inline-flex h-12 items-center justify-center rounded-[12px] bg-brand-500 px-5 text-sm font-semibold text-white transition hover:bg-brand-600"
        >
          Browse Doctors
        </a>
      </div>
    </section>
  );
}

function AppointmentsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchDoctorId = searchParams.get("doctorId");

  const storedDoctorId = useBookingStore((state) => state.selectedDoctorId);
  const storedAppointmentType = useBookingStore((state) => state.appointmentType);
  const storedSelectedDate = useBookingStore((state) => state.selectedDate);
  const storedSelectedTime = useBookingStore((state) => state.selectedTime);
  const storedPatientDetails = useBookingStore((state) => state.patientDetails);

  const setSelectedDoctorId = useBookingStore(
    (state) => state.setSelectedDoctorId,
  );
  const setSelectedAvailabilityId = useBookingStore(
    (state) => state.setSelectedAvailabilityId,
  );
  const setSelectedDateStore = useBookingStore((state) => state.setSelectedDate);
  const setSelectedTimeStore = useBookingStore((state) => state.setSelectedTime);
  const setAppointmentTypeStore = useBookingStore(
    (state) => state.setAppointmentType,
  );
  const setPatientDetailsStore = useBookingStore(
    (state) => state.setPatientDetails,
  );
  const setAppointmentIdStore = useBookingStore((state) => state.setAppointmentId);
  const setConfirmationCodeStore = useBookingStore(
    (state) => state.setConfirmationCode,
  );

  const effectiveDoctorId =
    searchDoctorId ??
    (storedDoctorId && /^\d+$/.test(storedDoctorId) ? storedDoctorId : null);

  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [availability, setAvailability] = useState<DoctorAvailability | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null);
  const [selectedAppointmentType, setSelectedAppointmentType] =
    useState<AppointmentType>(storedAppointmentType ?? "IN_PERSON");
  const [visibleMonth, setVisibleMonth] = useState<Date>(new Date());
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [currentDateTime, setCurrentDateTime] = useState(() => new Date());

  useEffect(() => {
    if (searchDoctorId) {
      setSelectedDoctorId(searchDoctorId);
    }
  }, [searchDoctorId, setSelectedDoctorId]);

  useEffect(() => {
    if (storedAppointmentType) {
      setSelectedAppointmentType(storedAppointmentType);
    }
  }, [storedAppointmentType]);

  useEffect(() => {
    if (!storedSelectedDate) {
      return;
    }

    const restoredDate = parseISO(storedSelectedDate);
    if (!Number.isNaN(restoredDate.getTime())) {
      setSelectedDate(restoredDate);
    }
  }, [storedSelectedDate]);

  useEffect(() => {
    if (!availability) {
      return;
    }

    const allSlots = [...availability.morningSlots, ...availability.afternoonSlots];
    const filteredSlots = allSlots.filter(
      (slot) =>
        !slot.isBooked && slot.appointmentType === selectedAppointmentType,
    );
    const availableDates = availability.availableDates.filter((date) =>
      filteredSlots.some((slot) => slot.availableDate === createDateKey(date)),
    );

    if (availableDates.length === 0) {
      setSelectedDate(undefined);
      setSelectedSlotId(null);
      return;
    }

    const selectedDateKey = selectedDate ? createDateKey(selectedDate) : null;
    const hasSelectedDate =
      selectedDateKey !== null &&
      availableDates.some((date) => createDateKey(date) === selectedDateKey);

    if (!hasSelectedDate) {
      setSelectedDate((current) =>
        current && availableDates.some((date) => createDateKey(date) === createDateKey(current))
          ? current
          : availableDates[0],
      );
    }
  }, [availability, selectedAppointmentType, selectedDate]);

  useEffect(() => {
    if (!availability || !selectedDate) {
      setSelectedSlotId(null);
      return;
    }

    const availableSlots = filterBookableSlotsForDate(
      [...availability.morningSlots, ...availability.afternoonSlots].filter(
        (slot) => slot.appointmentType === selectedAppointmentType,
      ),
      selectedDate,
      currentDateTime,
    );

    if (availableSlots.length === 0) {
      setSelectedSlotId(null);
      return;
    }

    const storedMatch = availableSlots.find(
      (slot) => slot.startTime === storedSelectedTime,
    );
    const currentMatch = availableSlots.find((slot) => slot.id === selectedSlotId);
    const nextSlot = storedMatch ?? currentMatch ?? availableSlots[0];

    if (nextSlot.id !== selectedSlotId) {
      setSelectedSlotId(nextSlot.id);
    }
  }, [
    availability,
    currentDateTime,
    selectedAppointmentType,
    selectedDate,
    selectedSlotId,
    storedSelectedTime,
  ]);

  useEffect(() => {
    if (selectedDate) {
      setVisibleMonth(startOfMonth(selectedDate));
    }
  }, [selectedDate]);

  useEffect(() => {
    const updateClock = () => setCurrentDateTime(new Date());

    updateClock();
    const timer = window.setInterval(updateClock, 60_000);

    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    let isActive = true;
    const controller = new AbortController();

    async function loadBookingData() {
      if (!effectiveDoctorId) {
        setDoctor(null);
        setAvailability(null);
        setLoadError(null);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setLoadError(null);

      try {
        const response = await getDoctorAvailability(effectiveDoctorId, {
          signal: controller.signal,
        });

        if (!isActive) {
          return;
        }

        setDoctor(response.doctor);
        setAvailability(response);
        setSelectedDoctorId(response.doctor.id);

        if (response.availableDates.length > 0) {
          setVisibleMonth(startOfMonth(response.availableDates[0]));
        }
      } catch (error) {
        if (!isActive) {
          return;
        }

        setDoctor(null);
        setAvailability(null);
        setLoadError(
          error instanceof ApiError
            ? error.message
            : "Unable to load the booking details right now. Please try again.",
        );
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadBookingData();

    return () => {
      isActive = false;
      controller.abort();
    };
  }, [effectiveDoctorId, reloadKey, setSelectedDoctorId]);

  const allSlots = useMemo(() => {
    if (!availability) {
      return [];
    }

    return [...availability.morningSlots, ...availability.afternoonSlots];
  }, [availability]);

  const availableSlots = useMemo(() => {
    if (!selectedDate) {
      return [];
    }

    return filterBookableSlotsForDate(
      allSlots.filter((slot) => slot.appointmentType === selectedAppointmentType),
      selectedDate,
      currentDateTime,
    );
  }, [allSlots, currentDateTime, selectedAppointmentType, selectedDate]);

  const filteredAvailableDates = useMemo(() => {
    if (!availability) {
      return [];
    }

    return availability.availableDates.filter((date) =>
      allSlots.some(
        (slot) =>
          !slot.isBooked &&
          slot.appointmentType === selectedAppointmentType &&
          slot.availableDate === createDateKey(date),
      ),
    );
  }, [allSlots, availability, selectedAppointmentType]);

  const selectedSlot = useMemo(
    () => availableSlots.find((slot) => slot.id === selectedSlotId) ?? null,
    [availableSlots, selectedSlotId],
  );

  const defaultPatientValues = useMemo(
    () => ({
      appointment_type: selectedAppointmentType,
      full_name: storedPatientDetails?.full_name ?? "",
      email: storedPatientDetails?.email ?? "",
      phone: storedPatientDetails?.phone ?? "",
      health_description: storedPatientDetails?.health_description ?? "",
    }),
    [selectedAppointmentType, storedPatientDetails],
  );

  const handleDateSelect = (date: Date | undefined) => {
    setBookingError(null);
    setSelectedDate(date);
    setSelectedSlotId(null);
    setSelectedDateStore(date ? createDateKey(date) : null);
    setSelectedTimeStore(null);
    setSelectedAvailabilityId(null);
  };

  const handleSlotSelect = (slot: AvailabilitySlot) => {
    setBookingError(null);
    setSelectedSlotId(slot.id);
    setSelectedAvailabilityId(slot.id);
    setSelectedTimeStore(slot.startTime);
  };

  const handleAppointmentTypeChange = (appointmentType: AppointmentType) => {
    setBookingError(null);
    setSelectedAppointmentType(appointmentType);
    setAppointmentTypeStore(appointmentType);
  };

  const handleSubmit = async (values: AppointmentFormValues) => {
    if (!doctor || !selectedDate || !selectedSlot) {
      setBookingError("Select a date and time before confirming the booking.");
      return;
    }

    if (
      isElapsedAppointmentSlot(
        selectedDate,
        selectedSlot.startTime,
        currentDateTime,
      )
    ) {
      setBookingError(
        "Selected time has already passed. Please choose a different slot.",
      );
      setSelectedSlotId(null);
      setSelectedAvailabilityId(null);
      setSelectedTimeStore(null);
      return;
    }

    setBookingError(null);

    try {
      const response = await createAppointment({
        doctor_id: doctor.backendId,
        availability_id: selectedSlot.id,
        appointment_date: createDateKey(selectedDate),
        start_time: selectedSlot.startTime,
        appointment_type: values.appointment_type,
        patient: {
          full_name: values.full_name,
          email: values.email,
          phone: values.phone?.trim() ? values.phone.trim() : null,
        },
        health_description: values.health_description?.trim() || null,
      });

      setSelectedDoctorId(doctor.id);
      setSelectedAvailabilityId(selectedSlot.id);
      setSelectedDateStore(createDateKey(selectedDate));
      setSelectedTimeStore(selectedSlot.startTime);
      setAppointmentTypeStore(values.appointment_type);
      setPatientDetailsStore({
        full_name: values.full_name,
        email: values.email,
        phone: values.phone,
        health_description: values.health_description,
      });
      setAppointmentIdStore(response.id);
      setConfirmationCodeStore(response.confirmation_code);

      router.push(
        `/appointments/confirmation?appointmentId=${response.id}&doctorId=${doctor.backendId}`,
      );
    } catch (error) {
      setBookingError(
        error instanceof ApiError
          ? error.message
          : "Unable to create the appointment right now. Please try again.",
      );
    }
  };

  if (!effectiveDoctorId) {
    return <NoDoctorState />;
  }

  if (isLoading && !doctor) {
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

  if (!doctor || !availability) {
    return <NoDoctorState />;
  }

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
                availableDates={filteredAvailableDates}
                onDateSelect={handleDateSelect}
                month={visibleMonth}
                onMonthChange={setVisibleMonth}
                referenceDate={currentDateTime}
              />
            </section>

            <AppointmentAvailability
              selectedDate={selectedDate}
              selectedSlotId={selectedSlotId}
              availableSlots={availableSlots}
              onSlotSelect={handleSlotSelect}
            />
          </div>

          <div className="space-y-6">
            <DoctorSummaryCard doctor={doctor} />

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
                  defaultValues={defaultPatientValues}
                  isBookingReady={Boolean(selectedDate && selectedSlot)}
                  onSubmit={handleSubmit}
                  onAppointmentTypeChange={handleAppointmentTypeChange}
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

export default function AppointmentsPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <AppointmentsPageContent />
    </Suspense>
  );
}
