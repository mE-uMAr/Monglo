
from __future__ import annotations

from typing import Any, Literal

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

class PaginationHandler:

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def paginate_offset(
        self,
        query: dict[str, Any],
        *,
        page: int = 1,
        per_page: int = 20,
        sort: list[tuple[str, int]] | None = None,
        projection: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        page = max(1, page)
        per_page = max(1, min(per_page, 100))

        skip = (page - 1) * per_page

        total = await self.collection.count_documents(query)

        cursor = self.collection.find(query, projection or {})

        if sort:
            cursor = cursor.sort(sort)

        items = await cursor.skip(skip).limit(per_page).to_list(per_page)

        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1

        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "strategy": "offset",
            },
        }

    async def paginate_cursor(
        self,
        query: dict[str, Any],
        *,
        cursor: str | None = None,
        per_page: int = 20,
        sort_field: str = "_id",
        sort_direction: int = 1,
        projection: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        per_page = max(1, min(per_page, 100))

        cursor_query = query.copy()

        if cursor:
            try:
                cursor_value = ObjectId(cursor)
            except Exception:
                cursor_value = cursor

            if sort_direction >= 0:
                cursor_query[sort_field] = {"$gt": cursor_value}
            else:
                cursor_query[sort_field] = {"$lt": cursor_value}

        cursor_obj = self.collection.find(cursor_query, projection or {})
        cursor_obj = cursor_obj.sort(sort_field, sort_direction)
        items = await cursor_obj.limit(per_page + 1).to_list(per_page + 1)

        has_next = len(items) > per_page
        if has_next:
            items = items[:per_page]

        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            next_cursor_value = last_item.get(sort_field)
            if isinstance(next_cursor_value, ObjectId):
                next_cursor = str(next_cursor_value)
            else:
                next_cursor = next_cursor_value

        return {
            "items": items,
            "pagination": {
                "per_page": per_page,
                "has_next": has_next,
                "next_cursor": next_cursor,
                "strategy": "cursor",
                "sort_field": sort_field,
            },
        }

    async def get_page_info(self, query: dict[str, Any], per_page: int = 20) -> dict[str, int]:
        total = await self.collection.count_documents(query)
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1

        return {"total": total, "per_page": per_page, "total_pages": total_pages}

class PaginationStrategy:

    @staticmethod
    def create(
        collection: AsyncIOMotorCollection, strategy: Literal["offset", "cursor"] = "offset"
    ) -> PaginationHandler:
        return PaginationHandler(collection)
