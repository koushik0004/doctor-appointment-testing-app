"use client";

import { create } from "zustand";

import type {
  AppointmentType,
  BookingPatientDetails,
} from "@/features/appointments/types";

type BookingState = {
  selectedDoctorId: string | null;
  selectedDate: string | null;
  selectedTime: string | null;
  appointmentType: AppointmentType | null;
  patientDetails: BookingPatientDetails | null;
  appointmentId: number | null;
  confirmationCode: string | null;
  setSelectedDoctorId: (doctorId: string | null) => void;
  setSelectedDate: (date: string | null) => void;
  setSelectedTime: (time: string | null) => void;
  setAppointmentType: (appointmentType: AppointmentType | null) => void;
  setPatientDetails: (patientDetails: BookingPatientDetails | null) => void;
  setAppointmentId: (appointmentId: number | null) => void;
  setConfirmationCode: (confirmationCode: string | null) => void;
  resetBooking: () => void;
};

const initialState = {
  selectedDoctorId: null,
  selectedDate: null,
  selectedTime: null,
  appointmentType: null,
  patientDetails: null,
  appointmentId: null,
  confirmationCode: null,
};

export const useBookingStore = create<BookingState>()((set) => ({
  ...initialState,
  setSelectedDoctorId: (selectedDoctorId) => set({ selectedDoctorId }),
  setSelectedDate: (selectedDate) => set({ selectedDate }),
  setSelectedTime: (selectedTime) => set({ selectedTime }),
  setAppointmentType: (appointmentType) => set({ appointmentType }),
  setPatientDetails: (patientDetails) => set({ patientDetails }),
  setAppointmentId: (appointmentId) => set({ appointmentId }),
  setConfirmationCode: (confirmationCode) => set({ confirmationCode }),
  resetBooking: () => set(initialState),
}));
