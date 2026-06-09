"use client";

import * as React from "react";

import type { FieldErrors, Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { cn } from "@/lib/utils";

import {
  appointmentFormDefaults,
  appointmentFormSchema,
  type AppointmentFormValues,
  appointmentTypeLabels,
} from "@/features/appointments/schema";
import { AppointmentTypeSelector } from "@/features/appointments/components/AppointmentTypeSelector";

type PatientDetailsFormProps = {
  defaultValues?: Partial<AppointmentFormValues>;
  submitLabel?: string;
  onSubmit?: (values: AppointmentFormValues) => void | Promise<void>;
  onAppointmentTypeChange?: (appointmentType: AppointmentFormValues["appointment_type"]) => void;
  isBookingReady?: boolean;
  className?: string;
};

const appointmentFormResolver: Resolver<AppointmentFormValues> = async (
  values,
) => {
  const result = appointmentFormSchema.safeParse(values);

  if (result.success) {
    return {
      values: result.data,
      errors: {},
    };
  }

  const errors: FieldErrors<AppointmentFormValues> = {};

  for (const issue of result.error.issues) {
    const fieldName = issue.path[0] as keyof AppointmentFormValues | undefined;

    if (!fieldName || errors[fieldName]) {
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

function FieldError({ message }: { message?: string }) {
  if (!message) {
    return null;
  }

  return <p className="mt-2 text-sm text-rose-600">{message}</p>;
}

export function PatientDetailsForm({
  defaultValues,
  submitLabel = "Confirm Appointment",
  onSubmit,
  onAppointmentTypeChange,
  isBookingReady = true,
  className,
}: PatientDetailsFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<AppointmentFormValues>({
    resolver: appointmentFormResolver,
    defaultValues: {
      ...appointmentFormDefaults,
      ...defaultValues,
    },
    mode: "onSubmit",
  });

  const selectedAppointmentType = watch("appointment_type");

  React.useEffect(() => {
    onAppointmentTypeChange?.(selectedAppointmentType);
  }, [onAppointmentTypeChange, selectedAppointmentType]);

  const submitHandler = handleSubmit(async (values) => {
    await onSubmit?.(values);
  });

  return (
    <form className={cn("space-y-6", className)} onSubmit={submitHandler}>
      <AppointmentTypeSelector
        value={selectedAppointmentType}
        onChange={(value) =>
          setValue("appointment_type", value, {
            shouldDirty: true,
            shouldValidate: true,
          })
        }
      />
      <FieldError message={errors.appointment_type?.message} />

      <div>
        <label htmlFor="full_name" className="mb-2 block text-sm font-semibold text-slate-900">
          Full Name
        </label>
        <input
          id="full_name"
          type="text"
          autoComplete="name"
          placeholder="Enter your full name"
          {...register("full_name")}
          aria-invalid={Boolean(errors.full_name)}
          className="h-12 w-full rounded-[12px] border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100"
        />
        <FieldError message={errors.full_name?.message} />
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label htmlFor="email" className="mb-2 block text-sm font-semibold text-slate-900">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="Enter your email"
            {...register("email")}
            aria-invalid={Boolean(errors.email)}
            className="h-12 w-full rounded-[12px] border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100"
          />
          <FieldError message={errors.email?.message} />
        </div>

        <div>
          <label htmlFor="phone" className="mb-2 block text-sm font-semibold text-slate-900">
            Phone
          </label>
          <input
            id="phone"
            type="tel"
            autoComplete="tel"
            placeholder="Optional"
            {...register("phone")}
            aria-invalid={Boolean(errors.phone)}
            className="h-12 w-full rounded-[12px] border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100"
          />
          <FieldError message={errors.phone?.message} />
        </div>
      </div>

      <div>
        <label
          htmlFor="health_description"
          className="mb-2 block text-sm font-semibold text-slate-900"
        >
          Brief Health Description
        </label>
        <textarea
          id="health_description"
          rows={4}
          maxLength={500}
          placeholder="Tell us what you'd like the doctor to know..."
          {...register("health_description")}
          aria-invalid={Boolean(errors.health_description)}
          className="w-full rounded-[12px] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100"
        />
        <div className="mt-2 flex items-start justify-between gap-4">
          <FieldError message={errors.health_description?.message} />
          <p className="text-xs leading-5 text-slate-500">
            Optional, up to 500 characters.
          </p>
        </div>
      </div>

      {!isBookingReady ? (
        <p className="rounded-[12px] border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Select a date and time before submitting the form.
        </p>
      ) : null}

      <button
        type="submit"
        disabled={!isBookingReady || isSubmitting}
        className={cn(
          "inline-flex h-14 w-full items-center justify-center rounded-[12px] text-base font-semibold text-white transition",
          !isBookingReady || isSubmitting
            ? "cursor-not-allowed bg-slate-300"
            : "bg-brand-500 hover:bg-brand-600",
        )}
      >
        {isSubmitting ? "Submitting..." : submitLabel}
      </button>

      <p className="text-center text-xs leading-5 text-slate-500">
        Current selection: {appointmentTypeLabels[selectedAppointmentType]}
      </p>
    </form>
  );
}
