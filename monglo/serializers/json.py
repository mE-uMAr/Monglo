
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from bson import Binary, DBRef, ObjectId

class JSONSerializer:

    def serialize(self, data: Any, *, pretty: bool = False) -> str:
        serialized = self._serialize_value(data)
        indent = 2 if pretty else None
        return json.dumps(serialized, indent=indent, ensure_ascii=False)

    def serialize_many(self, documents: list[dict[str, Any]], *, pretty: bool = False) -> str:
        return self.serialize(documents, pretty=pretty)

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Binary):
            return value.hex()
        elif isinstance(value, DBRef):
            return {"$ref": value.collection, "$id": str(value.id), "$db": value.database}
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, bytes):
            return value.hex()
        else:
            return value
