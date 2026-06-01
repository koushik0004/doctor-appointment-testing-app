import Link from "next/link";

const navigation = [
  { href: "/doctors", label: "Find Doctors" },
  { href: "#", label: "Services" },
];

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-[1320px] items-center justify-between px-4 py-5 sm:px-6 lg:px-8">
        <nav aria-label="Primary navigation">
          <ul className="flex items-center gap-2 sm:gap-4">
            {navigation.map((item) => (
              <li key={item.label}>
                <Link
                  href={item.href}
                  className="rounded-full px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 hover:text-slate-950"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <Link
          href="/"
          className="flex items-center gap-3 text-xl font-semibold tracking-tight text-cyan-500"
        >
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
        </Link>

        <div className="flex items-center gap-3">
          <Link
            href="#"
            className="rounded-full px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          >
            Sign In
          </Link>
          <Link
            href="/doctors"
            className="rounded-2xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-600"
          >
            Join CareNow
          </Link>
        </div>
      </div>
    </header>
  );
}
