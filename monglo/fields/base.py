"""
Base field type for Monglo.

Provides abstract base class for all field types with validation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseField(ABC):
    """Abstract base class for field types.
    
    Provides validation interface and widget configuration.
    
    Attributes:
        required: Whether field is required
        default: Default value
        label: Display label
        help_text: Help text for UI
        
    Example:
        >>> class MyField(BaseField):
        ...     def validate(self, value):
        ...         if not isinstance(value, str):
        ...             raise ValueError("Must be string")
        ...         return value
    """
    
    def __init__(
        self,
        *,
        required: bool = False,
        default: Any = None,
        label: str | None = None,
        help_text: str | None = None,
        readonly: bool = False
    ) -> None:
        """Initialize field.
        
        Args:
            required: Whether field is required
            default: Default value
            label: Display label
            help_text: Help text
            readonly: Whether field is readonly
        """
        self.required = required
        self.default = default
        self.label = label
        self.help_text = help_text
        self.readonly = readonly
    
    @abstractmethod
    def validate(self, value: Any) -> Any:
        """Validate and clean a value.
        
        Args:
            value: Value to validate
            
        Returns:
            Cleaned value
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    @abstractmethod
    def get_widget_config(self) -> dict[str, Any]:
        """Get widget configuration for UI.
        
        Returns:
            Widget configuration dictionary
        """
        pass
    
    def to_python(self, value: Any) -> Any:
        """Convert value to Python type.
        
        Args:
            value: Raw value
            
        Returns:
            Python value
        """
        if value is None:
            if self.required:
                raise ValueError("Field is required")
            return self.default
        
        return self.validate(value)
