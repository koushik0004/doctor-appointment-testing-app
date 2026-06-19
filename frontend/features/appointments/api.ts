import { format, parseISO } from "date-fns";

import { apiClient, type ApiRequestOptions } from "@/lib/api-client";
import {
  mapDoctorApiRecord,
} from "@/features/doctors/api";
import type { DoctorApiRecord } from "@/features/doctors/types";

import type {
  AppointmentConfirmationResponse,
  AppointmentCreatePayload,
  AppointmentCreateResponse,
  AvailabilitySlot,
  DoctorAvailability,
} from "@/features/appointments/types";

type AvailabilitySlotApiRecord = {
  id: number;
  available_date: string;
  start_time: string;
  end_time: string;
  appointment_type: AvailabilitySlot["appointmentType"];
  is_booked: boolean;
};

type DoctorAvailabilityApiResponse = {
  doctor_id: number;
  doctor: DoctorApiRecord;
  available_dates: string[];
  morning_slots: AvailabilitySlotApiRecord[];
  afternoon_slots: AvailabilitySlotApiRecord[];
};

type DoctorAvailabilityQuery = {
  dateFrom?: Date;
  dateTo?: Date;
  appointmentType?: AvailabilitySlot["appointmentType"];
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
  appointment_type: AvailabilitySlot["appointmentType"];
  health_description: string | null;
};

function mapAvailabilitySlot(record: AvailabilitySlotApiRecord): AvailabilitySlot {
  return {
    id: record.id,
    availableDate: record.available_date,
    startTime: record.start_time,
    endTime: record.end_time,
    appointmentType: record.appointment_type,
    isBooked: record.is_booked,
  };
}

function mapDoctorAvailability(
  response: DoctorAvailabilityApiResponse,
): DoctorAvailability {
  return {
    doctor: mapDoctorApiRecord(response.doctor),
    doctorId: response.doctor_id,
    availableDates: response.available_dates.map((entry) => parseISO(entry)),
    morningSlots: response.morning_slots.map(mapAvailabilitySlot),
    afternoonSlots: response.afternoon_slots.map(mapAvailabilitySlot),
  };
}

export async function getDoctorAvailability(
  doctorId: string | number,
  query?: DoctorAvailabilityQuery,
  options?: ApiRequestOptions,
): Promise<DoctorAvailability> {
  const params = new URLSearchParams();
  if (query?.dateFrom) {
    params.set("date_from", format(query.dateFrom, "yyyy-MM-dd"));
  }
  if (query?.dateTo) {
    params.set("date_to", format(query.dateTo, "yyyy-MM-dd"));
  }
  if (query?.appointmentType) {
    params.set("appointment_type", query.appointmentType);
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
