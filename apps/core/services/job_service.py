from typing import Optional, List
from apps.core.models import JobPosting, Company
from .base import BaseService


class JobService(BaseService):
    """Service for Job Posting management."""
    
    model = JobPosting
    
    @classmethod
    def create_job(cls, company_id: int, title: str, description: str, 
                   required_skills: List[str], **job_data) -> Optional[JobPosting]:
        """Create a new job posting for a company."""
        from .company_service import CompanyService
        
        company = CompanyService.get_by_id(company_id)
        if not company:
            return None
        
        job = cls.model.objects.create(
            company=company,
            title=title,
            description=description,
            required_skills=required_skills,
            **job_data
        )
        return job
    
    @classmethod
    def get_jobs_by_company(cls, company_id: int):
        """Get all job postings for a specific company."""
        return cls.model.objects.filter(company_id=company_id)
    
    @classmethod
    def get_active_jobs(cls):
        """Get all active job postings."""
        return cls.model.objects.filter(status='active')
    
    @classmethod
    def update_job_status(cls, job_id: int, status: str) -> Optional[JobPosting]:
        """Update job posting status."""
        job = cls.get_by_id(job_id)
        if job and status in ['draft', 'active', 'closed']:
            job.status = status
            job.save()
        return job
    
    @classmethod
    def can_user_manage_job(cls, job_id: int, user_id: int) -> bool:
        """Check if a user can manage a specific job posting."""
        job = cls.get_by_id(job_id)
        if job and job.company.user_id == user_id:
            return True
        return False
