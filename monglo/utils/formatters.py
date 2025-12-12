
from __future__ import annotations

from datetime import datetime, date
from typing import Any
from bson import ObjectId

class Formatter:
    
    @staticmethod
    def format_datetime(value: datetime | None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime(format_str)
        return str(value)
    
    @staticmethod
    def format_date(value: date | datetime | None, format_str: str = "%Y-%m-%d") -> str:
        if value is None:
            return ""
        if isinstance(value, (date, datetime)):
            return value.strftime(format_str)
        return str(value)
    
    @staticmethod
    def format_number(value: int | float | None, decimals: int = 2) -> str:
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:,.{decimals}f}"
        if isinstance(value, int):
            return f"{value:,}"
        return str(value)
    
    @staticmethod
    def format_currency(value: int | float | None, currency: str = "$") -> str:
        if value is None:
            return ""
        formatted = Formatter.format_number(value, decimals=2)
        return f"{currency}{formatted}"
    
    @staticmethod
    def format_percentage(value: int | float | None, decimals: int = 1) -> str:
        if value is None:
            return ""
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_objectid(value: ObjectId | str | None) -> str:
        if value is None:
            return ""
        id_str = str(value)
        # Show first 8 and last 8 characters
        if len(id_str) > 16:
            return f"{id_str[:8]}...{id_str[-8:]}"
        return id_str
    
    @staticmethod
    def format_boolean(value: bool | None, true_text: str = "Yes", false_text: str = "No") -> str:
        if value is None:
            return ""
        return true_text if value else false_text
    
    @staticmethod
    def truncate(value: str | None, length: int = 50, suffix: str = "...") -> str:
        if value is None:
            return ""
        value_str = str(value)
        if len(value_str) <= length:
            return value_str
        return value_str[:length - len(suffix)] + suffix
    
    @staticmethod
    def format_bytes(value: int | None) -> str:
        if value is None:
            return ""
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if value < 1024.0:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        
        return f"{value:.1f} PB"
    
    @staticmethod
    def format_list(value: list | None, separator: str = ", ", max_items: int = 5) -> str:
        if value is None or not isinstance(value, list):
            return ""
        
        if len(value) == 0:
            return "[]"
        
        if len(value) <= max_items:
            return separator.join(str(v) for v in value)
        
        shown = separator.join(str(v) for v in value[:max_items])
        remaining = len(value) - max_items
        return f"{shown}... (+{remaining} more)"
    
    @staticmethod
    def format_dict_summary(value: dict | None, max_keys: int = 3) -> str:
        if value is None or not isinstance(value, dict):
            return ""
        
        if len(value) == 0:
            return "{}"
        
        keys = list(value.keys())
        if len(keys) <= max_keys:
            return "{" + ", ".join(f"{k}: {value[k]}" for k in keys) + "}"
        
        shown = ", ".join(keys[:max_keys])
        remaining = len(keys) - max_keys
        return f"{{{shown}... (+{remaining} keys)}}"
