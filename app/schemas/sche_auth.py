from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.config import settings


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    dob: Optional[float] = None
    gender: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    identity_card: Optional[str] = None
    identity_card_date: Optional[float] = None
    identity_card_place: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRequest(BaseModel):
    exp: float
    auth_time: float
    sub: str
    typ: Optional[str] = "Bearer"
    email: Optional[EmailStr] = None


class TokenResponse(BaseModel):
    access_token: str
    expires_in: Optional[float] = settings.ACCESS_TOKEN_EXPIRE_SECONDS
    refresh_expires_in: Optional[float] = settings.ACCESS_TOKEN_EXPIRE_SECONDS
    token_type: Optional[str] = "Bearer"
