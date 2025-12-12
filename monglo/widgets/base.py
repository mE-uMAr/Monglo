
from abc import ABC, abstractmethod
from typing import Any

class BaseWidget(ABC):

    def __init__(self, **options):
        self.options = options

    @abstractmethod
    def render_config(self) -> dict[str, Any]:
        pass

    def validate(self, value: Any) -> bool:
        return True  # Override in subclasses for specific validation
