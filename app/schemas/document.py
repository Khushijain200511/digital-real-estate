from pydantic import BaseModel, Field
from typing import Optional, Literal


class DocumentRequestCreate(BaseModel):
    """Buyer requests a document from the seller."""
    message: Optional[str] = None


class DocumentStatusUpdate(BaseModel):
    """Admin updates the document status."""
    status: Literal["pending", "under_review", "approved", "rejected"]
    reason: Optional[str] = None