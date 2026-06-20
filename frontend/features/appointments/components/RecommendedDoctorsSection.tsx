"use client";

import * as React from "react";

import { format, isToday, isTomorrow, parseISO } from "date-fns";
import { useRouter } from "next/navigation";

import { DoctorCard } from "@/components/doctors/DoctorCard";
import { useRecommendedDoctors } from "@/features/appointments/hooks/use-recommended-doctors";
import type { RecommendedDoctor } from "@/features/appointments/types";
import type { Doctor } from "@/features/doctors/types";
import { doctors as mockDoctors } from "@/features/doctors/mock-doctors";

function formatNextAvailable(dateValue: string, slot: string) {
  try {
    const parsedDate = parseISO(dateValue);

    if (isToday(parsedDate)) {
      return `Today, ${slot}`;
    }

    if (isTomorrow(parsedDate)) {
      return `Tomorrow, ${slot}`;
    }

    return `${format(parsedDate, "EEE, MMM d")}, ${slot}`;
  } catch {
    return `${dateValue}, ${slot}`;
  }
}

function toDoctorCardModel(
  appointmentId: number,
  recommendedDoctor: RecommendedDoctor,
): Doctor {
  const fallbackDoctor =
    mockDoctors.find((doctor) => doctor.backendId === recommendedDoctor.doctor_id) ??
    mockDoctors.find((doctor) => doctor.name === recommendedDoctor.doctor_name);

  return {
    id: `recommended-${appointmentId}-${recommendedDoctor.doctor_id}`,
    backendId: recommendedDoctor.doctor_id,
    name: recommendedDoctor.doctor_name,
    specialty: recommendedDoctor.specialty,
    rating: recommendedDoctor.rating,
    reviewCount: recommendedDoctor.review_count,
    description:
      fallbackDoctor?.description ??
      `Available for booking at ${recommendedDoctor.clinic_name}.`,
    languages: fallbackDoctor?.languages ?? ["CareNow"],
    clinic: recommendedDoctor.clinic_name,
    location: fallbackDoctor?.location ?? "Available online",
    feeRange: fallbackDoctor?.feeRange ?? { min: 0, max: 0 },
    nextAvailable: formatNextAvailable(
      recommendedDoctor.next_available_date,
      recommendedDoctor.next_available_slot,
    ),
    appointmentTypes: fallbackDoctor?.appointmentTypes ?? ["IN_PERSON"],
    consultationFee: fallbackDoctor?.consultationFee ?? 0,
    durationMinutes: fallbackDoctor?.durationMinutes ?? 30,
    avatar: {
      imageSrc: recommendedDoctor.profile_image || fallbackDoctor?.avatar.imageSrc || "/avatars/doctor-sarah.svg",
      imageAlt:
        fallbackDoctor?.avatar.imageAlt ||
        `Portrait placeholder for ${recommendedDoctor.doctor_name}`,
    },
  };
}

function SelectionPrompt() {
  return (
    <div className="rounded-[22px] border border-dashed border-slate-200 bg-slate-50/80 px-5 py-8 text-center">
      <h3 className="text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950">
        Available Doctors
      </h3>
      <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-600">
        Select an appointment to load doctors recommended for the same specialty.
      </p>
    </div>
  );
}

function LoadingState() {
  return (
    <section aria-labelledby="available-doctors-heading" className="border-t border-slate-100 pt-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h3
            id="available-doctors-heading"
            className="text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950"
          >
            Available Doctors
          </h3>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Loading doctors recommended for this appointment.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-5">
        <div className="h-[280px] animate-pulse rounded-[24px] bg-slate-50" />
        <div className="h-[280px] animate-pulse rounded-[24px] bg-slate-50" />
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
    <section aria-labelledby="available-doctors-heading" className="border-t border-slate-100 pt-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h3
            id="available-doctors-heading"
            className="text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950"
          >
            Available Doctors
          </h3>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Recommended doctors could not be loaded for this appointment.
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-[20px] border border-rose-200 bg-rose-50 px-5 py-6 text-rose-800">
        <p className="text-sm font-semibold uppercase tracking-[0.16em]">
          Recommendation error
        </p>
        <p className="mt-2 text-sm leading-6">{message}</p>
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 inline-flex h-11 items-center justify-center rounded-[14px] bg-rose-600 px-5 text-sm font-semibold text-white transition hover:bg-rose-700"
        >
          Try again
        </button>
      </div>
    </section>
  );
}

function EmptyState({ specialty }: { specialty: string }) {
  return (
    <section aria-labelledby="available-doctors-heading" className="border-t border-slate-100 pt-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h3
            id="available-doctors-heading"
            className="text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950"
          >
            Available Doctors
          </h3>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            No recommended doctors are currently available for this appointment.
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-[22px] border border-brand-100 bg-brand-50/55 px-5 py-8 text-center">
        <p className="text-lg font-semibold tracking-[-0.03em] text-slate-950">
          No {specialty || "matching"} doctors available
        </p>
        <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-600">
          There are no other bookable doctors to recommend from this specialty right now.
        </p>
      </div>
    </section>
  );
}

export function RecommendedDoctorsSection({
  appointmentId,
}: {
  appointmentId: number | null;
}) {
  const router = useRouter();
  const { data, error, isLoading, refetch } = useRecommendedDoctors(appointmentId);

  if (appointmentId === null) {
    return <SelectionPrompt />;
  }

  if (isLoading && !data) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={refetch} />;
  }

  if (!data || data.recommended_doctors.length === 0) {
    return <EmptyState specialty={data?.specialty ?? ""} />;
  }

  const recommendedDoctors = data.recommended_doctors.map((recommendedDoctor) =>
    toDoctorCardModel(data.appointment_id, recommendedDoctor),
  );
  const [featuredDoctor, ...remainingDoctors] = recommendedDoctors;

  return (
    <section aria-labelledby="available-doctors-heading" className="border-t border-slate-100 pt-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h3
            id="available-doctors-heading"
            className="text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950"
          >
            Available Doctors
          </h3>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Doctors recommended from the same specialty as the selected appointment.
          </p>
        </div>
        <span className="rounded-full bg-brand-50 px-4 py-2 text-sm font-semibold text-brand-700 ring-1 ring-brand-100">
          {recommendedDoctors.length} available
        </span>
      </div>

      <div className="mt-6 space-y-5">
        <DoctorCard
          key={featuredDoctor.id}
          doctor={featuredDoctor}
          isSelected={false}
          onSelect={() => undefined}
          onAction={(doctor) => {
            router.push(`/appointments?doctorId=${doctor.backendId}`);
          }}
          actionLabel="Book Now"
          selectedActionLabel="Booked"
          variant="featured"
        />

        {remainingDoctors.length > 0 ? (
          <div className="grid gap-5 md:grid-cols-2">
            {remainingDoctors.map((doctor) => (
              <DoctorCard
                key={doctor.id}
                doctor={doctor}
                isSelected={false}
                onSelect={() => undefined}
                onAction={(selectedDoctor) => {
                  router.push(`/appointments?doctorId=${selectedDoctor.backendId}`);
                }}
                actionLabel="Book"
                selectedActionLabel="Booked"
                variant="compact"
              />
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}
