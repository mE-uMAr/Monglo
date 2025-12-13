from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any, Callable

from .authentication_backend import AuthenticationBackend

if TYPE_CHECKING:
    from fastapi import Request
    from motor.motor_asyncio import AsyncIOMotorCollection


class MongoDBAuthenticationBackend(AuthenticationBackend):
    def __init__(
        self,
        secret_key: str,
        user_collection: AsyncIOMotorCollection,
        username_field: str = "email",
        password_field: str = "hashed_password",
        role_field: str | None = None,
        admin_role: str | None = None,
        password_verifier: Callable[[str, str], bool] | None = None,
        additional_checks: Callable[[dict], bool] | None = None,
    ):
        super().__init__(secret_key)
        self.user_collection = user_collection
        self.username_field = username_field
        self.password_field = password_field
        self.role_field = role_field
        self.admin_role = admin_role
        self.password_verifier = password_verifier or self._default_password_verifier
        self.additional_checks = additional_checks
    
    @staticmethod
    def _default_password_verifier(plain_password: str, hashed_password: str) -> bool:
        """Default password verifier using SHA256"""
        hashed = hashlib.sha256(plain_password.encode()).hexdigest()
        return hashed == hashed_password
    
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if not username or not password:
            return False
        
        # Query user from database
        user = await self.user_collection.find_one({self.username_field: username})
        
        if not user:
            return False
        
        # Verify password
        hashed_password = user.get(self.password_field)
        if not hashed_password or not self.password_verifier(password, hashed_password):
            return False
        
        # Check admin role if specified
        if self.role_field and self.admin_role:
            user_role = user.get(self.role_field)
            if user_role != self.admin_role:
                return False
        
        # Perform additional checks if specified
        if self.additional_checks and not self.additional_checks(user):
            return False
        
        # Set session data
        request.session.update({
            "user_id": str(user.get("_id")),
            "username": username,
            "is_authenticated": True
        })
        
        return True
    
    async def logout(self, request: Request) -> bool:
        """Clear session data"""
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        """Check if user is authenticated via session"""
        return request.session.get("is_authenticated", False)


class SimpleAuthenticationBackend(AuthenticationBackend):
    
    def __init__(self, secret_key: str, credentials: dict[str, str]):
        super().__init__(secret_key)
        self.credentials = credentials
    
    async def login(self, request: Request) -> bool:
        """Authenticate against in-memory credentials"""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if not username or not password:
            return False
        
        # Check credentials
        if username in self.credentials and self.credentials[username] == password:
            request.session.update({
                "username": username,
                "is_authenticated": True
            })
            return True
        
        return False
    
    async def logout(self, request: Request) -> bool:
        """Clear session data"""
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        """Check if user is authenticated via session"""
        return request.session.get("is_authenticated", False)
