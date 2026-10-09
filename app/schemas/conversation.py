from pydantic import BaseModel
from typing import Optional, Literal


class ConversationCreate(BaseModel):
    property_id: str
    participant_id: str  

class MessageCreate(BaseModel):
    message: str
    message_type: Literal["text", "attachment", "system"] = "text"
    property_id: Optional[str] = None
    offer_id: Optional[str] = None