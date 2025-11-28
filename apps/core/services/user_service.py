from typing import Optional
from django.contrib.auth.hashers import make_password
from apps.core.models import User
from .base import BaseService


class UserService(BaseService):
    """Service for User management."""
    
    model = User
    
    @classmethod
    def create_user(cls, username: str, email: str, password: str, role: str = 'candidate', **extra_fields) -> User:
        """Create a new user with hashed password."""
        user = cls.model.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
            **extra_fields
        )
        return user
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional[User]:
        """Retrieve user by username."""
        try:
            return cls.model.objects.get(username=username)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional[User]:
        """Retrieve user by email."""
        try:
            return cls.model.objects.get(email=email)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        from django.contrib.auth import authenticate
        return authenticate(username=username, password=password)
    
    @classmethod
    def get_users_by_role(cls, role: str):
        """Get all users with a specific role."""
        return cls.model.objects.filter(role=role)
