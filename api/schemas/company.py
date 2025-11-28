from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    company_name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None


class CompanyCreate(CompanyBase):
    username: str
    email: str
    password: str


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None


class CompanyResponse(CompanyBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
