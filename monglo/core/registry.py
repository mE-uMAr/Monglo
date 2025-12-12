
from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from .config import CollectionConfig
from .relationships import Relationship

@dataclass
class CollectionAdmin:

    name: str
    database: AsyncIOMotorDatabase
    config: CollectionConfig
    relationships: list[Relationship] = field(default_factory=list)

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self.database[self.name]

    @property
    def display_name(self) -> str:
        return self.config.display_name or self.name.replace("_", " ").title()

    def get_relationship(self, field: str) -> Relationship | None:
        for rel in self.relationships:
            if rel.source_field == field:
                return rel
        return None

class CollectionRegistry:

    def __init__(self) -> None:
        self._collections: dict[str, CollectionAdmin] = {}

    def register(self, admin: CollectionAdmin) -> None:
        if admin.name in self._collections:
            raise ValueError(f"Collection '{admin.name}' is already registered")
        self._collections[admin.name] = admin

    def unregister(self, name: str) -> None:
        self._collections.pop(name, None)

    def get(self, name: str) -> CollectionAdmin:
        if name not in self._collections:
            raise KeyError(f"Collection '{name}' is not registered")
        return self._collections[name]

    def get_all(self) -> list[CollectionAdmin]:
        return list(self._collections.values())

    def __contains__(self, name: str) -> bool:
        return name in self._collections

    def __iter__(self):
        return iter(self._collections)

    def __len__(self) -> int:
        return len(self._collections)

    def items(self):
        return self._collections.items()
