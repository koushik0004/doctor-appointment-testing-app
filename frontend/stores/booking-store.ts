"use client";

import { create } from "zustand";

import type {
  AppointmentType,
  BookingPatientDetails,
} from "@/features/appointments/types";

type BookingState = {
  selectedDoctorId: string | null;
  selectedAvailabilityId: string | null;
  selectedDate: string | null;
  selectedTime: string | null;
  appointmentType: AppointmentType | null;
  patientDetails: BookingPatientDetails | null;
  confirmationId: string | null;
  setSelectedDoctorId: (doctorId: string | null) => void;
  setSelectedAvailabilityId: (availabilityId: string | null) => void;
  setSelectedDate: (date: string | null) => void;
  setSelectedTime: (time: string | null) => void;
  setAppointmentType: (appointmentType: AppointmentType | null) => void;
  setPatientDetails: (patientDetails: BookingPatientDetails | null) => void;
  setConfirmationId: (confirmationId: string | null) => void;
  resetBooking: () => void;
};

const initialState = {
  selectedDoctorId: null,
  selectedAvailabilityId: null,
  selectedDate: null,
  selectedTime: null,
  appointmentType: null,
  patientDetails: null,
  confirmationId: null,
};

export const useBookingStore = create<BookingState>()((set) => ({
  ...initialState,
  setSelectedDoctorId: (selectedDoctorId) => set({ selectedDoctorId }),
  setSelectedAvailabilityId: (selectedAvailabilityId) =>
    set({ selectedAvailabilityId }),
  setSelectedDate: (selectedDate) => set({ selectedDate }),
  setSelectedTime: (selectedTime) => set({ selectedTime }),
  setAppointmentType: (appointmentType) => set({ appointmentType }),
  setPatientDetails: (patientDetails) => set({ patientDetails }),
  setConfirmationId: (confirmationId) => set({ confirmationId }),
  resetBooking: () => set(initialState),
}));
