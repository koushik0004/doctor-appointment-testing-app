import json

from sqlalchemy import Boolean, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    specialty: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False)
    clinic_name: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    consultation_fee_min: Mapped[int] = mapped_column(Integer, nullable=False)
    consultation_fee_max: Mapped[int] = mapped_column(Integer, nullable=False)
    next_available_slot: Mapped[str] = mapped_column(Text, nullable=False)
    appointment_types: Mapped[str] = mapped_column(Text, nullable=False)
    languages: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    @staticmethod
    def encode_list(values: list[str]) -> str:
        return json.dumps(values)

    @staticmethod
    def decode_list(values: str) -> list[str]:
        return json.loads(values)
