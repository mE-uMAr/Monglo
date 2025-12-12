
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.views import View

if TYPE_CHECKING:
    from ..core.engine import MongloEngine

UI_DIR = Path(__file__).parent.parent.parent / "monglo_ui"
TEMPLATES_DIR = UI_DIR / "templates"

def create_ui_urlpatterns(
    engine: MongloEngine,
    prefix: str = "admin",
    title: str = "Monglo Admin",
    logo: str | None = None,
    brand_color: str = "#10b981",
):
    
    class AdminHomeView(View):
        async def get(self, request):
            collections = []
            
            for name, admin in engine.registry._collections.items():
                count = await admin.collection.count_documents({})
                collections.append({
                    "name": name,
                    "display_name": admin.display_name,
                    "count": count,
                    "relationships": len(admin.relationships)
                })
            
            context = {
                "title": title,
                "logo": logo,
                "brand_color": brand_color,
                "collections": collections,
                "current_collection": None
            }
            
            return render(request, str(TEMPLATES_DIR / "admin_home.html"), context)
    
    class TableViewClass(View):
        async def get(self, request, collection):
            from ..views.table_view import TableView
            from ..operations.crud import CRUDOperations
            
            page = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 20))
            search = request.GET.get("search", "")
            sort = request.GET.get("sort", "")
            
            admin = engine.registry.get(collection)
            
            sort_list = None
            if sort:
                field, direction = sort.split(":")
                sort_list = [(field, -1 if direction == "desc" else 1)]
            
            crud = CRUDOperations(admin)
            data = await crud.list(
                page=page,
                per_page=per_page,
                search=search if search else None,
                sort=sort_list
            )
            
            table_view = TableView(admin)
            config = table_view.render_config()
            
            collections = await _get_all_collections(engine)
            
            context = {
                "title": title,
                "logo": logo,
                "brand_color": brand_color,
                "collection": admin,
                "config": config,
                "data": data,
                "collections": collections,
                "current_collection": collection
            }
            
            return render(request, str(TEMPLATES_DIR / "table_view.html"), context)
    
    class DocumentViewClass(View):
        async def get(self, request, collection, id):
            from ..views.document_view import DocumentView
            from ..operations.crud import CRUDOperations
            from ..serializers.json import JSONSerializer
            
            admin = engine.registry.get(collection)
            
            crud = CRUDOperations(admin)
            try:
                document = await crud.get(id)
            except KeyError:
                return redirect(f"/{prefix}/{collection}/")
            
            # Serialize
            serializer = JSONSerializer()
            serialized_doc = serializer._serialize_value(document)
            
            doc_view = DocumentView(admin)
            config = doc_view.render_config()
            
            collections = await _get_all_collections(engine)
            
            context = {
                "title": title,
                "logo": logo,
                "brand_color": brand_color,
                "collection": admin,
                "document": serialized_doc,
                "config": config,
                "relationships": admin.relationships,
                "collections": collections,
                "current_collection": collection
            }
            
            return render(request, str(TEMPLATES_DIR / "document_view.html"), context)
        
        async def put(self, request, collection, id):
            from ..operations.crud import CRUDOperations
            from ..serializers.json import JSONSerializer
            import json
            
            data = json.loads(request.body)
            
            admin = engine.registry.get(collection)
            crud = CRUDOperations(admin)
            
            updated = await crud.update(id, data)
            
            serializer = JSONSerializer()
            serialized = serializer._serialize_value(updated)
            
            return JsonResponse({"success": True, "document": serialized})
        
        async def delete(self, request, collection, id):
            from ..operations.crud import CRUDOperations
            
            admin = engine.registry.get(collection)
            crud = CRUDOperations(admin)
            
            await crud.delete(id)
            return JsonResponse({"success": True, "message": "Document deleted"})
    
    class CreateDocumentView(View):
        async def post(self, request, collection):
            from ..operations.crud import CRUDOperations
            from ..serializers.json import JSONSerializer
            import json
            
            data = json.loads(request.body)
            
            admin = engine.registry.get(collection)
            crud = CRUDOperations(admin)
            
            created = await crud.create(data)
            
            serializer = JSONSerializer()
            serialized = serializer._serialize_value(created)
            
            return JsonResponse({"success": True, "document": serialized})
    
    return [
        path(f"{prefix}/", AdminHomeView.as_view(), name="monglo_admin_home"),
        path(f"{prefix}/<str:collection>/", TableViewClass.as_view(), name="monglo_table_view"),
        path(f"{prefix}/<str:collection>/document/<str:id>/", DocumentViewClass.as_view(), name="monglo_document_view"),
        path(f"{prefix}/<str:collection>/create/", CreateDocumentView.as_view(), name="monglo_create_document"),
    ]

async def _get_all_collections(engine: MongloEngine) -> list[dict[str, Any]]:
    collections = []
    for name, admin in engine.registry._collections.items():
        count = await admin.collection.count_documents({})
        collections.append({
            "name": name,
            "display_name": admin.display_name,
            "count": count
        })
    return collections
