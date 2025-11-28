from typing import Optional, List, Dict, Any
from django.db.models import Model, QuerySet


class BaseService:
    """Base service class for common CRUD operations."""
    
    model: Model = None
    
    @classmethod
    def get_by_id(cls, obj_id: int) -> Optional[Model]:
        """Retrieve an object by ID."""
        try:
            return cls.model.objects.get(id=obj_id)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def get_all(cls, filters: Optional[Dict[str, Any]] = None) -> QuerySet:
        """Retrieve all objects with optional filters."""
        queryset = cls.model.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    @classmethod
    def create(cls, **data) -> Model:
        """Create a new object."""
        return cls.model.objects.create(**data)
    
    @classmethod
    def update(cls, obj_id: int, **data) -> Optional[Model]:
        """Update an existing object."""
        obj = cls.get_by_id(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
        return obj
    
    @classmethod
    def delete(cls, obj_id: int) -> bool:
        """Delete an object by ID."""
        obj = cls.get_by_id(obj_id)
        if obj:
            obj.delete()
            return True
        return False
