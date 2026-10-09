from pydantic import BaseModel, Field
from typing import Optional


class SavedSearchCreate(BaseModel):
  
    name: str = Field(..., min_length=2, max_length=100)
    city: Optional[str] = None
    locality: Optional[str] = None
    property_type: Optional[str] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    bhk: Optional[int] = None
    parking: Optional[bool] = None
    possession_status: Optional[str] = None   
    amenities: Optional[list[str]] = []


class SavedSearchUpdate(BaseModel):
   
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    city: Optional[str] = None
    locality: Optional[str] = None
    property_type: Optional[str] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    bhk: Optional[int] = None
    parking: Optional[bool] = None
    possession_status: Optional[str] = None
    amenities: Optional[list[str]] = None