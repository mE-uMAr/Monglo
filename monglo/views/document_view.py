
from __future__ import annotations

from typing import Any

from .base import BaseView, ViewType, ViewUtilities

class DocumentView(BaseView):

    def render_config(self, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        schema = schema or {}

        fields = self._build_fields(schema)

        relationships = self._build_relationships()

        return {
            "type": ViewType.DOCUMENT.value,
            "collection": self.admin.name,
            "display_name": self.admin.display_name,
            "layout": self.config.document_view.layout,
            "fields": fields,
            "relationships": relationships,
            "readonly_fields": list(self.config.document_view.readonly_fields),
            "enable_relationships": self.config.document_view.enable_relationships,
            "relationship_depth": self.config.document_view.relationship_depth,
        }

    def _build_fields(self, schema: dict[str, Any]) -> list[dict[str, Any]]:
        fields = []

        # If no schema, use list_fields as default
        field_names = list(schema.keys()) if schema else (self.config.list_fields or ["_id"])

        for field_name in field_names:
            # Skip nested fields (contain dots)
            if "." in field_name:
                continue

            field_type = self.get_field_type(field_name, schema)
            is_readonly = self.is_readonly_field(field_name)

            field_config = {
                "path": field_name,
                "type": field_type,
                "label": self.get_display_label(field_name),
                "widget": ViewUtilities.get_widget_for_type(field_type, is_readonly),
                "readonly": is_readonly,
                "required": field_name == "_id",  # Only _id is required by default
            }

            if field_type == "embedded" and field_name in schema:
                nested_fields = self._build_nested_fields(field_name, schema)
                if nested_fields:
                    field_config["fields"] = nested_fields

            fields.append(field_config)

        return fields

    def _build_nested_fields(
        self, parent_field: str, schema: dict[str, Any]
    ) -> list[dict[str, Any]]:
        nested_fields = []
        prefix = f"{parent_field}."

        for field_name, field_info in schema.items():
            if (
                field_name.startswith(prefix)
                and field_name.count(".") == parent_field.count(".") + 1
            ):
                # This is a direct child
                nested_name = field_name[len(prefix) :]
                field_type = field_info.get("type", "string")

                nested_field = {
                    "path": nested_name,
                    "type": field_type,
                    "label": self.get_display_label(nested_name),
                    "widget": ViewUtilities.get_widget_for_type(field_type, False),
                }

                nested_fields.append(nested_field)

        return nested_fields

    def _build_relationships(self) -> list[dict[str, Any]]:
        relationships = []

        for rel in self.config.relationships:
            rel_config = {
                "field": rel.source_field,
                "collection": rel.target_collection,
                "type": rel.type.value,
                "target_field": rel.target_field,
            }

            if rel.reverse_name:
                rel_config["reverse_name"] = rel.reverse_name

            relationships.append(rel_config)

        return relationships
