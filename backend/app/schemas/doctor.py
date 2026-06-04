from pydantic import BaseModel


class DoctorBase(BaseModel):
    name: str
    slug: str
    specialty: str
    title: str | None = None
    rating: float
    review_count: int
    clinic_name: str
    location: str
    address: str | None = None
    fee_min: int | None = None
    fee_max: int | None = None
    languages: str | None = None
    image_url: str | None = None
    is_active: bool = True


class DoctorRead(DoctorBase):
    id: int

    model_config = {"from_attributes": True}
