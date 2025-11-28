from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class InterviewBase(BaseModel):
    job_posting_id: int
    candidate_id: int
    channel: str = 'web'


class InterviewCreate(InterviewBase):
    pass


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    difficulty: str
    skill_evaluated: str
    order: int
    
    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    question_id: int
    answer_text: str


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_text: str
    score: Optional[float] = None
    evaluation_notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewResponse(BaseModel):
    id: int
    job_posting_id: int
    candidate_id: int
    status: str
    channel: str
    skill_match_score: float
    final_score: Optional[float] = None
    agent_recommendation: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewDetailResponse(InterviewResponse):
    questions: List[QuestionResponse] = []
