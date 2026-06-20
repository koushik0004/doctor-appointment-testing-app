"use client";

import * as React from "react";

import type { FieldError, FieldErrors, Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { AppointmentDetailsPanel } from "@/features/appointments/components/AppointmentDetailsPanel";
import { AppointmentResultCard } from "@/features/appointments/components/AppointmentResultCard";
import { useAppointmentSearch } from "@/features/appointments/hooks/use-appointment-search";
import { DoctorCard } from "@/components/doctors/DoctorCard";
import { doctors } from "@/features/doctors/mock-doctors";
import { cn } from "@/lib/utils";

const searchFormSchema = z
  .object({
    name: z.string().trim(),
    email: z
      .string()
      .trim()
      .refine((value) => value === "" || z.string().email().safeParse(value).success, {
        message: "Enter a valid email address.",
      }),
    phone: z.string().trim().refine((value) => value === "" || /^\d+$/.test(value), {
      message: "Phone must contain numbers only.",
    }),
  })
  .superRefine((values, context) => {
    if (!values.name && !values.email && !values.phone) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        path: [],
        message: "Enter at least one search detail to look up an appointment.",
      });
    }
  });

type SearchFormValues = z.infer<typeof searchFormSchema>;

const emptySearchValues: SearchFormValues = {
  name: "",
  email: "",
  phone: "",
};

const searchFormResolver: Resolver<SearchFormValues> = async (values) => {
  const parsedValues = searchFormSchema.safeParse(values);

  if (parsedValues.success) {
    return {
      values: parsedValues.data,
      errors: {},
    };
  }

  const errors: FieldErrors<SearchFormValues> = {};

  for (const issue of parsedValues.error.issues) {
    const fieldName = issue.path[0] as keyof SearchFormValues | undefined;

    if (!fieldName) {
      errors.root = {
        type: issue.code,
        message: issue.message,
      } as FieldError;
      continue;
    }

    if (errors[fieldName]) {
      continue;
    }

    errors[fieldName] = {
      type: issue.code,
      message: issue.message,
    };
  }

  return {
    values: {},
    errors,
  };
};

function SearchField({
  label,
  name,
  value,
  onChange,
  placeholder,
  type = "text",
  autoComplete,
  inputMode,
  errorMessage,
}: {
  label: string;
  name: keyof SearchFormValues;
  value: string;
  onChange: (name: keyof SearchFormValues, value: string) => void;
  placeholder: string;
  type?: string;
  autoComplete?: string;
  inputMode?: React.HTMLAttributes<HTMLInputElement>["inputMode"];
  errorMessage?: string;
}) {
  const inputId = `${name}-input`;
  const errorId = `${name}-error`;

  return (
    <label className="block">
      <span className="text-sm font-semibold text-slate-700">{label}</span>
      <input
        id={inputId}
        type={type}
        name={name}
        value={value}
        onChange={(event) => onChange(name, event.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        inputMode={inputMode}
        aria-invalid={Boolean(errorMessage)}
        aria-describedby={errorMessage ? errorId : undefined}
        className="mt-2 h-12 w-full rounded-[14px] border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100 focus:ring-offset-2"
      />
      {errorMessage ? (
        <p id={errorId} className="mt-2 text-sm text-rose-600">
          {errorMessage}
        </p>
      ) : null}
    </label>
  );
}

function EmptyStateCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-[22px] border border-brand-100 bg-brand-50/55 px-5 py-8 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-white text-brand-600 ring-1 ring-brand-100">
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          className="h-5 w-5"
        >
          <rect x="3" y="5" width="18" height="16" rx="3" />
          <path d="M16 3v4M8 3v4M3 10h18" />
        </svg>
      </div>
      <h3 className="mt-4 text-lg font-semibold tracking-[-0.03em] text-slate-950">
        {title}
      </h3>
      <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-600">
        {description}
      </p>
    </div>
  );
}

function ErrorStateCard({ message }: { message: string }) {
  return (
    <div className="rounded-[20px] border border-rose-200 bg-rose-50 px-5 py-6 text-rose-800">
      <p className="text-sm font-semibold uppercase tracking-[0.16em]">
        Search failed
      </p>
      <p className="mt-2 text-sm leading-6">{message}</p>
    </div>
  );
}

function ResultsHeader({
  count,
}: {
  count: number | null;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
          Search Results
        </p>
        <h2
          id="appointment-results-heading"
          className="mt-2 text-[2rem] font-semibold tracking-[-0.05em] text-slate-950"
        >
          {count === null ? "Search results will appear here" : "Matched appointments"}
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
          Review each booking card, then open a result to inspect the complete
          appointment details in the booking sidebar.
        </p>
      </div>
      {count !== null ? (
        <span
          className="rounded-full bg-brand-50 px-4 py-2 text-sm font-semibold text-brand-700 ring-1 ring-brand-100"
          aria-live="polite"
        >
          {count} result{count === 1 ? "" : "s"}
        </span>
      ) : null}
    </div>
  );
}

