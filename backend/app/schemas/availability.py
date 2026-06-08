from datetime import date

from pydantic import BaseModel

from app.schemas.doctor import DoctorResponse


class AvailabilitySlotResponse(BaseModel):
    id: int
    available_date: date
    start_time: str
    end_time: str
    appointment_type: str
    is_booked: bool


class DoctorAvailabilityResponse(BaseModel):
    doctor_id: int
    doctor: DoctorResponse
    available_dates: list[date]
    morning_slots: list[AvailabilitySlotResponse]
    afternoon_slots: list[AvailabilitySlotResponse]
