
from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

if TYPE_CHECKING:
    from ..core.engine import MongloEngine

def create_starlette_routes(
    engine: MongloEngine,
    prefix: str = "/api/admin"
) -> list:
    
    # ==================== COLLECTIONS LIST ====================
    
    async def list_collections(request):
        collections = []
        
        for name, admin in engine.registry._collections.items():
            count = await admin.collection.count_documents({})
            collections.append({
                "name": name,
                "display_name": admin.display_name,
                "count": count,
                "relationships": len(admin.relationships)
            })
        
        return JSONResponse({"collections": collections})
    
    # ==================== COLLECTION ROUTES ====================
    
    async def list_documents(request):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        collection = request.path_params["collection"]
        
        page = int(request.query_params.get("page", 1))
        per_page = int(request.query_params.get("per_page", 20))
        search = request.query_params.get("search", "")
        sort_by = request.query_params.get("sort_by", "")
        sort_dir = request.query_params.get("sort_dir", "asc")
        
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
        
        return JSONResponse({
            **data,
            "items": serialized_items
        })
    
    async def get_document(request):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        collection = request.path_params["collection"]
        doc_id = request.path_params["id"]
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            document = await crud.get(doc_id)
        except KeyError:
            return JSONResponse({"error": "Document not found"}, status_code=404)
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(document)
        
        return JSONResponse({"document": serialized})
    
    async def create_document(request):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        collection = request.path_params["collection"]
        data = await request.json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        created = await crud.create(data)
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(created)
        
        return JSONResponse({"success": True, "document": serialized}, status_code=201)
    
    async def update_document(request):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        collection = request.path_params["collection"]
        doc_id = request.path_params["id"]
        data = await request.json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            updated = await crud.update(doc_id, data)
        except KeyError:
            return JSONResponse({"error": "Document not found"}, status_code=404)
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(updated)
        
        return JSONResponse({"success": True, "document": serialized})
    
    async def delete_document(request):
        from ..operations.crud import CRUDOperations
        
        collection = request.path_params["collection"]
        doc_id = request.path_params["id"]
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            await crud.delete(doc_id)
        except KeyError:
            return JSONResponse({"error": "Document not found"}, status_code=404)
        
        return JSONResponse({"success": True, "message": "Document deleted"})
    
    # ==================== VIEW CONFIGURATION ROUTES ====================
    
    async def get_table_config(request):
        from ..views.table_view import TableView
        
        collection = request.path_params["collection"]
        admin = engine.registry.get(collection)
        view = TableView(admin)
        config = view.render_config()
        
        return JSONResponse({"config": config})
    
    async def get_document_config(request):
        from ..views.document_view import DocumentView
        
        collection = request.path_params["collection"]
        admin = engine.registry.get(collection)
        view = DocumentView(admin)
        config = view.render_config()
        
        return JSONResponse({"config": config})
    
    async def get_relationships(request):
        collection = request.path_params["collection"]
        admin = engine.registry.get(collection)
        
        relationships = [
            {
                "source_field": rel.source_field,
                "target_collection": rel.target_collection,
                "type": rel.type.value
            }
            for rel in admin.relationships
        ]
        
        return JSONResponse({"relationships": relationships})
    
    # ==================== CREATE ROUTES ====================
    
    routes = [
        Route(f"{prefix}/", list_collections, methods=["GET"]),
        Route(f"{prefix}/{{collection}}", list_documents, methods=["GET"]),
        Route(f"{prefix}/{{collection}}", create_document, methods=["POST"]),
        Route(f"{prefix}/{{collection}}/{{id}}", get_document, methods=["GET"]),
        Route(f"{prefix}/{{collection}}/{{id}}", update_document, methods=["PUT"]),
        Route(f"{prefix}/{{collection}}/{{id}}", delete_document, methods=["DELETE"]),
        Route(f"{prefix}/{{collection}}/config/table", get_table_config, methods=["GET"]),
        Route(f"{prefix}/{{collection}}/config/document", get_document_config, methods=["GET"]),
        Route(f"{prefix}/{{collection}}/relationships", get_relationships, methods=["GET"]),
    ]
    
    return routes