function buildAvailableDoctors(matchedDoctorNames: string[]) {
  const matchedDoctorNameSet = new Set(matchedDoctorNames);

  return doctors
    .filter((doctor) => !matchedDoctorNameSet.has(doctor.name))
    .slice(0, 3);
}

export default function AppointmentSearchPage() {
  const {
    handleSubmit,
    watch,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<SearchFormValues>({
    resolver: searchFormResolver,
    defaultValues: emptySearchValues,
    mode: "onChange",
    reValidateMode: "onChange",
  });

  const {
    data: searchResponse,
    error: searchError,
    hasSearched,
    isLoading,
    resetSearch,
    search,
  } = useAppointmentSearch();
  const [selectedAppointmentId, setSelectedAppointmentId] = React.useState<
    number | null
  >(null);
  const [selectedAvailableDoctorId, setSelectedAvailableDoctorId] =
    React.useState("");

  const currentValues = watch();
  const parsedCurrentValues = searchFormSchema.safeParse(currentValues);
  const searchIsValid = parsedCurrentValues.success;
  const hasAnySearchValue = Boolean(
    currentValues.name.trim() ||
      currentValues.email.trim() ||
      currentValues.phone.trim(),
  );

  const onSubmit = handleSubmit(async (values) => {
    setSelectedAppointmentId(null);
    await search(values);
  });

  const appointments = React.useMemo(
    () => searchResponse?.appointments ?? [],
    [searchResponse?.appointments],
  );
  const availableDoctors = React.useMemo(
    () =>
      buildAvailableDoctors(appointments.map((appointment) => appointment.doctor_name)),
    [appointments],
  );

  function handleReset() {
    reset(emptySearchValues);
    resetSearch();
    setSelectedAppointmentId(null);
    setSelectedAvailableDoctorId("");
  }

  return (
    <section className="py-8 lg:py-12">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="overflow-hidden rounded-[32px] border border-brand-100 bg-brand-50/65 shadow-soft">
          <div className="px-6 py-10 text-center sm:px-10 lg:px-16 lg:py-14">
            <span className="inline-flex rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-brand-700 ring-1 ring-brand-100">
              Appointment search
            </span>
            <h1 className="mx-auto mt-5 max-w-5xl text-4xl font-semibold tracking-[-0.06em] text-slate-950 sm:text-5xl lg:text-6xl">
              Find your{" "}
              <span className="text-brand-500">healthcare</span> appointment.
            </h1>
            <p className="mx-auto mt-4 max-w-3xl text-base leading-7 text-slate-600 sm:text-lg">
              Search by patient name, email, or phone number, then open any
              booking to review the doctor, appointment, and patient details in
              one place.
            </p>
          </div>
        </div>

        <form
          onSubmit={onSubmit}
          className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft lg:p-8"
          aria-label="Search appointments"
        >
          <div className="rounded-[24px] border border-brand-100 bg-brand-50/45 p-5 sm:p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
                  Search details
                </p>
                <h2 className="mt-2 text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950">
                  Look up an existing booking
                </h2>
              </div>
              <p className="max-w-md text-sm leading-6 text-slate-600">
                Provide any one patient detail. Adding more details narrows the
                matched appointments.
              </p>
            </div>

            <div className="mt-6 grid gap-5 md:grid-cols-3">
              <SearchField
                label="Name"
                name="name"
                value={currentValues.name}
                onChange={(field, value) =>
                  setValue(field, value, {
                    shouldDirty: true,
                    shouldValidate: true,
                  })
                }
                placeholder="Enter patient name"
                autoComplete="name"
                errorMessage={errors.name?.message}
              />
              <SearchField
                label="Email"
                name="email"
                value={currentValues.email}
                onChange={(field, value) =>
                  setValue(field, value, {
                    shouldDirty: true,
                    shouldValidate: true,
                  })
                }
                placeholder="Enter email address"
                type="email"
                autoComplete="email"
                errorMessage={errors.email?.message}
              />
              <SearchField
                label="Phone"
                name="phone"
                value={currentValues.phone}
                onChange={(field, value) =>
                  setValue(field, value, {
                    shouldDirty: true,
                    shouldValidate: true,
                  })
                }
                placeholder="Enter phone number"
                autoComplete="tel"
                inputMode="numeric"
                errorMessage={errors.phone?.message}
              />
            </div>
          </div>

          {!searchIsValid && !hasAnySearchValue ? (
            <p className="mt-4 rounded-[16px] border border-brand-100 bg-brand-50 px-4 py-3 text-sm text-brand-900">
              Enter at least one search detail to enable Search.
            </p>
          ) : null}

          {errors.root?.message ? (
            <p
              className="mt-4 rounded-[16px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
              aria-live="assertive"
            >
              {errors.root.message}
            </p>
          ) : null}

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={!searchIsValid || isSubmitting || isLoading}
              aria-busy={isLoading}
              className={cn(
                "inline-flex h-12 items-center justify-center rounded-[14px] bg-brand-500 px-6 text-sm font-semibold text-white transition hover:bg-brand-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-100 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-300",
                isLoading ? "gap-3" : "",
              )}
            >
              {isLoading ? (
                <>
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    className="h-4 w-4 animate-spin"
                    fill="none"
                  >
                    <circle
                      cx="12"
                      cy="12"
                      r="8"
                      className="opacity-25"
                      stroke="currentColor"
                      strokeWidth="2"
                    />
                    <path
                      d="M20 12a8 8 0 0 0-8-8"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                  <span>Searching...</span>
                </>
              ) : (
                "Search"
              )}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="inline-flex h-12 items-center justify-center rounded-[14px] border border-slate-200 bg-white px-6 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-950 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-100 focus-visible:ring-offset-2"
            >
              Reset
            </button>
          </div>
        </form>

        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.45fr)_minmax(380px,0.95fr)]">
          <section
            className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft lg:p-8"
            aria-labelledby="appointment-results-heading"
          >
            <ResultsHeader count={hasSearched ? searchResponse?.count ?? 0 : null} />

            <div className="mt-6" aria-live="polite" aria-busy={isLoading}>
              {isLoading ? (
                <div className="grid gap-4">
                  <div className="h-[166px] animate-pulse rounded-[24px] bg-slate-50" />
                  <div className="h-[166px] animate-pulse rounded-[24px] bg-slate-50" />
                  <div className="h-[166px] animate-pulse rounded-[24px] bg-slate-50" />
                </div>
              ) : searchError ? (
                <ErrorStateCard message={searchError} />
              ) : !hasSearched ? (
                <EmptyStateCard
                  title="No search has been run yet"
                  description="Use the form above to load matching appointment cards."
                />
              ) : appointments.length === 0 ? (
                <EmptyStateCard
                  title="No matching appointments"
                  description="No bookings matched the search details you entered."
                />
              ) : (
                <div className="space-y-8">
                  <div className="grid gap-5">
                    {appointments.map((appointment) => (
                      <AppointmentResultCard
                        key={appointment.appointment_id}
                        appointment={appointment}
                        isSelected={selectedAppointmentId === appointment.appointment_id}
                        onViewDetails={(appointmentId) => {
                          setSelectedAppointmentId(appointmentId);
                        }}
                      />
                    ))}
                  </div>

                  {availableDoctors.length > 0 ? (
                    <section
                      aria-labelledby="available-doctors-heading"
                      className="border-t border-slate-100 pt-8"
                    >
                      <div className="flex flex-wrap items-end justify-between gap-4">
                        <div>
                          <h3
                            id="available-doctors-heading"
                            className="text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950"
                          >
                            Available Doctors
                          </h3>
                          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                            Reusing the same doctor card pattern for a simple
                            list of other available specialists.
                          </p>
                        </div>
                        <span className="rounded-full bg-brand-50 px-4 py-2 text-sm font-semibold text-brand-700 ring-1 ring-brand-100">
                          {availableDoctors.length} available
                        </span>
                      </div>

                      <div className="mt-6 grid gap-5">
                        {availableDoctors.map((doctor) => (
                          <DoctorCard
                            key={doctor.id}
                            doctor={doctor}
                            isSelected={doctor.id === selectedAvailableDoctorId}
                            onSelect={setSelectedAvailableDoctorId}
                            actionLabel="Book"
                            selectedActionLabel="Booked"
                          />
                        ))}
                      </div>
                    </section>
                  ) : null}
                </div>
              )}
            </div>
          </section>

          <aside className="space-y-5 xl:sticky xl:top-6">
            <AppointmentDetailsPanel appointmentId={selectedAppointmentId} />

            <div className="rounded-[28px] border border-sky-100 bg-sky-50/70 p-6 shadow-soft">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-500">
                CareNow Guarantee
              </p>
              <h3 className="mt-3 text-[1.75rem] font-semibold tracking-[-0.05em] text-slate-950">
                Booking support that matches the appointment flow
              </h3>
              <ul className="mt-5 space-y-4 text-sm leading-6 text-slate-600">
                <li className="flex items-start gap-3">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    className="mt-0.5 h-5 w-5 shrink-0 text-sky-500"
                  >
                    <path d="M20 6 9 17l-5-5" />
                  </svg>
                  <span>Verified medical professionals</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    className="mt-0.5 h-5 w-5 shrink-0 text-sky-500"
                  >
                    <circle cx="12" cy="12" r="9" />
                    <path d="M12 8v4l3 2" />
                  </svg>
                  <span>Instant booking confirmation</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    className="mt-0.5 h-5 w-5 shrink-0 text-sky-500"
                  >
                    <path d="M4 7a2 2 0 0 1 2-2h3l2 3h7a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z" />
                    <path d="M9 13h6" />
                  </svg>
                  <span>Telehealth options available</span>
                </li>
              </ul>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}
