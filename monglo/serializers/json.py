"""
JSON serializer for MongoDB documents.

Handles serialization of MongoDB-specific types to JSON-compatible formats.
"""

from __future__ import annotations

import json
from typing import Any
from datetime import datetime, date
from bson import ObjectId, DBRef, Binary


class JSONSerializer:
    """Serialize MongoDB documents to JSON.
    
    Handles conversion of MongoDB-specific types (ObjectId, datetime, Binary)
    to JSON-serializable types.
    
    Example:
        >>> serializer = JSONSerializer()
        >>> doc = {"_id": ObjectId(), "name": "Test", "created_at": datetime.now()}
        >>> json_str = serializer.serialize(doc)
        >>> # Returns JSON string with ObjectId as string
    """
    
    def serialize(self, data: Any, *, pretty: bool = False) -> str:
        """Serialize data to JSON string.
        
        Args:
            data: Data to serialize (dict, list, or primitive)
            pretty: If True, format with indentation
            
        Returns:
            JSON string
        """
        serialized = self._serialize_value(data)
        indent = 2 if pretty else None
        return json.dumps(serialized, indent=indent, ensure_ascii=False)
    
    def serialize_many(self, documents: list[dict[str, Any]], *, pretty: bool = False) -> str:
        """Serialize multiple documents to JSON array.
        
        Args:
            documents: List of documents
            pretty: If True, format with indentation
            
        Returns:
            JSON array string
        """
        return self.serialize(documents, pretty=pretty)
    
    def _serialize_value(self, value: Any) -> Any:
        """Recursively serialize a value.
        
        Args:
            value: Value to serialize
            
        Returns:
            JSON-serializable value
        """
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Binary):
            return value.hex()
        elif isinstance(value, DBRef):
            return {
                "$ref": value.collection,
                "$id": str(value.id),
                "$db": value.database
            }
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, bytes):
            return value.hex()
        else:
            return value
