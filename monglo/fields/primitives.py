
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseField

class StringField(BaseField):

    def __init__(
        self, *, min_length: int | None = None, max_length: int | None = None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        if self.min_length and len(value) < self.min_length:
            raise ValueError(f"String must be at least {self.min_length} characters")

        if self.max_length and len(value) > self.max_length:
            raise ValueError(f"String must be at most {self.max_length} characters")

        return value

    def get_widget_config(self) -> dict[str, Any]:
        return {"type": "text", "readonly": self.readonly, "maxLength": self.max_length}

class NumberField(BaseField):

    def __init__(
        self,
        *,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> int | float:
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError("Value must be a number") from None

        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Value must be at least {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Value must be at most {self.max_value}")

        return value

    def get_widget_config(self) -> dict[str, Any]:
        return {
            "type": "number",
            "readonly": self.readonly,
            "min": self.min_value,
            "max": self.max_value,
        }

class BooleanField(BaseField):

    def validate(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                return True
            elif value.lower() in ("false", "0", "no"):
                return False

        raise ValueError("Value must be a boolean")

    def get_widget_config(self) -> dict[str, Any]:
        return {"type": "checkbox", "readonly": self.readonly}

class DateField(BaseField):

    def validate(self, value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                pass

        raise ValueError("Value must be a valid date")

    def get_widget_config(self) -> dict[str, Any]:
        return {"type": "date", "readonly": self.readonly}

class DateTimeField(BaseField):

    def validate(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass

        raise ValueError("Value must be a valid datetime")

    def get_widget_config(self) -> dict[str, Any]:
        return {"type": "datetime", "readonly": self.readonly}
