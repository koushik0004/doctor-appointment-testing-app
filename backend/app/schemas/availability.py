from datetime import date

from pydantic import BaseModel


class AvailabilitySlotResponse(BaseModel):
    id: int
    available_date: date
    start_time: str
    end_time: str
    is_booked: bool


class DoctorAvailabilityResponse(BaseModel):
    date: date
    doctor_id: int
    available_slots: list[AvailabilitySlotResponse]
