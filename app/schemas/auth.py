from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    mobile: str = Field(..., min_length=10, max_length=15)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal["buyer", "seller", "builder", "agent"] = "buyer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyResetTokenRequest(BaseModel):
    token: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


class SendOTPRequest(BaseModel):
    channel: Literal["phone", "email"]
    destination: str = Field(..., min_length=10, max_length=100)
    purpose: Literal["registration", "login", "reset"] = "registration"


class VerifyOTPRequest(BaseModel):
    destination: str = Field(..., min_length=10, max_length=100)
    otp: str = Field(..., min_length=6, max_length=6)
    purpose: Literal["registration", "login", "reset"] = "registration"