"use client";

import * as React from "react";

import type { FieldErrors, Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";
import { z } from "zod";

type MockAppointment = {
  id: string;
  patientName: string;
  email: string;
  phone: string;
  appointmentDate: string;
  appointmentTime: string;
  doctorName: string;
  status: "Confirmed" | "Checked In" | "Completed";
  reason: string;
  appointmentType: "Video Visit" | "In Person";
};

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

const mockAppointments: MockAppointment[] = [
  {
    id: "apt-2048",
    patientName: "Ava Thompson",
    email: "ava.thompson@example.com",
    phone: "+1 (415) 555-0184",
    appointmentDate: "June 20, 2026",
    appointmentTime: "10:30 AM",
    doctorName: "Dr. Priya Shah",
    status: "Confirmed",
    reason: "Routine follow-up visit",
    appointmentType: "In Person",
  },
  {
    id: "apt-1982",
    patientName: "Jordan Lee",
    email: "jordan.lee@example.com",
    phone: "+1 (212) 555-0147",
    appointmentDate: "June 21, 2026",
    appointmentTime: "02:00 PM",
    doctorName: "Dr. Miguel Santos",
    status: "Completed",
    reason: "Annual wellness check",
    appointmentType: "Video Visit",
  },
  {
    id: "apt-1876",
    patientName: "Maya Patel",
    email: "maya.patel@example.com",
    phone: "+1 (646) 555-0130",
    appointmentDate: "June 22, 2026",
    appointmentTime: "11:15 AM",
    doctorName: "Dr. Elena Morris",
    status: "Checked In",
    reason: "Specialist consultation",
    appointmentType: "In Person",
  },
];

const statusStyles: Record<MockAppointment["status"], string> = {
  Confirmed: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100",
  "Checked In": "bg-sky-50 text-sky-700 ring-1 ring-sky-100",
  Completed: "bg-slate-100 text-slate-700 ring-1 ring-slate-200",
};

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
      };
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
  errorMessage,
}: {
  label: string;
  name: keyof SearchFormValues;
  value: string;
  onChange: (name: keyof SearchFormValues, value: string) => void;
  placeholder: string;
  type?: string;
  autoComplete?: string;
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

  const [submittedFilters, setSubmittedFilters] =
    React.useState<SearchFormValues | null>(null);
  const [selectedAppointmentId, setSelectedAppointmentId] = React.useState<
    string | null
  >(null);

  const currentValues = watch();
  const parsedCurrentValues = searchFormSchema.safeParse(currentValues);
  const searchIsValid = parsedCurrentValues.success;
  const hasAnySearchValue = Boolean(
    currentValues.name.trim() || currentValues.email.trim() || currentValues.phone.trim(),
  );

  const visibleAppointments = React.useMemo(() => {
    if (!submittedFilters) {
      return [];
    }

    return mockAppointments.filter((appointment) => {
      const normalizedName = submittedFilters.name.trim().toLowerCase();
      const normalizedEmail = submittedFilters.email.trim().toLowerCase();
      const normalizedPhone = submittedFilters.phone.trim();

      const matchesName =
        normalizedName.length === 0 ||
        appointment.patientName.toLowerCase().includes(normalizedName);
      const matchesEmail =
        normalizedEmail.length === 0 ||
        appointment.email.toLowerCase().includes(normalizedEmail);
      const matchesPhone =
        normalizedPhone.length === 0 ||
        appointment.phone.replace(/\D/g, "").includes(normalizedPhone);

      return matchesName && matchesEmail && matchesPhone;
    });
  }, [submittedFilters]);

  React.useEffect(() => {
    if (!visibleAppointments.length) {
      setSelectedAppointmentId(null);
      return;
    }

    if (!selectedAppointmentId) {
      setSelectedAppointmentId(visibleAppointments[0].id);
      return;
    }

    const selectedStillExists = visibleAppointments.some(
      (appointment) => appointment.id === selectedAppointmentId,
    );

    if (!selectedStillExists) {
      setSelectedAppointmentId(visibleAppointments[0].id);
    }
  }, [selectedAppointmentId, visibleAppointments]);

  const selectedAppointment =
    visibleAppointments.find(
      (appointment) => appointment.id === selectedAppointmentId,
    ) ?? null;
  const hasSubmittedSearch = Boolean(submittedFilters);

  const onSubmit = handleSubmit((values) => {
    setSubmittedFilters(values);
    setSelectedAppointmentId(mockAppointments[0].id);
  });

  function handleReset() {
    reset(emptySearchValues);
    setSubmittedFilters(null);
    setSelectedAppointmentId(null);
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
                type="text"
                autoComplete="tel"
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
                disabled={!searchIsValid || isSubmitting}
                className="inline-flex h-12 items-center justify-center rounded-[14px] bg-sky-500 px-6 text-sm font-semibold text-white transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                Search
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
                Results and appointment details below are mock placeholders for
                now.
              </li>
            </ul>
          </aside>
        </div>

        <div className="grid gap-8 xl:grid-cols-[1.08fr_0.92fr]">
          <section className="rounded-[24px] border border-slate-100 bg-white p-6 shadow-soft lg:p-8">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
                  Search Results Section
                </p>
                <h2 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
                  Appointment matches
                </h2>
              </div>
              {hasSubmittedSearch ? (
                <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">
                  Mock data loaded
                </span>
              ) : null}
            </div>

            <div className="mt-6 space-y-4">
              {!submittedFilters ? (
                <EmptyStateCard
                  title="No search has been run yet"
                  description="Use the form above to reserve this area for appointment search results."
                />
              ) : visibleAppointments.length === 0 ? (
                <EmptyStateCard
                  title="No matching appointments"
                  description="Adjust the name, email, or phone values and search again using the mock data set."
                />
              ) : (
                visibleAppointments.map((appointment) => {
                  const isSelected = appointment.id === selectedAppointmentId;

                  return (
                    <button
                      key={appointment.id}
                      type="button"
                      onClick={() => setSelectedAppointmentId(appointment.id)}
                      className={`w-full rounded-[20px] border p-5 text-left transition ${
                        isSelected
                          ? "border-sky-200 bg-sky-50 shadow-[0_0_0_1px_rgba(56,189,248,0.15)]"
                          : "border-slate-200 bg-white hover:border-slate-300"
                      }`}
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h3 className="text-lg font-semibold text-slate-950">
                            {appointment.patientName}
                          </h3>
                          <p className="mt-1 text-sm text-slate-500">
                            {appointment.email} · {appointment.phone}
                          </p>
                        </div>
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[appointment.status]}`}
                        >
                          {appointment.status}
                        </span>
                      </div>

                      <div className="mt-4 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
                        <p>
                          <span className="font-semibold text-slate-900">
                            Date:
                          </span>{" "}
                          {appointment.appointmentDate}
                        </p>
                        <p>
                          <span className="font-semibold text-slate-900">
                            Time:
                          </span>{" "}
                          {appointment.appointmentTime}
                        </p>
                        <p>
                          <span className="font-semibold text-slate-900">
                            Doctor:
                          </span>{" "}
                          {appointment.doctorName}
                        </p>
                        <p>
                          <span className="font-semibold text-slate-900">
                            Type:
                          </span>{" "}
                          {appointment.appointmentType}
                        </p>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </section>

          <section className="rounded-[24px] border border-slate-100 bg-white p-6 shadow-soft lg:p-8">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-600">
              Appointment Details Section
            </p>
            <h2 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              Selected appointment preview
            </h2>

            {!submittedFilters || !selectedAppointment ? (
              <div className="mt-6">
                <EmptyStateCard
                  title="Details will appear here"
                  description="The selected appointment summary can be reviewed in this panel after a mock search."
                />
              </div>
            ) : (
              <div className="mt-6 space-y-5">
                <div className="rounded-[20px] bg-slate-50 p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                        Appointment ID
                      </p>
                      <p className="mt-2 text-xl font-semibold text-slate-950">
                        {selectedAppointment.id}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[selectedAppointment.status]}`}
                    >
                      {selectedAppointment.status}
                    </span>
                  </div>
                </div>

                <dl className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-[18px] border border-slate-200 p-4">
                    <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Patient
                    </dt>
                    <dd className="mt-2 text-sm font-semibold text-slate-950">
                      {selectedAppointment.patientName}
                    </dd>
                  </div>
                  <div className="rounded-[18px] border border-slate-200 p-4">
                    <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Contact
                    </dt>
                    <dd className="mt-2 text-sm font-semibold text-slate-950">
                      {selectedAppointment.email}
                    </dd>
                  </div>
                  <div className="rounded-[18px] border border-slate-200 p-4">
                    <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Schedule
                    </dt>
                    <dd className="mt-2 text-sm font-semibold text-slate-950">
                      {selectedAppointment.appointmentDate} at{" "}
                      {selectedAppointment.appointmentTime}
                    </dd>
                  </div>
                  <div className="rounded-[18px] border border-slate-200 p-4">
                    <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Doctor
                    </dt>
                    <dd className="mt-2 text-sm font-semibold text-slate-950">
                      {selectedAppointment.doctorName}
                    </dd>
                  </div>
                  <div className="rounded-[18px] border border-slate-200 p-4">
                    <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Phone
                    </dt>
                    <dd className="mt-2 text-sm font-semibold text-slate-950">
                      {selectedAppointment.phone}
                    </dd>
                  </div>
                  <div className="rounded-[18px] border border-slate-200 p-4">
                    <dt className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Visit Type
                    </dt>
                    <dd className="mt-2 text-sm font-semibold text-slate-950">
                      {selectedAppointment.appointmentType}
                    </dd>
                  </div>
                </dl>

                <div className="rounded-[20px] border border-slate-200 bg-white p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Visit Reason
                  </p>
                  <p className="mt-2 text-sm leading-6 text-slate-700">
                    {selectedAppointment.reason}
                  </p>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </section>
  );
}
