from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request


class AuthenticationBackend(ABC):
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    @abstractmethod
    async def login(self, request: Request) -> bool:
        pass
    
    @abstractmethod
    async def logout(self, request: Request) -> bool:
        pass
    
    @abstractmethod
    async def authenticate(self, request: Request) -> bool:
        pass
