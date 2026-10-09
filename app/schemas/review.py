from pydantic import BaseModel, Field
from typing import Optional


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    location: int = Field(..., ge=1, le=5)
    property_quality: int = Field(..., ge=1, le=5)
    amenities: int = Field(..., ge=1, le=5)
    value_for_money: int = Field(..., ge=1, le=5)
    maintenance: int = Field(..., ge=1, le=5)
    overall_experience: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)