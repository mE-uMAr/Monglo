
from abc import ABC, abstractmethod
from typing import Any

from ..core.engine import MongloEngine

class BaseAdapter(ABC):

    def __init__(self, engine: MongloEngine, prefix: str = "/api/admin"):
        self.engine = engine
        self.prefix = prefix

    @abstractmethod
    def create_routes(self) -> Any:
        pass

    @abstractmethod
    async def list_collections_handler(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def list_documents_handler(
        self,
        collection: str,
        page: int,
        per_page: int,
        search: str | None,
        sort: str | None,
        filters: dict | None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_document_handler(self, collection: str, id: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def create_document_handler(
        self, collection: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def update_document_handler(
        self, collection: str, id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def delete_document_handler(self, collection: str, id: str) -> dict[str, Any]:
        pass

    def _serialize_document(self, doc: dict[str, Any]) -> dict[str, Any]:
        from ..serializers.json import JSONSerializer

        serializer = JSONSerializer()
        return serializer._serialize_value(doc)

    def _parse_sort(self, sort: str | None) -> list[tuple[str, int]] | None:
        if not sort:
            return None

        parts = sort.split(":")
        if len(parts) != 2:
            return None

        field, direction = parts
        return [(field, -1 if direction == "desc" else 1)]
