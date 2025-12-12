
from typing import Any

from ..core.registry import CollectionAdmin
from .base import BaseView

class RelationshipView(BaseView):

    def __init__(self, collection_admin: CollectionAdmin):
        self.collection = collection_admin
        self.engine = None  # Will be set by adapter if needed

    def render_config(self) -> dict[str, Any]:
        return {
            "type": "graph",
            "collection": self.collection.name,
            "nodes": self._build_nodes(),
            "edges": self._build_edges(),
            "layout": "force-directed",
            "options": {"nodeRadius": 30, "linkDistance": 150, "charge": -300, "gravity": 0.1},
        }

    def _build_nodes(self) -> list[dict[str, Any]]:
        nodes = []

        nodes.append(
            {
                "id": self.collection.name,
                "label": self.collection.display_name,
                "type": "collection",
                "primary": True,
                "relationshipCount": len(self.collection.relationships),
            }
        )

        related_collections = set()
        for rel in self.collection.relationships:
            if rel.target_collection not in related_collections:
                related_collections.add(rel.target_collection)
                nodes.append(
                    {
                        "id": rel.target_collection,
                        "label": rel.target_collection.replace("_", " ").title(),
                        "type": "collection",
                        "primary": False,
                    }
                )

        return nodes

    def _build_edges(self) -> list[dict[str, Any]]:
        edges = []

        for rel in self.collection.relationships:
            edges.append(
                {
                    "source": rel.source_collection,
                    "target": rel.target_collection,
                    "label": rel.source_field,
                    "type": rel.type.value,
                    "bidirectional": rel.reverse_name is not None,
                    "reverseName": rel.reverse_name,
                }
            )

        return edges

    def render_full_graph(self, all_collections: dict[str, CollectionAdmin]) -> dict[str, Any]:
        all_nodes = []
        all_edges = []
        seen_edges = set()

        for name, admin in all_collections.items():
            all_nodes.append(
                {
                    "id": name,
                    "label": admin.display_name,
                    "type": "collection",
                    "relationshipCount": len(admin.relationships),
                }
            )

        for _name, admin in all_collections.items():
            for rel in admin.relationships:
                edge_id = f"{rel.source_collection}:{rel.source_field}:{rel.target_collection}"

                if edge_id not in seen_edges:
                    seen_edges.add(edge_id)
                    all_edges.append(
                        {
                            "source": rel.source_collection,
                            "target": rel.target_collection,
                            "label": rel.source_field,
                            "type": rel.type.value,
                            "bidirectional": rel.reverse_name is not None,
                        }
                    )

        return {
            "type": "graph",
            "scope": "database",
            "nodes": all_nodes,
            "edges": all_edges,
            "layout": "force-directed",
            "options": {"nodeRadius": 40, "linkDistance": 200, "charge": -500, "gravity": 0.05},
        }
