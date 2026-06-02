import { DoctorSummaryCard } from "@/features/appointments/components/DoctorSummaryCard";
import { doctors } from "@/features/doctors/mock-doctors";

const weekdays = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
const calendarWeeks = [
  [null, null, 1, 2, 3, 4, 5],
  [6, 7, 8, 9, 10, 11, 12],
  [13, 14, 15, 16, 17, 18, 19],
  [20, 21, 22, 23, 24, 25, 26],
  [27, 28, 29, 30, 31, null, null],
];

const morningSlots = ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM"];
const afternoonSlots = ["02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM"];

export default function AppointmentsPage() {
  const doctor = doctors[0];

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

                <div className="flex items-center gap-5 text-slate-700">
                  <button
                    type="button"
                    className="text-3xl leading-none transition hover:text-slate-950"
                    aria-label="Previous month"
                  >
                    &lsaquo;
                  </button>
                  <span className="text-base font-semibold tracking-[0.14em]">
                    OCTOBER 2024
                  </span>
                  <button
                    type="button"
                    className="text-3xl leading-none transition hover:text-slate-950"
                    aria-label="Next month"
                  >
                    &rsaquo;
                  </button>
                </div>
              </div>

              <div className="rounded-[20px] border border-slate-200 bg-white p-6 shadow-soft">
                <div className="grid grid-cols-7 gap-y-5 text-center text-sm font-semibold text-slate-500">
                  {weekdays.map((weekday) => (
                    <div key={weekday}>{weekday}</div>
                  ))}
                </div>

                <div className="mt-4 space-y-4">
                  {calendarWeeks.map((week, weekIndex) => (
                    <div key={weekIndex} className="grid grid-cols-7 gap-3">
                      {week.map((day, dayIndex) => {
                        const isSelected = day === 24;
                        const isMuted = day !== null && day < 20;

                        return (
                          <button
                            key={`${weekIndex}-${dayIndex}`}
                            type="button"
                            className={[
                              "flex h-12 items-center justify-center rounded-[14px] text-base font-medium transition",
                              day === null
                                ? "pointer-events-none bg-transparent text-transparent"
                                : isSelected
                                  ? "bg-brand-500 text-white shadow-[0_12px_24px_rgba(6,182,212,0.32)]"
                                  : isMuted
                                    ? "text-slate-300"
                                    : "text-slate-800 hover:bg-slate-50",
                            ].join(" ")}
                            aria-pressed={isSelected}
                          >
                            {day ?? ""}
                          </button>
                        );
                      })}
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="space-y-8">
              <div>
                <h3 className="mb-4 text-lg font-semibold tracking-[-0.03em] text-slate-600">
                  MORNING
                </h3>
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {morningSlots.map((slot) => {
                    const isSelected = slot === "10:30 AM";

                    return (
                      <button
                        key={slot}
                        type="button"
                        className={[
                          "h-12 rounded-[12px] border px-4 text-base font-semibold transition",
                          isSelected
                            ? "border-brand-500 bg-brand-500 text-white shadow-[0_10px_22px_rgba(6,182,212,0.24)]"
                            : "border-slate-200 bg-white text-slate-900 hover:border-brand-100 hover:bg-brand-50/60",
                        ].join(" ")}
                        aria-pressed={isSelected}
                      >
                        {slot}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <h3 className="mb-4 text-lg font-semibold tracking-[-0.03em] text-slate-600">
                  AFTERNOON
                </h3>
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {afternoonSlots.map((slot) => (
                    <button
                      key={slot}
                      type="button"
                      className="h-12 rounded-[12px] border border-slate-200 bg-white px-4 text-base font-semibold text-slate-900 transition hover:border-brand-100 hover:bg-brand-50/60"
                    >
                      {slot}
                    </button>
                  ))}
                </div>
              </div>
            </section>
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

              <div className="mt-8">
                <p className="text-sm font-semibold text-slate-900">
                  Appointment Type
                </p>
                <div className="mt-3 grid grid-cols-2 rounded-[16px] bg-slate-100 p-1">
                  <button
                    type="button"
                    className="flex items-center justify-center gap-2 rounded-[12px] bg-white py-3 text-sm font-semibold text-brand-500 shadow-[0_8px_18px_rgba(15,23,42,0.08)]"
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
                      <path d="M14 9V5a3 3 0 0 0-3-3H6a3 3 0 0 0-3 3v14a3 3 0 0 0 3 3h5a3 3 0 0 0 3-3v-4" />
                      <path d="M21 12h-6" />
                      <path d="M18 9l3 3-3 3" />
                    </svg>
                    In-Person
                  </button>
                  <button
                    type="button"
                    className="flex items-center justify-center gap-2 rounded-[12px] py-3 text-sm font-semibold text-slate-500"
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
                      <rect x="3" y="6" width="14" height="12" rx="2" />
                      <path d="M17 10l4-2v8l-4-2" />
                    </svg>
                    Telemedicine
                  </button>
                </div>
              </div>

              <div className="mt-6 space-y-5">
                <div>
                  <label
                    htmlFor="fullName"
                    className="mb-2 block text-sm font-semibold text-slate-900"
                  >
                    Full Name
                  </label>
                  <input
                    id="fullName"
                    type="text"
                    placeholder="John Doe"
                    className="h-12 w-full rounded-[12px] border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100"
                  />
                </div>

                <div>
                  <label
                    htmlFor="email"
                    className="mb-2 block text-sm font-semibold text-slate-900"
                  >
                    Email Address
                  </label>
                  <input
                    id="email"
                    type="email"
                    placeholder="john.doe@example.com"
                    className="h-12 w-full rounded-[12px] border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100"
                  />
                </div>

                <div>
                  <label
                    htmlFor="description"
                    className="mb-2 block text-sm font-semibold text-slate-900"
                  >
                    Brief Health Description
                  </label>
                  <textarea
                    id="description"
                    rows={4}
                    placeholder="e.g., Shortness of breath, regular follow-up for high blood pressure..."
                    className="w-full rounded-[12px] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-300 focus:ring-2 focus:ring-brand-100"
                  />
                  <p className="mt-2 text-xs italic leading-5 text-slate-500">
                    This information helps Dr. Sarah Jenkins prepare for your
                    visit.
                  </p>
                </div>
              </div>

              <div className="mt-8 space-y-3">
                <button
                  type="button"
                  className="inline-flex h-14 w-full items-center justify-center rounded-[12px] bg-brand-500 text-base font-semibold text-white transition hover:bg-brand-600"
                >
                  Confirm Appointment
                </button>
                <button
                  type="button"
                  className="inline-flex h-12 w-full items-center justify-center rounded-[12px] border border-slate-200 bg-white text-sm font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
                >
                  Cancel / Back
                </button>
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
