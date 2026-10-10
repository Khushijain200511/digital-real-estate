from pydantic import BaseModel, Field
from typing import Optional, List


class AssistantRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=500)
    conversation_id: Optional[str] = None


class VoiceSearchRequest(BaseModel):
    transcript: str = Field(..., min_length=2, max_length=500)


class RecommendationsRequest(BaseModel):
    property_id: str
    limit: int = Field(10, ge=1, le=30)


class PriceEstimationRequest(BaseModel):
    property_type: str
    city: str
    locality: Optional[str] = None
    area_sqft: float = Field(..., gt=0)
    bhk: int = Field(..., ge=1, le=10)
    property_age: int = Field(0, ge=0, le=50)