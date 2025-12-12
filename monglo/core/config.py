"""
Configuration models for Monglo.

This module provides Pydantic models for configuring collections, views, and filters.
All configuration is type-safe and validated at runtime.
"""

from typing import Any, Literal
from pydantic import BaseModel, Field


class TableViewConfig(BaseModel):
    """Configuration for table view display.
    
    The table view is optimized for browsing and filtering large collections
    in a spreadsheet-like interface.
    
    Attributes:
        columns: Column definitions with field names, widths, and formatters
        default_sort: Default sort order as list of (field, direction) tuples
        per_page: Number of items per page
        enable_bulk_actions: Whether to show bulk action checkboxes
        enable_export: Whether to show export button
        row_actions: Available actions for each row (view, edit, delete, etc.)
    
    Example:
        >>> config = TableViewConfig(
        ...     columns=[
        ...         {"field": "name", "width": 200, "sortable": True},
        ...         {"field": "email", "width": 250, "formatter": "email"}
        ...     ],
        ...     default_sort=[("created_at", -1)],
        ...     per_page=50
        ... )
    """
    
    columns: list[dict[str, Any]] = Field(default_factory=list)
    default_sort: list[tuple[str, int]] = Field(default_factory=list)
    per_page: int = Field(default=20, ge=1, le=100)
    enable_bulk_actions: bool = True
    enable_export: bool = True
    row_actions: list[str] = Field(default_factory=lambda: ["view", "edit", "delete"])


class DocumentViewConfig(BaseModel):
    """Configuration for document view display.
    
    The document view shows individual documents in either a tree or form layout,
    with full support for nested data and relationships.
    
    Attributes:
        layout: Display layout - 'tree' for JSON-like view, 'form' for form inputs
        fields: Field definitions for custom rendering
        readonly_fields: Fields that cannot be edited
        enable_relationships: Whether to show related documents
        relationship_depth: How many levels deep to resolve relationships (1-3)
    
    Example:
        >>> config = DocumentViewConfig(
        ...     layout="form",
        ...     readonly_fields=["_id", "created_at"],
        ...     enable_relationships=True,
        ...     relationship_depth=2
        ... )
    """
    
    layout: Literal["tree", "form"] = "tree"
    fields: list[dict[str, Any]] = Field(default_factory=list)
    readonly_fields: list[str] = Field(default_factory=list)
    enable_relationships: bool = True
    relationship_depth: int = Field(default=1, ge=1, le=3)


class FilterConfig(BaseModel):
    """Configuration for a single filter.
    
    Filters allow users to narrow down collections based on field values.
    
    Attributes:
        field: The field name to filter on
        type: Filter type (eq, ne, gt, lt, gte, lte, in, regex, range, date_range)
        label: Human-readable label for the filter
        options: Available options for select-style filters
    
    Example:
        >>> filter_config = FilterConfig(
        ...     field="status",
        ...     type="in",
        ...     label="Status",
        ...     options=["active", "inactive", "pending"]
        ... )
    """
    
    field: str
    type: Literal["eq", "ne", "gt", "lt", "gte", "lte", "in", "regex", "range", "date_range"]
    label: str | None = None
    options: list[Any] | None = None


class CollectionConfig(BaseModel):
    """Complete configuration for a MongoDB collection in Monglo.
    
    This is the main configuration model that controls all aspects of how
    a collection is displayed and interacted with in the admin interface.
    
    Attributes:
        name: Collection name (optional, defaults to registered name)
        display_name: Human-readable name for the collection
        icon: Icon identifier for UI display
        list_fields: Fields to display in table view
        search_fields: Fields to include in text search
        sortable_fields: Fields that can be sorted
        table_view: Table view configuration
        document_view: Document view configuration
        filters: Available filters for the collection
        relationships: Manual relationship definitions
        actions: Available actions (create, edit, delete, etc.)
        bulk_actions: Available bulk actions (delete, export, etc.)
        custom_actions: Custom action definitions
        permissions: Role-based permissions mapping
        pagination_config: Pagination strategy and settings
    
    Example:
        >>> config = CollectionConfig(
        ...     display_name="Users",
        ...     icon="user",
        ...     list_fields=["name", "email", "created_at"],
        ...     search_fields=["name", "email"],
        ...     table_view=TableViewConfig(per_page=50),
        ...     filters=[
        ...         FilterConfig(field="status", type="eq", label="Status")
        ...     ]
        ... )
    """
    
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
            "max_per_page": 100
        }
    )
    
    @classmethod
    def from_schema(cls, schema: dict[str, Any]) -> "CollectionConfig":
        """Create configuration from an introspected schema.
        
        This factory method generates sensible defaults based on the
        discovered schema structure.
        
        Args:
            schema: Schema dictionary from SchemaIntrospector
            
        Returns:
            CollectionConfig with auto-generated settings
            
        Example:
            >>> schema = {"name": {"type": "string"}, "age": {"type": "number"}}
            >>> config = CollectionConfig.from_schema(schema)
            >>> assert "name" in config.list_fields
        """
        # Extract string fields for searching
        string_fields = [
            field for field, info in schema.items()
            if info.get("type") == "string"
        ][:5]  # Max 5 search fields
        
        # Extract sortable fields (primitives and dates)
        sortable_types = {"string", "number", "datetime", "date"}
        sortable_fields = [
            field for field, info in schema.items()
            if info.get("type") in sortable_types
        ]
        
        # First 10 fields for list view
        list_fields = list(schema.keys())[:10]
        
        return cls(
            list_fields=list_fields,
            search_fields=string_fields,
            sortable_fields=sortable_fields
        )
