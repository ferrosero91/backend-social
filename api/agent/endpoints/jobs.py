from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from api.schemas import JobCreate, JobUpdate, JobResponse
from api.dependencies import (
    get_job_service, get_current_company, get_current_user,
    JobService
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    data: JobCreate,
    company = Depends(get_current_company),
    job_service: JobService = Depends(get_job_service)
):
    """Create a new job posting (Company only)."""
    job = job_service.create_job(
        company_id=company.id,
        title=data.title,
        description=data.description,
        required_skills=data.required_skills,
        experience_required=data.experience_required,
        location=data.location,
        salary_range=data.salary_range
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create job posting"
        )
    
    return JobResponse.model_validate(job)


@router.get("", response_model=List[JobResponse])
def list_jobs(
    status_filter: str = None,
    job_service: JobService = Depends(get_job_service)
):
    """List all job postings with optional status filter."""
    if status_filter:
        jobs = job_service.get_all(filters={'status': status_filter})
    else:
        jobs = job_service.get_active_jobs()
    
    return [JobResponse.model_validate(job) for job in jobs]


@router.get("/my-jobs", response_model=List[JobResponse])
def list_my_jobs(
    company = Depends(get_current_company),
    job_service: JobService = Depends(get_job_service)
):
    """List all job postings for the current company."""
    jobs = job_service.get_jobs_by_company(company.id)
    return [JobResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service)
):
    """Get a specific job posting by ID."""
    job = job_service.get_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    
    return JobResponse.model_validate(job)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    data: JobUpdate,
    user = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
):
    """Update a job posting (Company owner only)."""
    if not job_service.can_user_manage_job(job_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this job"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    job = job_service.update(job_id, **update_data)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    user = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service)
):
    """Delete a job posting (Company owner only)."""
    if not job_service.can_user_manage_job(job_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this job"
        )
    
    success = job_service.delete(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
