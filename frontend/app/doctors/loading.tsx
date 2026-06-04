export default function DoctorsLoading() {
  return (
    <section className="-mx-4 bg-white sm:-mx-6 lg:-mx-8 xl:-mx-10">
      <div className="grid min-h-[calc(100vh-220px)] gap-0 lg:grid-cols-[280px_minmax(0,1fr)_340px]">
        <aside className="border-r border-slate-200 bg-slate-50 px-6 py-8">
          <div className="h-4 w-20 rounded-full bg-slate-200/80" />
          <div className="mt-8 space-y-4">
            <div className="h-3 w-24 rounded-full bg-slate-200/80" />
            <div className="space-y-2">
              <div className="h-10 rounded-xl bg-slate-200/80" />
              <div className="h-10 rounded-xl bg-slate-200/80" />
              <div className="h-10 rounded-xl bg-slate-200/80" />
            </div>
          </div>
        </aside>

        <div className="min-w-0 px-6 py-8 sm:px-8 lg:px-10 xl:px-12">
          <div className="h-12 w-72 rounded-full bg-slate-200/80" />
          <div className="mt-4 h-4 w-96 rounded-full bg-slate-200/80" />
          <div className="mt-10 space-y-5">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={`loading-card-${index}`} className="h-40 rounded-[20px] bg-slate-100" />
            ))}
          </div>
        </div>

        <div className="border-l border-slate-200 px-6 py-8 xl:px-7">
          <div className="h-56 rounded-[16px] bg-slate-100" />
        </div>
      </div>
    </section>
  );
}
