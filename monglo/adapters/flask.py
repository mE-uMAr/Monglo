
from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint, jsonify, request

if TYPE_CHECKING:
    from ..core.engine import MongloEngine

def create_flask_blueprint(
    engine: MongloEngine,
    name: str = "monglo_api",
    url_prefix: str = "/api/admin"
) -> Blueprint:
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    
    # ==================== COLLECTIONS LIST ====================
    
    @bp.route("/", methods=["GET"])
    async def list_collections():
        collections = []
        
        for name, admin in engine.registry._collections.items():
            count = await admin.collection.count_documents({})
            collections.append({
                "name": name,
                "display_name": admin.display_name,
                "count": count,
                "relationships": len(admin.relationships)
            })
        
        return jsonify({"collections": collections})
    
    # ==================== COLLECTION ROUTES (Auto-generated for each) ====================
    
    @bp.route("/<collection>", methods=["GET"])
    async def list_documents(collection: str):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        search = request.args.get("search", "")
        sort_by = request.args.get("sort_by", "")
        sort_dir = request.args.get("sort_dir", "asc")
        
        admin = engine.registry.get(collection)
        
        sort_list = None
        if sort_by:
            sort_list = [(sort_by, -1 if sort_dir == "desc" else 1)]
        
        crud = CRUDOperations(admin)
        data = await crud.list(
            page=page,
            per_page=per_page,
            search=search if search else None,
            sort=sort_list
        )
        
        # Serialize
        serializer = JSONSerializer()
        serialized_items = [serializer._serialize_value(item) for item in data["items"]]
        
        return jsonify({
            **data,
            "items": serialized_items
        })
    
    @bp.route("/<collection>/<id>", methods=["GET"])
    async def get_document(collection: str, id: str):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            document = await crud.get(id)
        except KeyError:
            return jsonify({"error": "Document not found"}), 404
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(document)
        
        return jsonify({"document": serialized})
    
    @bp.route("/<collection>", methods=["POST"])
    async def create_document(collection: str):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        data = request.get_json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        created = await crud.create(data)
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(created)
        
        return jsonify({"success": True, "document": serialized}), 201
    
    @bp.route("/<collection>/<id>", methods=["PUT"])
    async def update_document(collection: str, id: str):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        data = request.get_json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            updated = await crud.update(id, data)
        except KeyError:
            return jsonify({"error": "Document not found"}), 404
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(updated)
        
        return jsonify({"success": True, "document": serialized})
    
    @bp.route("/<collection>/<id>", methods=["DELETE"])
    async def delete_document(collection: str, id: str):
        from ..operations.crud import CRUDOperations
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            await crud.delete(id)
        except KeyError:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({"success": True, "message": "Document deleted"})
    
    # ==================== VIEW CONFIGURATION ROUTES ====================
    
    @bp.route("/<collection>/config/table", methods=["GET"])
    async def get_table_config(collection: str):
        from ..views.table_view import TableView
        
        admin = engine.registry.get(collection)
        view = TableView(admin)
        config = view.render_config()
        
        return jsonify({"config": config})
    
    @bp.route("/<collection>/config/document", methods=["GET"])
    async def get_document_config(collection: str):
        from ..views.document_view import DocumentView
        
        admin = engine.registry.get(collection)
        view = DocumentView(admin)
        config = view.render_config()
        
        return jsonify({"config": config})
    
    @bp.route("/<collection>/relationships", methods=["GET"])
    async def get_relationships(collection: str):
        admin = engine.registry.get(collection)
        
        relationships = [
            {
                "source_field": rel.source_field,
                "target_collection": rel.target_collection,
                "type": rel.type.value
            }
            for rel in admin.relationships
        ]
        
        return jsonify({"relationships": relationships})
    
    return bp
