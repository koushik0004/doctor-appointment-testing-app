export function Footer() {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-white">
      <div className="mx-auto w-full max-w-[1320px] px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr_0.8fr_0.8fr]">
          <div className="max-w-xs">
            <div className="flex items-center gap-3 text-2xl font-semibold tracking-tight text-cyan-500">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-50 text-cyan-500 ring-1 ring-cyan-100">
                <svg
                  aria-hidden="true"
                  viewBox="0 0 24 24"
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M3 12h4l2-5 4 10 2-5h6" />
                </svg>
              </span>
              CareNow
            </div>
            <p className="mt-5 text-sm leading-7 text-slate-500">
              Making healthcare accessible, one appointment at a time. Quality
              care from vetted professionals.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-slate-900">Patient Care</h2>
            <ul className="mt-5 space-y-3 text-sm text-slate-500">
              <li>How it Works</li>
              <li>Search Doctors</li>
              <li>Safety Guidelines</li>
            </ul>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-slate-900">Support</h2>
            <ul className="mt-5 space-y-3 text-sm text-slate-500">
              <li>Help Center</li>
              <li>Contact Us</li>
              <li>Privacy Policy</li>
            </ul>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-slate-900">Connect</h2>
            <div className="mt-5 flex items-center gap-4 text-slate-500">
              <span className="rounded-full border border-slate-200 px-3 py-2 text-sm">
                f
              </span>
              <span className="rounded-full border border-slate-200 px-3 py-2 text-sm">
                t
              </span>
              <span className="rounded-full border border-slate-200 px-3 py-2 text-sm">
                ig
              </span>
            </div>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-slate-200 pt-6 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
          <p>© 2024 CareNow Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <p>Terms of Service</p>
            <p>Cookie Policy</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
