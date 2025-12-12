"""
Document serializer for preserving structure in detail views.

Handles nested documents and relationships while maintaining tree structure.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime, date
from bson import ObjectId, DBRef


class DocumentSerializer:
    """Serialize documents with full structure preservation.
    
    Maintains nested document structure and includes type annotations
    for UI widget selection.
    
    Example:
        >>> serializer = DocumentSerializer()
        >>> result = serializer.serialize(document, schema=schema)
        >>> # Returns document with type annotations
    """
    
    def serialize(
        self,
        document: dict[str, Any],
        *,
        schema: dict[str, Any] | None = None,
        include_types: bool = True
    ) -> dict[str, Any]:
        """Serialize document with optional type annotations.
        
        Args:
            document: Document to serialize
            schema: Optional schema for type information
            include_types: Whether to include type annotations
            
        Returns:
            Serialized document
        """
        schema = schema or {}
        
        result = {}
        for key, value in document.items():
            serialized_value = self._serialize_value(value)
            
            if include_types and key in schema:
                result[key] = {
                    "value": serialized_value,
                    "type": schema[key].get("type", "string"),
                    "metadata": {
                        "nullable": schema[key].get("nullable", False),
                        "frequency": schema[key].get("frequency", 1.0)
                    }
                }
            else:
                result[key] = serialized_value
        
        return result
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize a single value, preserving structure.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized value
        """
        if isinstance(value, ObjectId):
            return {"$oid": str(value)}
        elif isinstance(value, datetime):
            return {"$date": value.isoformat()}
        elif isinstance(value, date):
            return {"$date": value.isoformat()}
        elif isinstance(value, DBRef):
            return {
                "$ref": value.collection,
                "$id": str(value.id)
            }
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, bytes):
            return {"$binary": value.hex()}
        else:
            return value
