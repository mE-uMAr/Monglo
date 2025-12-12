
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from bson import ObjectId

class TableSerializer:

    def __init__(self, columns: list[dict[str, Any]]) -> None:
        self.columns = columns

    def serialize_row(self, document: dict[str, Any]) -> dict[str, Any]:
        row = {}

        for column in self.columns:
            field = column["field"]
            value = self._get_field_value(document, field)

            # Apply formatter if specified
            formatter = column.get("formatter")
            if formatter:
                value = self._apply_formatter(value, formatter)

            row[field] = value

        return row

    def serialize_rows(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.serialize_row(doc) for doc in documents]

    def _get_field_value(self, document: dict[str, Any], field_path: str) -> Any:
        keys = field_path.split(".")
        value = document

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    break
            else:
                return None

        return value

    def _apply_formatter(self, value: Any, formatter: str) -> Any:
        if value is None:
            return None

        if formatter == "datetime":
            if isinstance(value, datetime):
                return value.isoformat()
        elif formatter == "date":
            if isinstance(value, (datetime, date)):
                return value.strftime("%Y-%m-%d")
        elif formatter == "objectid":
            if isinstance(value, ObjectId):
                return str(value)
        elif formatter == "boolean":
            return "Yes" if value else "No"
        elif formatter == "number":
            if isinstance(value, (int, float)):
                return f"{value:,.2f}" if isinstance(value, float) else str(value)

        return value
