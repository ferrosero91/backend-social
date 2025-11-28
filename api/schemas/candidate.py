from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class CandidateBase(BaseModel):
    full_name: str
    skills: List[str] = []
    experience_years: int = 0
    education: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None


class CandidateCreate(CandidateBase):
    username: str
    email: str
    password: str


class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None


class CandidateResponse(CandidateBase):
    id: int
    user_id: int
    cv_parsed_data: Dict = {}
    created_at: datetime
    
    class Config:
        from_attributes = True
