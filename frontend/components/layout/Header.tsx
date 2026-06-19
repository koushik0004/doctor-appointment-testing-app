import Link from "next/link";

const navigation = [
  { href: "/doctors", label: "Find Doctors" },
  { href: "/appointments/search", label: "Appointment Search" },
  { href: "#", label: "Services" },
];

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto grid w-full max-w-[1600px] grid-cols-[1fr_auto_1fr] items-center px-4 py-5 sm:px-6 lg:px-8 xl:px-10">
        <nav aria-label="Primary navigation">
          <ul className="flex items-center gap-5">
            {navigation.map((item) => (
              <li key={item.label}>
                <Link
                  href={item.href}
                  className="px-2 py-2 text-sm font-semibold text-slate-700 transition hover:text-slate-950"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <Link
          href="/"
          className="flex items-center justify-center gap-3 text-[2rem] font-semibold tracking-[-0.05em] text-sky-400"
        >
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
        </Link>

        <div className="flex items-center justify-end gap-3">
          <Link
            href="#"
            className="px-4 py-2 text-sm font-semibold text-slate-700 transition hover:text-slate-950"
          >
            Sign In
          </Link>
          <Link
            href="/doctors"
            className="rounded-[12px] bg-sky-400 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-500"
          >
            Join CareNow
          </Link>
        </div>
      </div>
    </header>
  );
}
