
from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase

class AuditLogger:
    
    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        collection_name: str = "monglo_audit_log"
    ):
        self.db = database
        self.collection = database[collection_name]
    
    async def log_create(
        self,
        collection: str,
        document: dict[str, Any],
        user: dict[str, Any] | None = None
    ) -> None:
        await self._log_action(
            action="create",
            collection=collection,
            document_id=str(document.get("_id")),
            user=user,
            data=document
        )
    
    async def log_update(
        self,
        collection: str,
        document_id: str,
        before: dict[str, Any],
        after: dict[str, Any],
        user: dict[str, Any] | None = None
    ) -> None:
        changes = self._calculate_changes(before, after)
        
        await self._log_action(
            action="update",
            collection=collection,
            document_id=document_id,
            user=user,
            changes=changes,
            before=before,
            after=after
        )
    
    async def log_delete(
        self,
        collection: str,
        document_id: str,
        document: dict[str, Any],
        user: dict[str, Any] | None = None
    ) -> None:
        await self._log_action(
            action="delete",
            collection=collection,
            document_id=document_id,
            user=user,
            data=document
        )
    
    async def log_bulk_operation(
        self,
        collection: str,
        action: str,
        count: int,
        user: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        await self._log_action(
            action=action,
            collection=collection,
            user=user,
            count=count,
            details=details
        )
    
    async def _log_action(
        self,
        action: str,
        collection: str,
        user: dict[str, Any] | None = None,
        **kwargs
    ) -> None:
        log_entry = {
            "timestamp": datetime.utcnow(),
            "action": action,
            "collection": collection,
            "user": {
                "id": user.get("id") if user else "anonymous",
                "role": user.get("role") if user else None
            } if user else None,
            **kwargs
        }
        
        await self.collection.insert_one(log_entry)
    
    def _calculate_changes(
        self,
        before: dict[str, Any],
        after: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        changes = {}
        
        # Find changed fields
        all_keys = set(before.keys()) | set(after.keys())
        
        for key in all_keys:
            old_value = before.get(key)
            new_value = after.get(key)
            
            if old_value != new_value:
                changes[key] = {
                    "old": old_value,
                    "new": new_value
                }
        
        return changes
    
    async def get_document_history(
        self,
        collection: str,
        document_id: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        cursor = self.collection.find({
            "collection": collection,
            "document_id": document_id
        }).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_user_activity(
        self,
        user_id: str,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        cursor = self.collection.find({
            "user.id": user_id
        }).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
