"use client";

import type { AiWidgetMessage, AiWidgetMessageContent } from "@/lib/ai-widget/types";
import type { AiWidgetChatKnowledgeSource } from "@/lib/ai-widget/types";
import { AppointmentHelpMessage } from "@/lib/ai-widget/components/AppointmentHelpMessage";
import { AvailabilityMessage } from "@/lib/ai-widget/components/AvailabilityMessage";
import { DoctorCardMessage } from "@/lib/ai-widget/components/DoctorCardMessage";
import { SearchFilterSummary } from "@/lib/ai-widget/components/SearchFilterSummary";
import { cn } from "@/lib/utils";

type MessageContentRendererProps = {
  message: AiWidgetMessage;
  onBookAppointment?: (doctorId: number) => void;
};

function TextContent({ text }: { text: string }) {
  return <p className="whitespace-pre-wrap leading-6">{text}</p>;
}

function KnowledgeSourceFooter({
  source,
}: {
  source: AiWidgetChatKnowledgeSource;
}) {
  const matchedTerms = source.matched_terms.filter(Boolean);

  return (
    <div className="mt-3 border-t border-slate-200 pt-3 text-[0.72rem] leading-5 text-slate-500">
      <p className="font-semibold uppercase tracking-[0.16em] text-slate-400">
        Knowledge source
      </p>
      <p className="mt-1 break-words text-slate-600">{source.title}</p>
      <p className="mt-0.5 break-words text-slate-500">{source.source_path}</p>
      {matchedTerms.length > 0 ? (
        <p className="mt-1 text-slate-500">
          Matched terms: {matchedTerms.join(", ")}
        </p>
      ) : null}
    </div>
  );
}

function DoctorListContent({
  content,
  onBookAppointment,
}: {
  content: Extract<AiWidgetMessageContent, { type: "doctor_list" }>;
  onBookAppointment?: (doctorId: number) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <p className="text-sm font-semibold text-slate-950">{content.title}</p>
        <p className="text-sm leading-6 text-slate-600">{content.summary}</p>
      </div>

      {content.searchSummary ? (
        <SearchFilterSummary
          countLabel={content.searchSummary.countLabel}
          filters={content.searchSummary.filters}
        />
      ) : null}

      <div className="space-y-3">
        {content.doctors.map((doctor) => (
          <DoctorCardMessage
            key={doctor.doctorId}
            doctor={doctor}
            onBookAppointment={onBookAppointment}
          />
        ))}
      </div>
    </div>
  );
}

function AvailabilityContent({
  content,
  onBookAppointment,
}: {
  content: Extract<AiWidgetMessageContent, { type: "availability" }>;
  onBookAppointment?: (doctorId: number) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <p className="text-sm font-semibold text-slate-950">{content.title}</p>
        <p className="text-sm leading-6 text-slate-600">{content.summary}</p>
      </div>

      {content.searchSummary ? (
        <SearchFilterSummary
          countLabel={content.searchSummary.countLabel}
          filters={content.searchSummary.filters}
        />
      ) : null}

      <div className="space-y-3">
        {content.slots.map((slot) => (
          <AvailabilityMessage
            key={`${slot.doctorId}-${slot.availableDate}-${slot.availableTime}`}
            slot={slot}
            onBookAppointment={onBookAppointment}
          />
        ))}
      </div>
    </div>
  );
}

export function MessageContentRenderer({
  message,
  onBookAppointment,
}: MessageContentRendererProps) {
  const isUser = message.role === "user";
  const assistantShellClasses = cn(
    "max-w-[85%] rounded-3xl px-4 py-3 text-sm leading-6 shadow-sm",
    "bg-slate-100 text-slate-700",
  );
  const userShellClasses = cn(
    "max-w-[85%] rounded-3xl px-4 py-3 text-sm leading-6 shadow-sm",
    "bg-slate-950 text-white",
  );

  if (message.content.type === "doctor_list") {
    return (
      <article className={cn(assistantShellClasses, "max-w-[92%]")}>
        <DoctorListContent
          content={message.content}
          onBookAppointment={onBookAppointment}
        />
      </article>
    );
  }

  if (message.content.type === "availability") {
    return (
      <article className={cn(assistantShellClasses, "max-w-[92%]")}>
        <AvailabilityContent
          content={message.content}
          onBookAppointment={onBookAppointment}
        />
      </article>
    );
  }

  if (message.content.type === "appointment_help") {
    return <AppointmentHelpMessage content={message.content} />;
  }

  return (
    <article className={isUser ? userShellClasses : assistantShellClasses}>
      <TextContent text={message.content.text} />
      {!isUser && message.metadata?.knowledge_source ? (
        <KnowledgeSourceFooter source={message.metadata.knowledge_source} />
      ) : null}
    </article>
  );
}
