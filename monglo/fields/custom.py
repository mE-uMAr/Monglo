
from __future__ import annotations

from typing import Any, Callable

from .base import BaseField

class CustomField(BaseField):
    
    def __init__(
        self,
        validator: Callable[[Any], bool] | None = None,
        serializer: Callable[[Any], Any] | None = None,
        widget_config: dict[str, Any] | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._custom_validator = validator
        self._custom_serializer = serializer
        self._widget_config = widget_config or {}
    
    def validate(self, value: Any) -> bool:
        if self._custom_validator:
            return self._custom_validator(value)
        return True  # Default: accept any value
    
    def serialize(self, value: Any) -> Any:
        if self._custom_serializer:
            return self._custom_serializer(value)
        return value  # Default: return as-is
    
    def get_widget_config(self) -> dict[str, Any]:
        return self._widget_config

class EnumField(CustomField):
    
    def __init__(self, choices: list[str], **kwargs):
        self.choices = choices
        super().__init__(
            validator=lambda v: v in choices,
            widget_config={
                "type": "select",
                "choices": [{"value": c, "label": c.title()} for c in choices]
            },
            **kwargs
        )

class URLField(CustomField):
    
    def __init__(self, require_https: bool = False, **kwargs):
        self.require_https = require_https
        
        def validate_url(value: str) -> bool:
            import re
            if not isinstance(value, str):
                return False
            
            pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(pattern, value):
                return False
            
            if self.require_https and not value.startswith('https://'):
                return False
            
            return True
        
        super().__init__(
            validator=validate_url,
            widget_config={
                "type": "url",
                "placeholder": "https://example.com"
            },
            **kwargs
        )

class ColorField(CustomField):
    
    def __init__(self, **kwargs):
        def validate_color(value: str) -> bool:
            import re
            if not isinstance(value, str):
                return False
            return bool(re.match(r'^#[0-9A-Fa-f]{6}$', value))
        
        super().__init__(
            validator=validate_color,
            widget_config={
                "type": "color",
                "default": "#000000"
            },
            **kwargs
        )

class JSONField(CustomField):
    
    def __init__(self, schema: dict | None = None, **kwargs):
        self.schema = schema
        
        def validate_json(value: Any) -> bool:
            # Allow dict or list (JSON-serializable types)
            if isinstance(value, (dict, list)):
                return True
            
            # Try parsing if string
            if isinstance(value, str):
                try:
                    import json
                    json.loads(value)
                    return True
                except:
                    return False
            
            return False
        
        super().__init__(
            validator=validate_json,
            widget_config={
                "type": "json",
                "schema": schema
            },
            **kwargs
        )
