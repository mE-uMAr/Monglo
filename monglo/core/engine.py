from __future__ import annotations

from typing import Any, Literal

from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import CollectionConfig
from .introspection import SchemaIntrospector
from .registry import CollectionAdmin, CollectionRegistry
from .relationships import RelationshipDetector

class MongloEngine:

    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        *,
        auto_discover: bool = False,
        relationship_detection: Literal["auto", "manual", "off"] = "auto",
        excluded_collections: list[str] | None = None,
    ) -> None:
        self.db = database
        self._auto_discover = auto_discover
        self._relationship_detection = relationship_detection
        self._excluded_collections = set(excluded_collections or [])

        self.registry = CollectionRegistry()
        self.introspector = SchemaIntrospector(database)
        self.relationship_detector = RelationshipDetector(database)

        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        if self._auto_discover:
            await self._discover_collections()

        self._initialized = True

    async def register_collection(
        self, name: str, *, config: CollectionConfig | None = None
    ) -> CollectionAdmin:

        if name in self.registry:
            raise ValueError(f"Collection '{name}' is already registered")

        if config is None:
            schema = await self.introspector.introspect(name)
            config = CollectionConfig.from_schema(schema)
            config.name = name

        if not config.name:
            config.name = name

        relationships = []
        if self._relationship_detection in ["auto", "manual"]:
            if self._relationship_detection == "auto":
                relationships = await self.relationship_detector.detect(name, config)
            elif self._relationship_detection == "manual" and config.relationships:
                relationships = config.relationships

        collection_admin = CollectionAdmin(
            name=name, database=self.db, config=config, relationships=relationships
        )

        self.registry.register(collection_admin)

        return collection_admin

    async def unregister_collection(self, name: str) -> None:
        self.registry.unregister(name)

    async def _discover_collections(self) -> None:

        collection_names = await self.db.list_collection_names()

        system_prefixes = ("system.",)
        collections_to_register = [
            name
            for name in collection_names
            if not name.startswith(system_prefixes) and name not in self._excluded_collections
        ]

        for name in collections_to_register:
            try:
                await self.register_collection(name)
            except Exception as e:

                print(f"Warning: Failed to register collection '{name}': {e}")

    def get_adapter(self, framework: str):
        framework = framework.lower()

        if framework == "fastapi":
            from ..adapters.fastapi import FastAPIAdapter

            return FastAPIAdapter(self)
        elif framework == "flask":
            from ..adapters.flask import FlaskAdapter

            return FlaskAdapter(self)
        elif framework == "django":
            from ..adapters.django import DjangoAdapter

            return DjangoAdapter(self)
        elif framework == "starlette":
            from ..adapters.starlette import StarletteAdapter

            return StarletteAdapter(self)
        else:
            raise ValueError(
                f"Unsupported framework: {framework}. "
                f"Supported frameworks: fastapi, flask, django, starlette"
            )

    async def get_collection_stats(self) -> dict[str, Any]:
        stats = {"total_collections": len(self.registry), "collections": []}

        for name, admin in self.registry.items():
            count = await admin.collection.count_documents({})
            stats["collections"].append(
                {
                    "name": name,
                    "display_name": admin.display_name,
                    "document_count": count,
                    "relationship_count": len(admin.relationships),
                }
            )

        return stats

    async def refresh_collection(self, name: str) -> None:
        if name not in self.registry:
            raise KeyError(f"Collection '{name}' is not registered")

        await self.unregister_collection(name)
        await self.register_collection(name)
