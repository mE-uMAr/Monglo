
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

class TableViewConfig(BaseModel):

    columns: list[dict[str, Any]] = Field(default_factory=list)
    default_sort: list[tuple[str, int]] = Field(default_factory=list)
    per_page: int = Field(default=20, ge=1, le=100)
    enable_bulk_actions: bool = True
    enable_export: bool = True
    row_actions: list[str] = Field(default_factory=lambda: ["view", "edit", "delete"])

class DocumentViewConfig(BaseModel):

    layout: Literal["tree", "form"] = "tree"
    fields: list[dict[str, Any]] = Field(default_factory=list)
    readonly_fields: list[str] = Field(default_factory=list)
    enable_relationships: bool = True
    relationship_depth: int = Field(default=1, ge=1, le=3)

class FilterConfig(BaseModel):

    field: str
    type: Literal["eq", "ne", "gt", "lt", "gte", "lte", "in", "regex", "range", "date_range"]
    label: str | None = None
    options: list[Any] | None = None

class CollectionConfig(BaseModel):

    # Basic metadata
    name: str | None = None
    display_name: str | None = None
    icon: str | None = None

    # Field configuration
    list_fields: list[str] | None = None
    search_fields: list[str] | None = None
    sortable_fields: list[str] | None = None

    # View configuration
    table_view: TableViewConfig = Field(default_factory=TableViewConfig)
    document_view: DocumentViewConfig = Field(default_factory=DocumentViewConfig)

    # Filters
    filters: list[FilterConfig] = Field(default_factory=list)

    # Relationships (will be populated by relationship detector)
    relationships: list[Any] = Field(default_factory=list)  # Will be Relationship objects

    # Actions
    actions: list[str] = Field(default_factory=lambda: ["create", "edit", "delete"])
    bulk_actions: list[str] = Field(default_factory=lambda: ["delete", "export"])
    custom_actions: list[Any] = Field(default_factory=list)

    # Permissions
    permissions: dict[str, list[str]] = Field(default_factory=dict)

    # Performance settings
    pagination_config: dict[str, Any] = Field(
        default_factory=lambda: {
            "style": "offset",  # or "cursor"
            "per_page": 20,
            "max_per_page": 100,
        }
    )

    @classmethod
    def from_schema(cls, schema: dict[str, Any]) -> CollectionConfig:
        # Extract string fields for searching
        string_fields = [field for field, info in schema.items() if info.get("type") == "string"][
            :5
        ]  # Max 5 search fields

        # Extract sortable fields (primitives and dates)
        sortable_types = {"string", "number", "datetime", "date"}
        sortable_fields = [
            field for field, info in schema.items() if info.get("type") in sortable_types
        ]

        # First 10 fields for list view
        list_fields = list(schema.keys())[:10]

        return cls(
            list_fields=list_fields, search_fields=string_fields, sortable_fields=sortable_fields
        )
