
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

class AggregationOperations:

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def aggregate(self, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(None)

    async def get_field_stats(
        self, field: str, *, query: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        pipeline: list[dict[str, Any]] = []

        if query:
            pipeline.append({"$match": query})

        pipeline.append(
            {
                "$group": {
                    "_id": None,
                    "min": {"$min": f"${field}"},
                    "max": {"$max": f"${field}"},
                    "avg": {"$avg": f"${field}"},
                    "sum": {"$sum": f"${field}"},
                    "count": {"$sum": 1},
                }
            }
        )

        results = await self.aggregate(pipeline)

        if results:
            stats = results[0]
            stats.pop("_id", None)
            return stats

        return {"min": None, "max": None, "avg": None, "sum": None, "count": 0}

    async def group_by(
        self,
        field: str,
        *,
        count: bool = True,
        sum_field: str | None = None,
        avg_field: str | None = None,
        query: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        pipeline: list[dict[str, Any]] = []

        if query:
            pipeline.append({"$match": query})

        group_stage: dict[str, Any] = {"_id": f"${field}"}

        if count:
            group_stage["count"] = {"$sum": 1}

        if sum_field:
            group_stage["total"] = {"$sum": f"${sum_field}"}

        if avg_field:
            group_stage["average"] = {"$avg": f"${avg_field}"}

        pipeline.append({"$group": group_stage})

        if count:
            pipeline.append({"$sort": {"count": -1}})

        # Limit results
        if limit:
            pipeline.append({"$limit": limit})

        results = await self.aggregate(pipeline)

        # Rename _id to the field name for clarity
        for result in results:
            result[field] = result.pop("_id")

        return results

    async def get_distinct_counts(
        self, field: str, *, query: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        distinct = await self.collection.distinct(field, query or {})

        total = await self.collection.count_documents(query or {})

        return {
            "field": field,
            "distinct_count": len(distinct),
            "total_documents": total,
            "cardinality_ratio": len(distinct) / total if total > 0 else 0,
            "sample_values": distinct[:10] if len(distinct) <= 100 else [],
        }

    async def get_date_histogram(
        self, date_field: str, *, interval: str = "day", query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        interval_formats = {"day": "%Y-%m-%d", "week": "%Y-W%V", "month": "%Y-%m", "year": "%Y"}

        format_str = interval_formats.get(interval, "%Y-%m-%d")

        pipeline: list[dict[str, Any]] = []

        if query:
            pipeline.append({"$match": query})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": {"$dateToString": {"format": format_str, "date": f"${date_field}"}},
                        "count": {"$sum": 1},
                    }
                },
                {"$sort": {"_id": 1}},
                {"$project": {"_id": 0, "date": "$_id", "count": 1}},
            ]
        )

        return await self.aggregate(pipeline)

    async def get_top_values(
        self, field: str, *, limit: int = 10, query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return await self.group_by(field, query=query, limit=limit)
