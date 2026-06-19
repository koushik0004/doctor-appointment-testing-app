import { format, parseISO } from "date-fns";

import { apiClient, type ApiRequestOptions } from "@/lib/api-client";
import type {
  AppointmentConfirmationResponse,
  AppointmentCreatePayload,
  AppointmentCreateResponse,
  AppointmentSearchQuery,
  AppointmentSearchResponse,
  AvailabilitySlot,
  AppointmentType,
  DoctorAvailability,
} from "@/features/appointments/types";

type AvailabilitySlotApiRecord = {
  id: number;
  start_time: string;
  end_time: string;
  is_booked: boolean;
};

type DoctorAvailabilityApiResponse = {
  date: string;
  doctor_id: number;
  available_slots: AvailabilitySlotApiRecord[];
};

type DoctorAvailabilityQuery = {
  date: Date;
};

type AppointmentCreateApiResponse = {
  id: number;
  confirmation_code: string;
  status: string;
  doctor_id: number;
  patient_id: number;
  appointment_date: string;
  start_time: string;
  end_time: string;
};

type AppointmentConfirmationApiResponse = {
  id: number;
  confirmation_code: string;
  status: string;
  doctor: {
    name: string;
    specialty: string;
    clinic_name: string;
    location: string;
  };
  patient: {
    full_name: string;
    email: string;
    phone: string | null;
  };
  appointment_date: string;
  start_time: string;
  end_time: string;
  appointment_type: AppointmentType;
  health_description: string | null;
};

function mapAvailabilitySlot(record: AvailabilitySlotApiRecord): AvailabilitySlot {
  return {
    id: record.id,
    startTime: record.start_time,
    endTime: record.end_time,
    isBooked: record.is_booked,
  };
}

function mapDoctorAvailability(
  response: DoctorAvailabilityApiResponse,
): DoctorAvailability {
  const availableSlots = response.available_slots.map(mapAvailabilitySlot);
  return {
    doctorId: response.doctor_id,
    date: parseISO(response.date),
    availableSlots,
    morningSlots: availableSlots.filter(
      (slot) => Number(slot.startTime.slice(0, 2)) < 12,
    ),
    afternoonSlots: availableSlots.filter(
      (slot) => Number(slot.startTime.slice(0, 2)) >= 12,
    ),
  };
}

export async function getDoctorAvailability(
  doctorId: string | number,
  query?: DoctorAvailabilityQuery,
  options?: ApiRequestOptions,
): Promise<DoctorAvailability> {
  const params = new URLSearchParams();
  if (query?.date) {
    params.set("date", format(query.date, "yyyy-MM-dd"));
  }

  const response = await apiClient.get<DoctorAvailabilityApiResponse>(
    `/doctors/${doctorId}/availability${params.toString() ? `?${params.toString()}` : ""}`,
    options,
  );

  return mapDoctorAvailability(response);
}

export async function createAppointment(
  payload: AppointmentCreatePayload,
  options?: ApiRequestOptions,
): Promise<AppointmentCreateResponse> {
  const response = await apiClient.post<AppointmentCreateApiResponse>(
    "/appointments",
    payload,
    options,
  );

  return response;
}

export async function getAppointmentConfirmation(
  appointmentId: string | number,
  options?: ApiRequestOptions,
): Promise<AppointmentConfirmationResponse> {
  const response = await apiClient.get<AppointmentConfirmationApiResponse>(
    `/appointments/${appointmentId}`,
    options,
  );

  return response;
}

export async function searchAppointments(
  query: AppointmentSearchQuery,
  options?: ApiRequestOptions,
): Promise<AppointmentSearchResponse> {
  const params = new URLSearchParams();

  if (query.name?.trim()) {
    params.set("name", query.name.trim());
  }

  if (query.email?.trim()) {
    params.set("email", query.email.trim());
  }

  if (query.phone?.trim()) {
    params.set("phone", query.phone.trim());
  }

  const response = await apiClient.get<AppointmentSearchResponse>(
    `/appointments/search${params.toString() ? `?${params.toString()}` : ""}`,
    options,
  );

  return response;
}
