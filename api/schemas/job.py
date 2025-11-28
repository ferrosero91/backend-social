from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    experience_required: int = 0
    location: Optional[str] = None
    salary_range: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_required: Optional[int] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = None


class JobResponse(JobBase):
    id: int
    company_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
