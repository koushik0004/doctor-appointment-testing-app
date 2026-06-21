"use client";

import { cn } from "@/lib/utils";

type ChatLauncherProps = {
  isOpen: boolean;
  label: string;
  onClick: () => void;
  className?: string;
};

export function ChatLauncher({
  isOpen,
  label,
  onClick,
  className,
}: ChatLauncherProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-expanded={isOpen}
      aria-label={label}
      className={cn(
        "inline-flex h-14 items-center gap-3 rounded-full bg-slate-950 px-5 text-sm font-semibold text-white shadow-lg transition hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2",
        className,
      )}
    >
      <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white/10">
        AI
      </span>
      <span>{label}</span>
    </button>
  );
}
