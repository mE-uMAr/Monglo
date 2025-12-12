
from __future__ import annotations

from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection

from ..core.query_builder import QueryBuilder
from ..core.registry import CollectionAdmin

class CRUDOperations:

    def __init__(self, admin: CollectionAdmin) -> None:
        self.admin = admin
        self.collection: AsyncIOMotorCollection = admin.collection

    async def list(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        filters: dict[str, Any] | None = None,
        sort: list[tuple[str, int]] | None = None,
        search: str | None = None,
        projection: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        query_parts = []

        if filters:
            filter_query = QueryBuilder.build_filter(filters)
            if filter_query:
                query_parts.append(filter_query)

        if search and self.admin.config.search_fields:
            search_query = QueryBuilder.build_search_query(search, self.admin.config.search_fields)
            if search_query:
                query_parts.append(search_query)

        final_query = QueryBuilder.combine_queries(*query_parts)

        total = await self.collection.count_documents(final_query)

        skip, limit = QueryBuilder.build_pagination_query(
            page=page,
            per_page=per_page,
            max_per_page=self.admin.config.pagination_config.get("max_per_page", 100),
        )

        sort_spec = QueryBuilder.build_sort(sort or self.admin.config.table_view.default_sort)

        cursor = self.collection.find(final_query, projection or {})

        if sort_spec:
            cursor = cursor.sort(sort_spec)

        items = await cursor.skip(skip).limit(limit).to_list(limit)

        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    async def get(self, id: str | ObjectId) -> dict[str, Any]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except InvalidId as e:
                raise ValueError(f"Invalid ObjectId: {id}") from e

        document = await self.collection.find_one({"_id": id})

        if document is None:
            raise KeyError(f"Document with _id={id} not found in {self.admin.name}")

        return document

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        if not data:
            raise ValueError("Document data cannot be empty")

        # Ensure _id is ObjectId or let MongoDB generate it
        if "_id" in data and isinstance(data["_id"], str):
            try:
                data["_id"] = ObjectId(data["_id"])
            except InvalidId as e:
                raise ValueError(f"Invalid _id: {data['_id']}") from e

        result = await self.collection.insert_one(data)

        created = await self.collection.find_one({"_id": result.inserted_id})
        return created

    async def update(
        self, id: str | ObjectId, data: dict[str, Any], *, partial: bool = True
    ) -> dict[str, Any]:
        if not data:
            raise ValueError("Update data cannot be empty")

        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except InvalidId as e:
                raise ValueError(f"Invalid ObjectId: {id}") from e

        # Don't allow updating _id
        if "_id" in data:
            data = data.copy()
            del data["_id"]

        if partial:
            result = await self.collection.update_one({"_id": id}, {"$set": data})
        else:
            result = await self.collection.replace_one({"_id": id}, data)

        if result.matched_count == 0:
            raise KeyError(f"Document with _id={id} not found in {self.admin.name}")

        updated = await self.collection.find_one({"_id": id})
        return updated

    async def delete(self, id: str | ObjectId) -> bool:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except InvalidId as e:
                raise ValueError(f"Invalid ObjectId: {id}") from e

        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0

    async def bulk_delete(self, ids: list[str | ObjectId]) -> dict[str, Any]:
        object_ids = []
        for id in ids:
            if isinstance(id, str):
                try:
                    object_ids.append(ObjectId(id))
                except InvalidId:
                    continue  # Skip invalid IDs
            else:
                object_ids.append(id)

    async def bulk_create(self, documents: list[dict]) -> list[dict]:
        if not documents:
            return []
        
        result = await self.collection.insert_many(documents)
        
        for doc, inserted_id in zip(documents, result.inserted_ids):
            doc["_id"] = inserted_id
        
        return documents
    
    async def bulk_update(
        self,
        updates: list[dict[str, Any]]
    ) -> dict[str, Any]:
        from pymongo import UpdateOne
        
        requests = [
            UpdateOne(op["filter"], op["update"])
            for op in updates
        ]
        
        result = await self.collection.bulk_write(requests)
        
        return {
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted": result.upserted_count
        }
    
    async def bulk_delete(self, ids: list[str]) -> int:
        if not ids:
            return 0
        
        object_ids = [self._to_object_id(id_str) for id_str in ids]
        
        result = await self.collection.delete_many({
            "_id": {"$in": object_ids}
        })
        
        return result.deleted_count

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        query = QueryBuilder.build_filter(filters) if filters else {}
        return await self.collection.count_documents(query)

    async def exists(self, id: str | ObjectId) -> bool:
        try:
            await self.get(id)
            return True
        except (ValueError, KeyError):
            return False
