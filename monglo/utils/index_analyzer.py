
from __future__ import annotations

from typing import Any
from collections import defaultdict

class IndexAnalyzer:
    
    def __init__(self, database):
        self.db = database
        self.query_stats = defaultdict(lambda: defaultdict(int))
    
    async def analyze_collection(self, collection_name: str) -> list[dict[str, Any]]:
        collection = self.db[collection_name]
        recommendations = []
        
        existing_indexes = await self._get_existing_indexes(collection)
        existing_fields = self._extract_indexed_fields(existing_indexes)
        
        if collection_name in self.query_stats:
            for field, count in self.query_stats[collection_name].items():
                if field not in existing_fields and count > 5:
                    recommendations.append({
                        "fields": [field],
                        "type": "single",
                        "reason": f"Frequently queried ({count} times)",
                        "priority": "high" if count > 20 else "medium"
                    })
        
        stats = await collection.aggregate([
            {"$collStats": {"storageStats": {}}}
        ]).to_list(1)
        
        if stats:
            storage_stats = stats[0].get("storageStats", {})
            doc_count = storage_stats.get("count", 0)
            
            # For large collections, recommend indexes on common patterns
            if doc_count > 10000:
                # Recommend index on _id if doing sorts/ranges (already exists by default)
                pass
            
            # Sample documents to find common fields
            sample_docs = await collection.find().limit(100).to_list(100)
            common_fields = self._find_common_fields(sample_docs)
            
            for field in common_fields:
                if field != "_id" and field not in existing_fields:
                    recommendations.append({
                        "fields": [field],
                        "type": "single",
                        "reason": f"Common field in {len(sample_docs)} documents",
                        "priority": "low"
                    })
        
        return recommendations
    
    async def _get_existing_indexes(self, collection) -> list[dict]:
        indexes = []
        async for index in collection.list_indexes():
            indexes.append(index)
        return indexes
    
    def _extract_indexed_fields(self, indexes: list[dict]) -> set[str]:
        fields = set()
        for index in indexes:
            key = index.get("key", {})
            fields.update(key.keys())
        return fields
    
    def _find_common_fields(self, documents: list[dict]) -> list[str]:
        if not documents:
            return []
        
        field_counts = defaultdict(int)
        for doc in documents:
            for field in doc.keys():
                field_counts[field] += 1
        
        threshold = len(documents) * 0.8
        common_fields = [
            field for field, count in field_counts.items()
            if count >= threshold
        ]
        
        return common_fields
    
    def track_query(self, collection_name: str, filter_dict: dict) -> None:
        for field in filter_dict.keys():
            # Skip operators
            if not field.startswith("$"):
                self.query_stats[collection_name][field] += 1
    
    async def get_slow_queries(self, collection_name: str) -> list[dict]:
        try:
            slow_queries = await self.db.system.profile.find({
                "ns": f"{self.db.name}.{collection_name}",
                "millis": {"$gt": 100}  # Queries taking > 100ms
            }).sort("millis", -1).limit(10).to_list(10)
            
            return slow_queries
        except:
            # Profiler might not be enabled
            return []
    
    async def suggest_compound_indexes(
        self,
        collection_name: str
    ) -> list[dict[str, Any]]:
        recommendations = []
        
        if collection_name in self.query_stats:
            field_pairs = defaultdict(int)
            
            # This is simplified - in reality, you'd track actual query combinations
            # For now, suggest common combinations
            stats = self.query_stats[collection_name]
            fields = list(stats.keys())
            
            # Suggest index on frequently used field combinations
            if len(fields) >= 2:
                sorted_fields = sorted(fields, key=lambda f: stats[f], reverse=True)
                
                # Recommend compound index on top 2 fields
                if len(sorted_fields) >= 2:
                    recommendations.append({
                        "fields": sorted_fields[:2],
                        "type": "compound",
                        "reason": "Frequently queried together",
                        "priority": "medium"
                    })
        
        return recommendations
    
    def get_index_stats_summary(self) -> dict[str, Any]:
        summary = {}
        for collection, field_stats in self.query_stats.items():
            summary[collection] = {
                "total_queries": sum(field_stats.values()),
                "most_queried_field": max(field_stats.items(), key=lambda x: x[1])[0] if field_stats else None,
                "field_count": len(field_stats)
            }
        return summary
