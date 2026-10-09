from pydantic import BaseModel, Field
from typing import Optional, Literal


class OfferCreate(BaseModel):
  
    property_id: str
    amount: float = Field(..., gt=0)
    message: Optional[str] = None


class CounterOfferRequest(BaseModel):
  
    amount: float = Field(..., gt=0)
    message: Optional[str] = None


class RejectOfferRequest(BaseModel):
   
    reason: Optional[str] = None