import Link from "next/link";

export default function HomePage() {
  return (
    <section className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
      <div className="rounded-3xl border border-brand-100 bg-white p-8 shadow-soft">
        <span className="inline-flex rounded-full bg-brand-50 px-3 py-1 text-sm font-medium text-brand-900">
          Project foundation
        </span>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-slate-950">
          Book a doctor with a clear and simple flow.
        </h1>
        <p className="mt-4 max-w-2xl text-base text-slate-600">
          This foundation sets up the shared layout, routes, styles, state, and
          API client for the manual booking experience.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/doctors"
            className="rounded-full bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700"
          >
            View doctors
          </Link>
          <Link
            href="/appointments"
            className="rounded-full border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-cyan-200 hover:text-cyan-700"
          >
            Appointment page
          </Link>
        </div>
      </div>

      <aside className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <h2 className="text-lg font-semibold text-slate-950">
          Foundation status
        </h2>
        <ul className="mt-5 space-y-3 text-sm text-slate-600">
          <li>Shared header and footer are active.</li>
          <li>Base routes are ready for feature expansion.</li>
          <li>Zustand booking store is scaffolded.</li>
          <li>API client is prepared without live integration.</li>
        </ul>
      </aside>
    </section>
  );
}
