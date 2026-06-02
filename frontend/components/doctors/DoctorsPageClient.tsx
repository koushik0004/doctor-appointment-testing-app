"use client";

import { useEffect, useMemo, useState } from "react";
import { BookingSummary } from "@/components/doctors/BookingSummary";
import { DoctorCard } from "@/components/doctors/DoctorCard";
import { DoctorFilters } from "@/components/doctors/DoctorFilters";
import { DoctorsPagination } from "@/components/doctors/DoctorsPagination";
import { doctors } from "@/features/doctors/mock-doctors";
import {
  AppointmentType,
  Doctor,
  DoctorSortOption,
} from "@/features/doctors/types";

const PAGE_SIZE = 4;

const availabilityOrder = [
  "Today",
  "Tomorrow",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
  "Monday",
  "Tuesday",
];

function compareAvailability(left: Doctor, right: Doctor) {
  const leftIndex = availabilityOrder.findIndex((entry) =>
    left.nextAvailable.startsWith(entry),
  );
  const rightIndex = availabilityOrder.findIndex((entry) =>
    right.nextAvailable.startsWith(entry),
  );

  return leftIndex - rightIndex;
}

export function DoctorsPageClient() {
  const [selectedSpecialty, setSelectedSpecialty] = useState("All specialties");
  const [selectedAppointmentType, setSelectedAppointmentType] = useState<
    AppointmentType | "ALL"
  >("ALL");
  const [sortBy, setSortBy] = useState<DoctorSortOption>("TOP_RATED");
  const [selectedDoctorId, setSelectedDoctorId] = useState(doctors[0]?.id ?? "");
  const [currentPage, setCurrentPage] = useState(1);

  const filteredDoctors = useMemo(() => {
    return doctors.filter((doctor) => {
      const matchesSpecialty =
        selectedSpecialty === "All specialties" ||
        doctor.specialty === selectedSpecialty;
      const matchesAppointmentType =
        selectedAppointmentType === "ALL" ||
        doctor.appointmentTypes.includes(selectedAppointmentType);

      return matchesSpecialty && matchesAppointmentType;
    });
  }, [selectedAppointmentType, selectedSpecialty]);

  const sortedDoctors = useMemo(() => {
    if (sortBy === "TOP_RATED") {
      return filteredDoctors;
    }

    return [...filteredDoctors].sort((left, right) => {
      const availabilityComparison = compareAvailability(left, right);
      if (availabilityComparison !== 0) {
        return availabilityComparison;
      }

      if (right.rating !== left.rating) {
        return right.rating - left.rating;
      }

      return right.reviewCount - left.reviewCount;
    });
  }, [filteredDoctors, sortBy]);

  const totalPages = Math.max(1, Math.ceil(sortedDoctors.length / PAGE_SIZE));
  const paginatedDoctors = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return sortedDoctors.slice(start, start + PAGE_SIZE);
  }, [currentPage, sortedDoctors]);

  const selectedDoctor =
    sortedDoctors.find((doctor) => doctor.id === selectedDoctorId) ?? null;

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedAppointmentType, selectedSpecialty, sortBy]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  useEffect(() => {
    if (selectedDoctorId && sortedDoctors.some((doctor) => doctor.id === selectedDoctorId)) {
      return;
    }

    setSelectedDoctorId(sortedDoctors[0]?.id ?? "");
  }, [selectedDoctorId, sortedDoctors]);

  return (
    <section className="-mx-4 bg-white sm:-mx-6 lg:-mx-8 xl:-mx-10">
      <div className="grid min-h-[calc(100vh-220px)] gap-0 lg:grid-cols-[280px_minmax(0,1fr)_340px]">
        <DoctorFilters
          selectedSpecialty={selectedSpecialty}
          selectedAppointmentType={selectedAppointmentType}
          onSelectSpecialty={setSelectedSpecialty}
          onSelectAppointmentType={setSelectedAppointmentType}
        />

        <div className="min-w-0 px-6 py-8 sm:px-8 lg:px-10 xl:px-12">
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
              <div className="space-y-3">
                <h1 className="text-[3.1rem] font-semibold leading-none tracking-[-0.05em] text-slate-900">
                  Available Doctors
                </h1>
                <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[0.98rem] text-slate-500">
                  <p className="max-w-[160px]">Showing {sortedDoctors.length} top-rated providers in</p>
                  <p className="font-semibold leading-5 text-slate-700">London, UK</p>
                  <button
                    type="button"
                    className="font-semibold text-sky-500 transition hover:text-sky-600"
                  >
                    Change Location
                  </button>
                </div>
              </div>

              <label className="flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                <span>Sort By:</span>
                <select
                  value={sortBy}
                  onChange={(event) =>
                    setSortBy(event.target.value as DoctorSortOption)
                  }
                  className="min-w-40 rounded-[12px] border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium normal-case tracking-normal text-slate-700 outline-none transition focus:border-sky-300 focus:bg-white"
                >
                  <option value="TOP_RATED">Top Rated</option>
                  <option value="EARLIEST_AVAILABILITY">
                    Earliest Availability
                  </option>
                </select>
              </label>
            </div>

            <div className="space-y-5">
              {paginatedDoctors.length > 0 ? (
                paginatedDoctors.map((doctor) => (
                  <DoctorCard
                    key={doctor.id}
                    doctor={doctor}
                    isSelected={doctor.id === selectedDoctorId}
                    onSelect={setSelectedDoctorId}
                  />
                ))
              ) : (
                <div className="rounded-[20px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
                  <h2 className="text-xl font-semibold text-slate-900">
                    No doctors match the current filters
                  </h2>
                  <p className="mt-3 text-sm text-slate-500">
                    Adjust specialty or appointment type to see more options.
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-8">
            <DoctorsPagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          </div>
        </div>

        <div className="border-l border-slate-200 px-6 py-8 xl:px-7">
          <BookingSummary doctor={selectedDoctor} />
        </div>
      </div>
    </section>
  );
}
