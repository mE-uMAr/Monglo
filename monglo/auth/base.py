
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

class BaseAuthProvider(ABC):
    
    @abstractmethod
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> dict[str, Any] | None:
        pass
    
    @abstractmethod
    async def authorize(
        self,
        user: dict[str, Any],
        action: str,
        collection: str | None = None
    ) -> bool:
        pass
    
    async def get_user_info(self, user_id: str) -> dict[str, Any] | None:
        return None
