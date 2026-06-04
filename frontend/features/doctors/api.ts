import { apiClient, type ApiRequestOptions } from "@/lib/api-client";

import {
  type AppointmentType,
  type Doctor,
  type DoctorApiRecord,
  type DoctorListApiResponse,
} from "@/features/doctors/types";

type DoctorListParams = {
  specialty?: string;
  appointmentType?: AppointmentType | "ALL";
};

function mapDoctorApiRecord(record: DoctorApiRecord): Doctor {
  return {
    id: String(record.id),
    name: record.name,
    specialty: record.specialty,
    rating: record.rating,
    reviewCount: record.review_count,
    description: record.description,
    languages: record.languages,
    clinic: record.clinic_name,
    location: record.location,
    feeRange: {
      min: record.consultation_fee_min,
      max: record.consultation_fee_max,
    },
    nextAvailable: record.next_available_slot,
    appointmentTypes: record.appointment_types,
    consultationFee: record.consultation_fee_min,
    durationMinutes: 30,
    avatar: {
      imageSrc: record.image_url,
      imageAlt: `Portrait of ${record.name}`,
    },
  };
}

export async function listDoctors(
  params: DoctorListParams = {},
  options?: ApiRequestOptions,
): Promise<{ items: Doctor[]; total: number }> {
  const query = new URLSearchParams();

  if (params.specialty) {
    query.set("specialty", params.specialty);
  }

  if (params.appointmentType && params.appointmentType !== "ALL") {
    query.set("appointment_type", params.appointmentType);
  }

  const response = await apiClient.get<DoctorListApiResponse>(
    `/doctors${query.toString() ? `?${query.toString()}` : ""}`,
    options,
  );

  return {
    items: response.items.map(mapDoctorApiRecord),
    total: response.total,
  };
}

export async function getDoctor(
  doctorId: string | number,
  options?: ApiRequestOptions,
): Promise<Doctor> {
  const response = await apiClient.get<DoctorApiRecord>(
    `/doctors/${doctorId}`,
    options,
  );

  return mapDoctorApiRecord(response);
}
