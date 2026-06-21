"use client";

import { aiWidgetClassNames } from "@/lib/ai-widget/styles";
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
      title={label}
      className={cn(
        aiWidgetClassNames.launcher,
        className,
      )}
    >
      <span className="pointer-events-none absolute inset-0 rounded-full bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.36),transparent_55%)]" />
      <span className="relative inline-flex h-10 w-10 items-center justify-center rounded-full bg-white/14 ring-1 ring-white/20">
        <span className="absolute h-3 w-3 rounded-full bg-cyan-200 blur-[5px]" />
        <span className="text-xs font-bold tracking-[0.28em] text-white">AI</span>
      </span>
      <span className="relative hidden sm:inline">{label}</span>
      <span className="sr-only sm:hidden">{label}</span>
    </button>
  );
}
