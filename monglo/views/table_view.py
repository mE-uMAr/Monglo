"""
Table view configuration generator.

Generates configuration for table/grid display of collection documents.
"""

from __future__ import annotations

from typing import Any

from .base import BaseView, ViewType, ViewUtilities


class TableView(BaseView):
    """Generate table view configuration for a collection.
    
    Creates configuration for displaying documents in a table/grid layout
    with columns, filters, sorting, and actions.
    
    Example:
        >>> table_view = TableView(collection_admin)
        >>> config = table_view.render_config()
        >>> # Returns table configuration with columns, filters, actions
    """
    
    def render_config(self) -> dict[str, Any]:
        """Generate table view configuration.
        
        Returns:
            Table view configuration dictionary
        """
        # Use configured list_fields or default to _id
        list_fields = self.config.list_fields or ["_id"]
        
        # Build columns from list_fields
        columns = self._build_columns(list_fields)
        
        # Build filter configurations
        filters = self._build_filters()
        
        # Get sort configuration
        sort_config = self._build_sort_config()
        
        # Build action definitions
        actions = self._build_actions()
        
        return {
            "type": ViewType.TABLE.value,
            "collection": self.admin.name,
            "display_name": self.admin.display_name,
            "columns": columns,
            "filters": filters,
            "sort": sort_config,
            "actions": actions["row_actions"],
            "bulk_actions": actions["bulk_actions"],
            "pagination": {
                "style": self.config.pagination_config.get("style", "offset"),
                "per_page": self.config.table_view.per_page,
                "max_per_page": self.config.pagination_config.get("max_per_page", 100)
            },
            "enable_search": bool(self.config.search_fields),
            "search_fields": self.config.search_fields or [],
            "enable_export": self.config.table_view.enable_export
        }
    
    def _build_columns(self, fields: list[str]) -> list[dict[str, Any]]:
        """Build column definitions.
        
        Args:
            fields: List of field names
            
        Returns:
            List of column configurations
        """
        columns = []
        
        for field in fields:
            # Detect field type (would come from schema in real usage)
            field_type = "string"  # Default
            
            column = {
                "field": field,
                "label": self.get_display_label(field),
                "sortable": field in (self.config.sortable_fields or []),
                "width": ViewUtilities.get_default_width(field_type)
            }
            
            # Add formatter if applicable
            formatter = ViewUtilities.get_formatter_for_type(field_type)
            if formatter:
                column["formatter"] = formatter
            
            columns.append(column)
        
        return columns
    
    def _build_filters(self) -> list[dict[str, Any]]:
        """Build filter UI configurations.
        
        Returns:
            List of filter configurations
        """
        filters = []
        
        for filter_config in self.config.filters:
            filter_def = {
                "field": filter_config.field,
                "type": filter_config.type,
                "label": filter_config.label or self.get_display_label(filter_config.field)
            }
            
            # Add options if available
            if filter_config.options:
                filter_def["options"] = filter_config.options
            
            filters.append(filter_def)
        
        return filters
    
    def _build_sort_config(self) -> dict[str, Any]:
        """Build sort configuration.
        
        Returns:
            Sort configuration
        """
        return {
            "default": self.config.table_view.default_sort,
            "sortable_fields": self.config.sortable_fields or []
        }
    
    def _build_actions(self) -> dict[str, list[str]]:
        """Build action configurations.
        
        Returns:
            Dictionary with row_actions and bulk_actions
        """
        return {
            "row_actions": self.config.table_view.row_actions,
            "bulk_actions": self.config.bulk_actions
        }
