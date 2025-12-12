
from __future__ import annotations

from typing import Any
import hashlib

from .base import BaseAuthProvider

class SimpleAuthProvider(BaseAuthProvider):
    
    def __init__(
        self,
        users: dict[str, dict[str, Any]] | None = None,
        user_collection=None
    ):
        self.users = users or {}
        self.user_collection = user_collection
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> dict[str, Any] | None:
        password_hash = self.hash_password(password)
        
        if username in self.users:
            user_data = self.users[username]
            if user_data.get("password_hash") == password_hash:
                return {
                    "id": username,
                    "username": username,
                    "role": user_data.get("role", "user"),
                    **{k: v for k, v in user_data.items() 
                       if k not in ["password_hash"]}
                }
        
        if self.user_collection:
            user = await self.user_collection.find_one({
                "username": username,
                "password_hash": password_hash
            })
            
            if user:
                return {
                    "id": str(user["_id"]),
                    "username": username,
                    "role": user.get("role", "user"),
                    **{k: v for k, v in user.items() 
                       if k not in ["_id", "password_hash"]}
                }
        
        return None
    
    async def authorize(
        self,
        user: dict[str, Any],
        action: str,
        collection: str | None = None
    ) -> bool:
        role = user.get("role", "readonly")
        
        if role == "admin":
            return True
        
        if role == "user":
            return action in ["read", "create", "update"]
        
        if role == "readonly":
            return action == "read"
        
        return False
    
    async def get_user_info(self, user_id: str) -> dict[str, Any] | None:
        if user_id in self.users:
            user_data = self.users[user_id]
            return {
                "id": user_id,
                "username": user_id,
                "role": user_data.get("role", "user")
            }
        
        if self.user_collection:
            from bson import ObjectId
            try:
                user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    return {
                        "id": str(user["_id"]),
                        "username": user.get("username"),
                        "role": user.get("role", "user")
                    }
            except:
                pass
        
        return None
