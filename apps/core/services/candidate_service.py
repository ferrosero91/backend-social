from typing import Optional
from apps.core.models import Candidate, User
from .base import BaseService


class CandidateService(BaseService):
    """Service for Candidate management."""
    
    model = Candidate
    
    @classmethod
    def create_candidate_with_user(cls, username: str, email: str, password: str,
                                    full_name: str, **candidate_data) -> Candidate:
        """Create a candidate profile along with its user account."""
        from .user_service import UserService
        
        user = UserService.create_user(
            username=username,
            email=email,
            password=password,
            role='candidate'
        )
        
        candidate = cls.model.objects.create(
            user=user,
            full_name=full_name,
            **candidate_data
        )
        return candidate
    
    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional[Candidate]:
        """Get candidate profile by user ID."""
        try:
            return cls.model.objects.get(user_id=user_id)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def update_cv(cls, candidate_id: int, cv_file, parsed_data: dict = None) -> Optional[Candidate]:
        """Update candidate's CV and parsed data."""
        candidate = cls.get_by_id(candidate_id)
        if candidate:
            candidate.cv_file = cv_file
            if parsed_data:
                candidate.cv_parsed_data = parsed_data
            candidate.save()
        return candidate
    
    @classmethod
    def get_candidate_interviews(cls, candidate_id: int):
        """Get all interviews for a candidate."""
        candidate = cls.get_by_id(candidate_id)
        if candidate:
            return candidate.interviews.all()
        return []
