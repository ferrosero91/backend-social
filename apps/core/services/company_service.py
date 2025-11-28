from typing import Optional
from apps.core.models import Company, User
from .base import BaseService


class CompanyService(BaseService):
    """Service for Company management."""
    
    model = Company
    
    @classmethod
    def create_company_with_user(cls, username: str, email: str, password: str, 
                                  company_name: str, **company_data) -> Company:
        """Create a company profile along with its user account."""
        from .user_service import UserService
        
        user = UserService.create_user(
            username=username,
            email=email,
            password=password,
            role='company'
        )
        
        company = cls.model.objects.create(
            user=user,
            company_name=company_name,
            **company_data
        )
        return company
    
    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional[Company]:
        """Get company profile by user ID."""
        try:
            return cls.model.objects.get(user_id=user_id)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def get_company_jobs(cls, company_id: int):
        """Get all job postings for a company."""
        company = cls.get_by_id(company_id)
        if company:
            return company.job_postings.all()
        return []
