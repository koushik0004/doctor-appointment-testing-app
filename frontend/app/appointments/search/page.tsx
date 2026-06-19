"use client";

import * as React from "react";

import type { FieldError, FieldErrors, Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { AppointmentResultCard } from "@/features/appointments/components/AppointmentResultCard";
import { useAppointmentSearch } from "@/features/appointments/hooks/use-appointment-search";

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
  return (
    <label className="block">
      <span className="text-sm font-semibold text-slate-700">{label}</span>
      <input
        type={type}
        name={name}
        value={value}
        onChange={(event) => onChange(name, event.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        inputMode={inputMode}
        aria-invalid={Boolean(errorMessage)}
        className="mt-2 h-12 w-full rounded-[14px] border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-300 focus:ring-4 focus:ring-sky-50"
      />
      {errorMessage ? (
        <p className="mt-2 text-sm text-rose-600">{errorMessage}</p>
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
    <div className="rounded-[20px] border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center">
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
    </div>
  );
}

function LoadingStateCard() {
  return (
    <div className="rounded-[20px] border border-sky-100 bg-sky-50 px-5 py-6 text-sky-800">
      <p className="text-sm font-semibold uppercase tracking-[0.16em]">Loading</p>
      <p className="mt-2 text-sm leading-6">
        Searching appointments and fetching the latest API response...
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

function SearchSidebarCard({
  title,
  description,
  items,
}: {
  title: string;
  description: string;
  items: string[];
}) {
  return (
    <div className="rounded-[24px] border border-slate-100 bg-white p-6 shadow-soft">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
        Search Guide
      </p>
      <h3 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
        {title}
      </h3>
      <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
      <ul className="mt-5 space-y-3 text-sm leading-6 text-slate-600">
        {items.map((item) => (
          <li
            key={item}
            className="rounded-[16px] bg-slate-50 px-4 py-3 ring-1 ring-slate-100"
          >
            {item}
          </li>
        ))}
      </ul>
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
          Appointment Results
        </p>
        <h2 className="mt-2 text-[2rem] font-semibold tracking-[-0.05em] text-slate-950">
          {count === null ? "Search results will appear here" : "Matched appointments"}
        </h2>
      </div>
      {count !== null ? (
        <span className="rounded-full bg-sky-50 px-4 py-2 text-sm font-semibold text-sky-700 ring-1 ring-sky-100">
          {count} result{count === 1 ? "" : "s"}
        </span>
      ) : null}
    </div>
  );
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

  const currentValues = watch();
  const parsedCurrentValues = searchFormSchema.safeParse(currentValues);
  const searchIsValid = parsedCurrentValues.success;
  const hasAnySearchValue = Boolean(
    currentValues.name.trim() ||
      currentValues.email.trim() ||
      currentValues.phone.trim(),
  );

  const onSubmit = handleSubmit(async (values) => {
    await search(values);
  });

  const appointments = searchResponse?.appointments ?? [];

  function handleReset() {
    reset(emptySearchValues);
    resetSearch();
  }

  return (
    <section className="py-10 lg:py-14">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="rounded-[28px] border border-sky-100 bg-gradient-to-br from-sky-50 via-white to-cyan-50 p-6 shadow-soft lg:p-8">
          <span className="inline-flex rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">
            Appointment search
          </span>
          <h1 className="mt-4 text-4xl font-semibold tracking-[-0.05em] text-slate-950 lg:text-5xl">
            Search Your Appointment
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
            Find previously booked appointments using your name, email, or phone
            number.
          </p>
        </div>

        <div className="grid gap-8 xl:grid-cols-[1.12fr_0.88fr]">
          <form
            onSubmit={onSubmit}
            className="rounded-[24px] border border-slate-100 bg-white p-6 shadow-soft lg:p-8"
          >
            <div className="grid gap-5 md:grid-cols-3">
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

            {!searchIsValid && !hasAnySearchValue ? (
              <p className="mt-4 rounded-[16px] border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                Enter at least one search detail to enable Search.
              </p>
            ) : null}

            {errors.root?.message ? (
              <p className="mt-4 rounded-[16px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {errors.root.message}
              </p>
            ) : null}

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={!searchIsValid || isSubmitting || isLoading}
                className="inline-flex h-12 items-center justify-center rounded-[14px] bg-sky-500 px-6 text-sm font-semibold text-white transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isLoading ? "Searching..." : "Search"}
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="inline-flex h-12 items-center justify-center rounded-[14px] border border-slate-200 bg-white px-6 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-950"
              >
                Reset
              </button>
            </div>
          </form>

          <aside className="rounded-[24px] border border-slate-100 bg-white p-6 shadow-soft lg:p-8">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
              Search tips
            </p>
            <h2 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              Use one or more patient details to narrow the search.
            </h2>
            <ul className="mt-5 space-y-4 text-sm leading-6 text-slate-600">
              <li className="rounded-[16px] bg-slate-50 px-4 py-3">
                Name works best for quick lookups when spelling is known.
              </li>
              <li className="rounded-[16px] bg-slate-50 px-4 py-3">
                Email and phone are useful for confirming the exact booking.
              </li>
              <li className="rounded-[16px] bg-slate-50 px-4 py-3">
                Results below show appointment cards with a View Details action.
              </li>
            </ul>
          </aside>
        </div>

        <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_360px]">
          <section className="rounded-[28px] border border-slate-100 bg-white p-6 shadow-soft lg:p-8">
            <ResultsHeader count={hasSearched ? searchResponse?.count ?? 0 : null} />

            <div className="mt-6">
              {isLoading ? (
                <LoadingStateCard />
              ) : searchError ? (
                <ErrorStateCard message={searchError} />
              ) : !hasSearched ? (
                <EmptyStateCard
                  title="No search has been run yet"
                  description="Use the form above to load appointment cards from the API."
                />
              ) : appointments.length === 0 ? (
                <EmptyStateCard
                  title="No matching appointments"
                  description="The API returned no appointments for the provided search details."
                />
              ) : (
                <div className="grid gap-5">
                  {appointments.map((appointment, index) => (
                    <div
                      key={appointment.appointment_id}
                      className={
                        index === 0
                          ? "rounded-[28px] border border-sky-100 bg-gradient-to-br from-sky-50 to-white p-1 shadow-[0_24px_60px_-36px_rgba(56,189,248,0.55)]"
                          : ""
                      }
                    >
                      <AppointmentResultCard
                        appointment={appointment}
                        onViewDetails={() => {
                          // Details panel is intentionally deferred to the next step.
                        }}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          <aside className="space-y-5">
            <SearchSidebarCard
              title="Use one or more patient details"
              description="Search by name, email, or phone. The API trims whitespace, validates email format, and returns matching appointments as cards."
              items={[
                "Name supports partial, case-insensitive matching.",
                "Email and phone use exact matching after trimming.",
                "Result cards show appointment ID, patient, doctor, schedule, type, and status.",
              ]}
            />

            <div className="rounded-[24px] border border-slate-100 bg-white p-6 shadow-soft">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
                Coming next
              </p>
              <h3 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
                Details panel
              </h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                The View Details action is in place, but the full appointment
                details panel stays out of this step.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}
