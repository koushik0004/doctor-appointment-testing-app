"use client";

import { useRouter } from "next/navigation";

import { AiWidgetRoot } from "@/lib/ai-widget/components";
import { createNoopAiWidgetAdapter } from "@/lib/ai-widget/adapters";
import { createApiAiWidgetService } from "@/lib/ai-widget/services";
import type {
  AiWidgetChatRequest,
  AiWidgetChatResponse,
  AiWidgetMessage,
  AiWidgetService,
  AiWidgetWorkflowResult,
} from "@/lib/ai-widget/types";
import { useBookingStore } from "@/stores/booking-store";

function getWorkflowMetadata(message: AiWidgetMessage): AiWidgetWorkflowResult | undefined {
  const workflow = message.metadata?.workflow;
  if (!workflow || typeof workflow !== "object") {
    return undefined;
  }

  return workflow as AiWidgetWorkflowResult;
}

export function GlobalAiWidget() {
  const router = useRouter();
  const setSelectedDoctorId = useBookingStore((state) => state.setSelectedDoctorId);
  const setSelectedDate = useBookingStore((state) => state.setSelectedDate);
  const setSelectedTime = useBookingStore((state) => state.setSelectedTime);
  const setAppointmentType = useBookingStore((state) => state.setAppointmentType);
  const setPatientDetails = useBookingStore((state) => state.setPatientDetails);
  const setAppointmentId = useBookingStore((state) => state.setAppointmentId);
  const setConfirmationCode = useBookingStore((state) => state.setConfirmationCode);
  const apiService = createApiAiWidgetService();

  const service: AiWidgetService = {
    async sendMessage(request: AiWidgetChatRequest): Promise<AiWidgetChatResponse> {
      const response = await apiService.sendMessage(request);
      const workflow = getWorkflowMetadata(response.reply);

      if (
        workflow?.workflow_type === "BOOK_APPOINTMENT" &&
        workflow.status === "COMPLETED" &&
        workflow.appointment &&
        workflow.draft.doctor_id
      ) {
        setSelectedDoctorId(String(workflow.draft.doctor_id));
        setSelectedDate(workflow.appointment.appointment_date);
        setSelectedTime(workflow.appointment.start_time);
        setAppointmentType(
          workflow.appointment.appointment_type === "TELEMEDICINE"
            ? "TELEMEDICINE"
            : "IN_PERSON",
        );
        setPatientDetails({
          full_name: workflow.appointment.patient_name,
          email: workflow.draft.patient_email ?? "",
          phone: workflow.draft.patient_phone ?? "",
          health_description: workflow.draft.health_description ?? "",
        });
        setAppointmentId(workflow.appointment.appointment_id);
        setConfirmationCode(workflow.appointment.confirmation_code);
        router.push(
          `/appointments/confirmation?appointmentId=${encodeURIComponent(String(workflow.appointment.appointment_id))}&doctorId=${encodeURIComponent(String(workflow.draft.doctor_id))}`,
        );
      }

      return response;
    },
  };

  return (
    <AiWidgetRoot
      adapter={createNoopAiWidgetAdapter()}
      service={service}
    />
  );
}
