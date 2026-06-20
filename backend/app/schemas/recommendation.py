from enum import Enum
from datetime import date

from pydantic import BaseModel


class RecommendationReason(str, Enum):
    SAME_SPECIALTY = "same_specialty"
    RELATED_SPECIALTY = "related_specialty"


class RecommendedDoctorResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    specialty: str
    rating: float
    review_count: int
    next_available_date: date
    next_available_slot: str
    profile_image: str
    clinic_name: str
    recommendation_reason: RecommendationReason


class RecommendedDoctorsResponse(BaseModel):
    appointment_id: int
    specialty: str
    recommended_doctors: list[RecommendedDoctorResponse]
