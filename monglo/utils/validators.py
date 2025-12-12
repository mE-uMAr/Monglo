
from __future__ import annotations

import re
from datetime import datetime, date
from typing import Any
from bson import ObjectId

class Validator:
    
    @staticmethod
    def is_valid_email(value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_valid_url(value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_valid_objectid(value: str | ObjectId) -> bool:
        if isinstance(value, ObjectId):
            return True
        
        if not isinstance(value, str):
            return False
        
        if len(value) != 24:
            return False
        
        try:
            ObjectId(value)
            return True
        except:
            return False
    
    @staticmethod
    def is_valid_date(value: str | date | datetime) -> bool:
        if isinstance(value, (date, datetime)):
            return True
        
        if not isinstance(value, str):
            return False
        
        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    @staticmethod
    def is_in_range(value: int | float, min_val: int | float | None = None, 
                    max_val: int | float | None = None) -> bool:
        if not isinstance(value, (int, float)):
            return False
        
        if min_val is not None and value < min_val:
            return False
        
        if max_val is not None and value > max_val:
            return False
        
        return True
    
    @staticmethod
    def has_min_length(value: str, min_length: int) -> bool:
        if not isinstance(value, str):
            return False
        return len(value) >= min_length
    
    @staticmethod
    def has_max_length(value: str, max_length: int) -> bool:
        if not isinstance(value, str):
            return False
        return len(value) <= max_length
    
    @staticmethod
    def matches_pattern(value: str, pattern: str) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_not_empty(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True
