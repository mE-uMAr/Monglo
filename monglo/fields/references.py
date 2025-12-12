"""
Reference field types for MongoDB.

ObjectIdField and DBRefField for handling references.
"""

from __future__ import annotations

from typing import Any
from bson import ObjectId, DBRef
from bson.errors import InvalidId

from .base import BaseField


class ObjectIdField(BaseField):
    """ObjectId field type.
    
    Example:
        >>> field = ObjectIdField()
        >>> oid = field.validate("507f1f77bcf86cd799439011")
        >>> isinstance(oid, ObjectId)
        True
    """
    
    def validate(self, value: Any) -> ObjectId:
        """Validate ObjectId value."""
        if isinstance(value, ObjectId):
            return value
        
        if isinstance(value, str):
            try:
                return ObjectId(value)
            except InvalidId:
                raise ValueError(f"Invalid ObjectId: {value}")
        
        raise ValueError("Value must be an ObjectId or valid ObjectId string")
    
    def get_widget_config(self) -> dict[str, Any]:
        """Get widget configuration."""
        return {
            "type": "text",
            "readonly": self.readonly,
            "format": "objectid"
        }


class DBRefField(BaseField):
    """DBRef field type.
    
    Example:
        >>> field = DBRefField(collection="users")
        >>> ref = field.validate(ObjectId())
    """
    
    def __init__(
        self,
        *,
        collection: str,
        database: str | None = None,
        **kwargs
    ) -> None:
        """Initialize DBRef field.
        
        Args:
            collection: Target collection name
            database: Optional database name
            **kwargs: Base field arguments
        """
        super().__init__(**kwargs)
        self.collection = collection
        self.database = database
    
    def validate(self, value: Any) -> DBRef:
        """Validate DBRef value."""
        if isinstance(value, DBRef):
            return value
        
        if isinstance(value, ObjectId):
            return DBRef(self.collection, value, self.database)
        
        if isinstance(value, str):
            try:
                oid = ObjectId(value)
                return DBRef(self.collection, oid, self.database)
            except InvalidId:
                raise ValueError(f"Invalid ObjectId for DBRef: {value}")
        
        raise ValueError("Value must be DBRef, ObjectId, or ObjectId string")
    
    def get_widget_config(self) -> dict[str, Any]:
        """Get widget configuration."""
        return {
            "type": "reference",
            "readonly": self.readonly,
            "collection": self.collection
        }
