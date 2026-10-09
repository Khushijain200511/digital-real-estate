from pydantic import BaseModel, Field
from typing import Optional



class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    mobile: Optional[str] = None
    role: str
    is_verified: bool = False



class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    mobile: Optional[str] = Field(None, min_length=10, max_length=15)