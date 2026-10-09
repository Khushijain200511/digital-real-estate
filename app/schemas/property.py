from pydantic import BaseModel, Field
from typing import Optional
from typing import List

class ComparePropertiesRequest(BaseModel):
    property_ids: List[str] = Field(..., min_items=2, max_items=3)


class MediaResponse(BaseModel):
    media_id: str
    url: str
    media_type: str  
    filename: Optional[str] = None
    