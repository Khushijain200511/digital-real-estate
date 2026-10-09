from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class VerificationSubmit(BaseModel):
    document_ids: List[str] = Field(..., min_items=1)
    notes: Optional[str] = None


class VerificationUpdate(BaseModel):
    status: Literal["verified", "rejected", "under_review"]
    notes: Optional[str] = None