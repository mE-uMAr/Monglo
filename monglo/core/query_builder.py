
import re
from typing import Any

from bson import ObjectId
from bson import errors as bson_errors

class QueryBuilder:

    @staticmethod
    def build_filter(filters: dict[str, Any] | None = None) -> dict[str, Any]:
        if not filters:
            return {}

        query: dict[str, Any] = {}

        for key, value in filters.items():
            if "__" in key:
                field, operator = key.rsplit("__", 1)
            else:
                field = key
                operator = "eq"

            if operator == "eq":
                query[field] = QueryBuilder._convert_value(value, field)
            elif operator == "ne":
                query[field] = {"$ne": QueryBuilder._convert_value(value, field)}
            elif operator == "gt":
                query[field] = {"$gt": QueryBuilder._convert_value(value, field)}
            elif operator == "gte":
                query[field] = {"$gte": QueryBuilder._convert_value(value, field)}
            elif operator == "lt":
                query[field] = {"$lt": QueryBuilder._convert_value(value, field)}
            elif operator == "lte":
                query[field] = {"$lte": QueryBuilder._convert_value(value, field)}
            elif operator == "in":
                query[field] = {"$in": [QueryBuilder._convert_value(v, field) for v in value]}
            elif operator == "nin":
                query[field] = {"$nin": [QueryBuilder._convert_value(v, field) for v in value]}
            elif operator == "regex":
                query[field] = {"$regex": value, "$options": "i"}  # Case-insensitive
            elif operator == "range":
                if len(value) == 2:
                    query[field] = {
                        "$gte": QueryBuilder._convert_value(value[0], field),
                        "$lte": QueryBuilder._convert_value(value[1], field),
                    }
            elif operator == "exists":
                query[field] = {"$exists": bool(value)}

        return query

    @staticmethod
    def build_search_query(search: str, fields: list[str]) -> dict[str, Any]:
        if not search or not fields:
            return {}

        # Escape special regex characters
        escaped_search = re.escape(search)

        or_conditions = [{field: {"$regex": escaped_search, "$options": "i"}} for field in fields]

        return {"$or": or_conditions}

    @staticmethod
    def build_sort(sort: list[tuple[str, int]] | None = None) -> list[tuple[str, int]]:
        if not sort:
            return [("_id", 1)]  # Default sort by _id

        return sort

    @staticmethod
    def combine_queries(*queries: dict[str, Any]) -> dict[str, Any]:
        non_empty = [q for q in queries if q]

        if not non_empty:
            return {}

        if len(non_empty) == 1:
            return non_empty[0]

        return {"$and": non_empty}

    @staticmethod
    def _convert_value(value: Any, field: str) -> Any:
        # Try to convert to ObjectId if field ends with _id
        if field.endswith("_id") or field == "_id":
            if isinstance(value, str):
                try:
                    return ObjectId(value)
                except (bson_errors.InvalidId, TypeError):
                    pass

        return value

    @staticmethod
    def build_pagination_query(
        page: int = 1, per_page: int = 20, max_per_page: int = 100
    ) -> tuple[int, int]:
        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))

        skip = (page - 1) * per_page
        limit = per_page

        return skip, limit

    @staticmethod
    def build_projection(
        fields: list[str] | None = None, exclude_fields: list[str] | None = None
    ) -> dict[str, int] | None:
        if fields:
            # Include specific fields (always include _id unless explicitly excluded)
            projection = {field: 1 for field in fields}
            if "_id" not in fields and exclude_fields and "_id" in exclude_fields:
                projection["_id"] = 0
            return projection

        if exclude_fields:
            # Exclude specific fields
            return {field: 0 for field in exclude_fields}

        return None  # Return all fields
