
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

class BaseField(ABC):

    def __init__(
        self,
        *,
        required: bool = False,
        default: Any = None,
        label: str | None = None,
        help_text: str | None = None,
        readonly: bool = False,
    ) -> None:
        self.required = required
        self.default = default
        self.label = label
        self.help_text = help_text
        self.readonly = readonly

    @abstractmethod
    def validate(self, value: Any) -> Any:
        pass

    @abstractmethod
    def get_widget_config(self) -> dict[str, Any]:
        pass

    def to_python(self, value: Any) -> Any:
        if value is None:
            if self.required:
                raise ValueError("Field is required")
            return self.default

        return self.validate(value)
