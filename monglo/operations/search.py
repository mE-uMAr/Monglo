
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

class SearchOperations:

    def __init__(self, collection: AsyncIOMotorCollection, search_fields: list[str] | None = None):
        self.collection = collection
        self.search_fields = search_fields or []

    async def search(
        self, query: str, *, case_sensitive: bool = False, limit: int = 100, skip: int = 0
    ) -> list[dict[str, Any]]:
        if not query or not self.search_fields:
            return []

        options = "" if case_sensitive else "i"
        conditions = [
            {field: {"$regex": query, "$options": options}} for field in self.search_fields
        ]

        cursor = self.collection.find({"$or": conditions}).skip(skip).limit(limit)
        return await cursor.to_list(limit)

    async def search_with_highlight(
        self, query: str, *, limit: int = 100, skip: int = 0
    ) -> list[dict[str, Any]]:
        results = await self.search(query, limit=limit, skip=skip)

        query_lower = query.lower()
        for doc in results:
            doc["_matched_fields"] = [
                field
                for field in self.search_fields
                if field in doc and query_lower in str(doc[field]).lower()
            ]

        return results

    async def search_count(self, query: str, *, case_sensitive: bool = False) -> int:
        if not query or not self.search_fields:
            return 0

        options = "" if case_sensitive else "i"
        conditions = [
            {field: {"$regex": query, "$options": options}} for field in self.search_fields
        ]

        return await self.collection.count_documents({"$or": conditions})

    async def search_paginated(
        self, query: str, *, page: int = 1, per_page: int = 20, case_sensitive: bool = False
    ) -> dict[str, Any]:
        skip = (page - 1) * per_page
        items = await self.search(query, case_sensitive=case_sensitive, limit=per_page, skip=skip)
        total = await self.search_count(query, case_sensitive=case_sensitive)

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }
