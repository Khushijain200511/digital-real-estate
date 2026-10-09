from pydantic import BaseModel, Field
from typing import Optional, Literal


class BookingCreate(BaseModel):
    property_id: str
    offer_id: str
    agreed_price: float = Field(..., gt=0)
    booking_amount: float = Field(..., gt=0)


class BookingUpdate(BaseModel):
    status: Literal["payment_pending", "confirmed", "cancelled", "completed"]
    notes: Optional[str] = None