from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from api.schemas import (
    UserCreate, UserResponse, 
    CompanyCreate, CompanyResponse,
    CandidateCreate, CandidateResponse
)
from api.dependencies import (
    get_user_service, get_company_service, get_candidate_service,
    get_current_user, UserService, CompanyService, CandidateService
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register/company", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def register_company(
    data: CompanyCreate,
    company_service: CompanyService = Depends(get_company_service)
):
    """Register a new company with user account."""
    try:
        company = company_service.create_company_with_user(
            username=data.username,
            email=data.email,
            password=data.password,
            company_name=data.company_name,
            industry=data.industry,
            size=data.size,
            description=data.description,
            website=str(data.website) if data.website else None
        )
        return CompanyResponse.model_validate(company)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create company: {str(e)}"
        )


@router.post("/register/candidate", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def register_candidate(
    data: CandidateCreate,
    candidate_service: CandidateService = Depends(get_candidate_service)
):
    """Register a new candidate with user account."""
    try:
        candidate = candidate_service.create_candidate_with_user(
            username=data.username,
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            skills=data.skills,
            experience_years=data.experience_years,
            education=data.education,
            linkedin_url=str(data.linkedin_url) if data.linkedin_url else None
        )
        return CandidateResponse.model_validate(candidate)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create candidate: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(user = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
def update_current_user(
    data: UserCreate,
    user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update current authenticated user information."""
    try:
        # Update user fields
        update_data = {}
        if data.username and data.username != user.username:
            update_data['username'] = data.username
        if data.email and data.email != user.email:
            update_data['email'] = data.email
        if data.phone:
            update_data['phone'] = data.phone
        if data.password:
            from django.contrib.auth.hashers import make_password
            update_data['password'] = make_password(data.password)
        
        updated_user = user_service.update(user.id, **update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(updated_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Delete current authenticated user account."""
    success = user_service.delete(user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
