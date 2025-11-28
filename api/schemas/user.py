from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: str = 'candidate'
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    phone: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access: str
    refresh: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str
