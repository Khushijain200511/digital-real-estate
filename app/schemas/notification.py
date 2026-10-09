from pydantic import BaseModel
from typing import Optional, Literal


NotificationType = Literal[
    "offer_received",
    "offer_accepted",
    "offer_rejected",
    "offer_countered",
    "booking_created",
    "booking_confirmed",
    "payment_received",
    "verification_approved",
    "verification_rejected",
    "new_message",
    "site_visit_requested",
    "site_visit_approved",
    "site_visit_cancelled",
    "document_uploaded",
    "document_requested",
    "system",
]


class NotificationCreate(BaseModel):
   
    user_id: str
    title: str
    body: Optional[str] = None
    type: NotificationType = "system"
    reference_id: Optional[str] = None   
    reference_type: Optional[str] = None 
    action_url: Optional[str] = None