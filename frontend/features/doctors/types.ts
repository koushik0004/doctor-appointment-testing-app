export type AppointmentType = "IN_PERSON" | "TELEMEDICINE";

export type Doctor = {
  id: string;
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

export type DoctorSortOption = "TOP_RATED" | "EARLIEST_AVAILABILITY";
