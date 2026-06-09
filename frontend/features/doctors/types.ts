export type AppointmentType = "IN_PERSON" | "TELEMEDICINE";

export const specialtyOptions = [
  "All specialties",
  "General Practice",
  "Cardiology",
  "Pediatrics",
  "Dermatology",
  "Internal Medicine",
] as const;

export const appointmentTypeOptions = [
  { label: "All types", value: "ALL" },
  { label: "In-person", value: "IN_PERSON" },
  { label: "Telemedicine", value: "TELEMEDICINE" },
] as const;

export type Doctor = {
  id: string;
  backendId: number;
  name: string;
  specialty: string;
  rating: number;
  reviewCount: number;
  description: string;
  languages: string[];
  clinic: string;
  location: string;
  feeRange: {
    min: number;
    max: number;
  };
  nextAvailable: string;
  appointmentTypes: AppointmentType[];
  consultationFee: number;
  durationMinutes: number;
  avatar: {
    imageSrc: string;
    imageAlt: string;
  };
};

export type DoctorApiRecord = {
  id: number;
  name: string;
  specialty: string;
  rating: number;
  review_count: number;
  clinic_name: string;
  location: string;
  consultation_fee_min: number;
  consultation_fee_max: number;
  next_available_slot: string;
  appointment_types: AppointmentType[];
  languages: string[];
  description: string;
  image_url: string;
};

export type DoctorListApiResponse = {
  items: DoctorApiRecord[];
  total: number;
};

export type DoctorSortOption = "TOP_RATED" | "EARLIEST_AVAILABILITY";
