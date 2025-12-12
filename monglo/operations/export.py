
from __future__ import annotations

import csv
import json
from datetime import date, datetime
from io import StringIO
from typing import Any, Literal

from bson import ObjectId

class ExportOperations:

    def to_json(
        self, documents: list[dict[str, Any]], *, pretty: bool = False, ensure_ascii: bool = False
    ) -> str:
        # Serialize documents
        serialized = [self._serialize_document(doc) for doc in documents]

        indent = 2 if pretty else None
        return json.dumps(serialized, indent=indent, ensure_ascii=ensure_ascii, default=str)

    def to_csv(
        self,
        documents: list[dict[str, Any]],
        *,
        fields: list[str] | None = None,
        include_headers: bool = True,
    ) -> str:
        if not documents:
            return ""

        # Determine fields
        if fields is None:
            fields = list(documents[0].keys())

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)

        if include_headers:
            writer.writeheader()

        # Write rows
        for doc in documents:
            # Serialize and filter fields
            serialized = self._serialize_document(doc)
            row = {field: serialized.get(field, "") for field in fields}
            writer.writerow(row)

        return output.getvalue()

    def to_ndjson(self, documents: list[dict[str, Any]]) -> str:
        lines = []
        for doc in documents:
            serialized = self._serialize_document(doc)
            lines.append(json.dumps(serialized, default=str))

        return "\n".join(lines)

    def _serialize_document(self, doc: dict[str, Any]) -> dict[str, Any]:
        serialized = {}

        for key, value in doc.items():
            serialized[key] = self._serialize_value(value)

        return serialized

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, dict):
            return self._serialize_document(value)
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, bytes):
            return value.hex()  # Convert binary to hex string
        else:
            return value

class ExportFormat:

    JSON = "json"
    CSV = "csv"
    NDJSON = "ndjson"

async def export_collection(
    collection,
    *,
    format: Literal["json", "csv", "ndjson"] = "json",
    query: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    limit: int | None = None,
    **kwargs,
) -> str:
    cursor = collection.find(query or {})

    if limit:
        cursor = cursor.limit(limit)

    documents = await cursor.to_list(limit or 0)

    # Export
    exporter = ExportOperations()

    if format == "json":
        return exporter.to_json(documents, **kwargs)
    elif format == "csv":
        return exporter.to_csv(documents, fields=fields, **kwargs)
    elif format == "ndjson":
        return exporter.to_ndjson(documents)
    else:
        raise ValueError(f"Unsupported export format: {format}")
