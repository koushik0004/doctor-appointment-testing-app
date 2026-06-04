"use client";

import { useEffect } from "react";

type DoctorsErrorProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function DoctorsError({ error, reset }: DoctorsErrorProps) {
  useEffect(() => {
    console.error("Doctors route error", error);
  }, [error]);

  return (
    <section className="mx-auto flex min-h-[calc(100vh-220px)] max-w-3xl items-center justify-center px-4 py-16">
      <div className="w-full rounded-[24px] border border-rose-200 bg-rose-50 px-6 py-8 text-center sm:px-10">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-rose-600">
          Something went wrong
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-rose-900">
          The doctor list could not load
        </h1>
        <p className="mt-4 text-sm leading-6 text-rose-700">
          The doctors route hit an unexpected error. Retry to reload the live API response.
        </p>
        <button
          type="button"
          onClick={reset}
          className="mt-6 rounded-[12px] bg-rose-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-rose-700"
        >
          Retry
        </button>
      </div>
    </section>
  );
}
