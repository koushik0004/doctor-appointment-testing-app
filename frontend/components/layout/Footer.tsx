export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto w-full max-w-[1600px] px-4 py-16 sm:px-6 lg:px-8 xl:px-10">
        <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr_0.85fr_0.7fr]">
          <div className="max-w-xs">
            <div className="flex items-center gap-3 text-[2rem] font-semibold tracking-[-0.05em] text-sky-400">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-sky-50 text-sky-400 ring-1 ring-sky-100">
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
            <div className="mt-5 flex items-center gap-6 text-slate-500">
              <span className="text-lg">f</span>
              <span className="text-lg">t</span>
              <span className="text-lg">ig</span>
            </div>
          </div>
        </div>

        <div className="mt-14 flex flex-col gap-3 border-t border-slate-200 pt-6 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
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
