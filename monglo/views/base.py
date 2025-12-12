
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from ..core.registry import CollectionAdmin

class ViewType(Enum):

    TABLE = "table"
    DOCUMENT = "document"
    RELATIONSHIP = "relationship"

class BaseView(ABC):

    def __init__(self, admin: CollectionAdmin) -> None:
        self.admin = admin
        self.config = admin.config
        self.collection = admin.collection

    @abstractmethod
    def render_config(self) -> dict[str, Any]:
        pass

    def get_field_type(self, field: str, schema: dict[str, Any]) -> str:
        if field in schema:
            return schema[field].get("type", "string")
        return "string"

    def is_readonly_field(self, field: str) -> bool:
        # _id is always readonly
        if field == "_id":
            return True

        if field in self.config.document_view.readonly_fields:
            return True

        return False

    def get_display_label(self, field: str) -> str:
        return field.replace("_", " ").title()

class ViewUtilities:

    @staticmethod
    def get_widget_for_type(field_type: str, readonly: bool = False) -> str:
        if readonly:
            return "readonly"

        widget_map = {
            "string": "text",
            "integer": "number",
            "number": "number",
            "boolean": "checkbox",
            "datetime": "datetime",
            "date": "date",
            "objectid": "text",
            "array": "array",
            "embedded": "embedded",
        }

        return widget_map.get(field_type, "text")

    @staticmethod
    def get_formatter_for_type(field_type: str) -> str | None:
        formatter_map = {
            "datetime": "datetime",
            "date": "date",
            "objectid": "objectid",
            "boolean": "boolean",
            "number": "number",
        }

        return formatter_map.get(field_type)

    @staticmethod
    def is_sortable_type(field_type: str) -> bool:
        sortable_types = {"string", "integer", "number", "datetime", "date", "boolean"}
        return field_type in sortable_types

    @staticmethod
    def is_filterable_type(field_type: str) -> bool:
        # Most types are filterable, except embedded and arrays
        non_filterable = {"embedded", "array"}
        return field_type not in non_filterable

    @staticmethod
    def get_default_width(field_type: str) -> int:
        width_map = {
            "string": 200,
            "integer": 100,
            "number": 100,
            "boolean": 80,
            "datetime": 180,
            "date": 120,
            "objectid": 220,
        }

        return width_map.get(field_type, 150)
