"use client";

export function buildAppointmentBookingUrl(doctorId: number) {
  return `/appointments?doctorId=${encodeURIComponent(String(doctorId))}`;
}
