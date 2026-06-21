"use client";

import type { FormEvent } from "react";

import { cn } from "@/lib/utils";

type MessageComposerProps = {
  value: string;
  placeholder: string;
  disabled?: boolean;
  isSending?: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export function MessageComposer({
  value,
  placeholder,
  disabled = false,
  isSending = false,
  onChange,
  onSubmit,
}: MessageComposerProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 flex items-end gap-3 border-t border-slate-100 pt-4">
      <label className="sr-only" htmlFor="ai-widget-message">
        Chat message
      </label>
      <textarea
        id="ai-widget-message"
        rows={2}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        className={cn(
          "min-h-14 flex-1 resize-none rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-slate-400",
          disabled && "cursor-not-allowed bg-slate-50 text-slate-400",
        )}
      />
      <button
        type="submit"
        disabled={disabled}
        className="inline-flex h-12 items-center justify-center rounded-full bg-slate-950 px-5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
      >
        {isSending ? "Sending..." : "Send"}
      </button>
    </form>
  );
}
