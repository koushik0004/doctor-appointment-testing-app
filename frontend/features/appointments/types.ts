import type { Doctor } from "@/features/doctors/types";

export type AppointmentType = "IN_PERSON" | "TELEMEDICINE";

export type AvailabilitySlot = {
  id: number;
  startTime: string;
  endTime: string;
  isBooked: boolean;
};

export type BookingPatientDetails = {
  full_name: string;
  email: string;
  phone?: string;
  health_description?: string;
};

export type DoctorAvailability = {
  doctorId: number;
  date: Date;
  availableSlots: AvailabilitySlot[];
  morningSlots: AvailabilitySlot[];
  afternoonSlots: AvailabilitySlot[];
};

export type AppointmentPatientInput = {
  full_name: string;
  email: string;
  phone?: string | null;
};

export type AppointmentCreatePayload = {
  doctor_id: number;
  appointment_date: string;
  start_time: string;
  appointment_type: AppointmentType;
  patient: AppointmentPatientInput;
  health_description?: string | null;
};

export type AppointmentCreateResponse = {
  id: number;
  confirmation_code: string;
  status: string;
  doctor_id: number;
  patient_id: number;
  appointment_date: string;
  start_time: string;
  end_time: string;
};

export type AppointmentDoctorSummary = {
  name: string;
  specialty: string;
  clinic_name: string;
  location: string;
};

export type AppointmentPatientSummary = {
  full_name: string;
  email: string;
  phone: string | null;
};

export type AppointmentConfirmationResponse = {
  id: number;
  confirmation_code: string;
  status: string;
  doctor: AppointmentDoctorSummary;
  patient: AppointmentPatientSummary;
  appointment_date: string;
  start_time: string;
  end_time: string;
  appointment_type: AppointmentType;
  health_description: string | null;
};

export type AppointmentStatus = "PENDING" | "CONFIRMED" | "CANCELLED";

export type AppointmentSearchStatus = "booked" | "completed" | "cancelled";

export type AppointmentSearchResult = {
  appointment_id: number;
  patient_name: string;
  patient_email: string;
  patient_phone: string | null;
  doctor_name: string;
  doctor_specialty: string;
  appointment_date: string;
  appointment_time: string;
  appointment_type: AppointmentType;
  status: AppointmentSearchStatus;
};

export type AppointmentSearchResponse = {
  count: number;
  appointments: AppointmentSearchResult[];
};

export type AppointmentDetailsResponse = {
  appointment_id: number;
  doctor: AppointmentDoctorSummary;
  patient: AppointmentPatientSummary;
  appointment_date: string;
  appointment_time: string;
  appointment_type: AppointmentType;
  status: AppointmentStatus;
  created_at: string;
};

export type RecommendationReason = "same_specialty" | "related_specialty";

export type RecommendedDoctor = {
  doctor_id: number;
  doctor_name: string;
  specialty: string;
  rating: number;
  review_count: number;
  next_available_date: string;
  next_available_slot: string;
  profile_image: string;
  clinic_name: string;
  recommendation_reason: RecommendationReason;
};

export type RecommendedDoctorsResponse = {
  appointment_id: number;
  specialty: string;
  recommended_doctors: RecommendedDoctor[];
};

export type AppointmentSearchQuery = {
  name?: string;
  email?: string;
  phone?: string;
};
