from pydantic import BaseModel, Field
from typing import Optional


class PaymentOrderCreate(BaseModel):
    booking_id: str
    amount: float = Field(..., gt=0)
    currency: str = "INR"


class PaymentVerify(BaseModel):
    payment_id: str
    gateway_order_id: str
    gateway_payment_id: str
    signature: str


class PaymentWebhook(BaseModel):
    event: str
    payment_id: str
    booking_id: Optional[str] = None
    amount: float
    status: str