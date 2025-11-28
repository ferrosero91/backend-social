from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from apps.core.services import (
    UserService, CompanyService, CandidateService, 
    JobService, InterviewService
)

# JWT Security
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user from JWT token."""
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    
    try:
        token = AccessToken(credentials.credentials)
        user_id = token['user_id']
        user = UserService.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except (InvalidToken, TokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def get_current_company(user = Depends(get_current_user)):
    """Dependency to ensure current user is a company."""
    if user.role != 'company':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies can access this resource"
        )
    
    company = CompanyService.get_by_user_id(user.id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )
    
    return company


def get_current_candidate(user = Depends(get_current_user)):
    """Dependency to ensure current user is a candidate."""
    if user.role != 'candidate':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can access this resource"
        )
    
    candidate = CandidateService.get_by_user_id(user.id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    
    return candidate


# Service dependencies
def get_user_service() -> UserService:
    return UserService


def get_company_service() -> CompanyService:
    return CompanyService


def get_candidate_service() -> CandidateService:
    return CandidateService


def get_job_service() -> JobService:
    return JobService


def get_interview_service() -> InterviewService:
    return InterviewService
