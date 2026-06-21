"use client";

import type { AiWidgetMessage, AiWidgetMessageContent } from "@/lib/ai-widget/types";
import { AppointmentHelpMessage } from "@/lib/ai-widget/components/AppointmentHelpMessage";
import { AvailabilityMessage } from "@/lib/ai-widget/components/AvailabilityMessage";
import { DoctorCardMessage } from "@/lib/ai-widget/components/DoctorCardMessage";
import { cn } from "@/lib/utils";

type MessageContentRendererProps = {
  message: AiWidgetMessage;
  onBookAppointment?: (doctorId: number) => void;
};

function TextContent({ text }: { text: string }) {
  return <p className="whitespace-pre-wrap leading-6">{text}</p>;
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
    </article>
  );
}
