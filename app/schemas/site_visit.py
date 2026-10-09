from pydantic import BaseModel, Field
from typing import Optional, Literal


class SiteVisitCreate(BaseModel):
  
    property_id: str
    date: str = Field(..., description="Format: YYYY-MM-DD")  
    time: str = Field(..., description="Format: HH:MM")      
    notes: Optional[str] = None


class SiteVisitUpdate(BaseModel):
  
    status: Optional[Literal["approved", "rescheduled", "cancelled", "completed"]] = None
    date: Optional[str] = None     
    time: Optional[str] = None     
    notes: Optional[str] = None