"""
Table serializer for flattening documents for grid display.

Converts nested MongoDB documents into flat row data suitable for tables.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime, date
from bson import ObjectId


class TableSerializer:
    """Serialize documents for table/grid display.
    
    Flattens nested documents and applies formatters for readable display.
    
    Example:
        >>> serializer = TableSerializer(columns=["name", "email", "created_at"])
        >>> row = serializer.serialize_row(document)
        >>> # Returns flat dict with formatted values
    """
    
    def __init__(self, columns: list[dict[str, Any]]) -> None:
        """Initialize table serializer.
        
        Args:
            columns: Column configurations with field names and formatters
        """
        self.columns = columns
    
    def serialize_row(self, document: dict[str, Any]) -> dict[str, Any]:
        """Serialize a single document to table row.
        
        Args:
            document: Document to serialize
            
        Returns:
            Flat dictionary with column values
        """
        row = {}
        
        for column in self.columns:
            field = column["field"]
            value = self._get_field_value(document, field)
            
            # Apply formatter if specified
            formatter = column.get("formatter")
            if formatter:
                value = self._apply_formatter(value, formatter)
            
            row[field] = value
        
        return row
    
    def serialize_rows(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Serialize multiple documents to table rows.
        
        Args:
            documents: List of documents
            
        Returns:
            List of row dictionaries
        """
        return [self.serialize_row(doc) for doc in documents]
    
    def _get_field_value(self, document: dict[str, Any], field_path: str) -> Any:
        """Get value from document using dot notation.
        
        Args:
            document: Document to extract from
            field_path: Field path (supports dot notation)
            
        Returns:
            Field value or None if not found
        """
        keys = field_path.split(".")
        value = document
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    break
            else:
                return None
        
        return value
    
    def _apply_formatter(self, value: Any, formatter: str) -> Any:
        """Apply formatter to a value.
        
        Args:
            value: Value to format
            formatter: Formatter name
            
        Returns:
            Formatted value
        """
        if value is None:
            return None
        
        if formatter == "datetime":
            if isinstance(value, datetime):
                return value.isoformat()
        elif formatter == "date":
            if isinstance(value, (datetime, date)):
                return value.strftime("%Y-%m-%d")
        elif formatter == "objectid":
            if isinstance(value, ObjectId):
                return str(value)
        elif formatter == "boolean":
            return "Yes" if value else "No"
        elif formatter == "number":
            if isinstance(value, (int, float)):
                return f"{value:,.2f}" if isinstance(value, float) else str(value)
        
        return value
