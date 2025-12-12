
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

if TYPE_CHECKING:
    from ..core.engine import MongloEngine

UI_DIR = Path(__file__).parent.parent.parent / "monglo_ui"
STATIC_DIR = UI_DIR / "static"
TEMPLATES_DIR = UI_DIR / "templates"

def create_ui_router(
    engine: MongloEngine,
    prefix: str = "/admin",
    title: str = "Monglo Admin",
    logo: str | None = None,
    brand_color: str = "#10b981",  # Green
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=["Monglo Admin UI"])
    
    # Setup Jinja2 templates with all filters
    templates = _setup_templates()
    
    # Mount static files
    router.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="admin_static")
    
    # ==================== UI ROUTES ====================
    
    @router.get("/", response_class=HTMLResponse, name="admin_home")
    async def admin_home(request: Request):
        collections = []
        
        for name, admin in engine.registry._collections.items():
            count = await admin.collection.count_documents({})
            collections.append({
                "name": name,
                "display_name": admin.display_name,
                "count": count,
                "relationships": len(admin.relationships)
            })
        
        return templates.TemplateResponse("admin_home.html", {
            "request": request,
            "title": title,
            "logo": logo,
            "brand_color": brand_color,
            "collections": collections,
            "current_collection": None
        })
    
    @router.get("/{collection}", response_class=HTMLResponse, name="table_view")
    async def table_view(
        request: Request,
        collection: str,
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        search: Optional[str] = None,
        sort: Optional[str] = None
    ):
        from ..views.table_view import TableView
        from ..operations.crud import CRUDOperations
        
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
        
        table_view_obj = TableView(admin)
        config = table_view_obj.render_config()
        
        collections = await _get_all_collections(engine)
        
        return templates.TemplateResponse("table_view.html", {
            "request": request,
            "title": title,
            "logo": logo,
            "brand_color": brand_color,
            "collection": admin,
            "config": config,
            "data": data,
            "collections": collections,
            "current_collection": collection
        })
    
    @router.get("/{collection}/document/{id}", response_class=HTMLResponse, name="document_view")
    async def document_view(
        request: Request,
        collection: str,
        id: str
    ):
        from ..views.document_view import DocumentView
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        admin = engine.registry.get(collection)
        
        crud = CRUDOperations(admin)
        try:
            document = await crud.get(id)
        except KeyError:
            # Document not found
            return RedirectResponse(url=f"{prefix}/{collection}", status_code=302)
        
        # Serialize for template safety
        serializer = JSONSerializer()
        serialized_doc = serializer._serialize_value(document)
        
        doc_view = DocumentView(admin)
        config = doc_view.render_config()
        
        collections = await _get_all_collections(engine)
        
        return templates.TemplateResponse("document_view.html", {
            "request": request,
            "title": title,
            "logo": logo,
            "brand_color": brand_color,
            "collection": admin,
            "document": serialized_doc,
            "config": config,
            "relationships": admin.relationships,
            "collections": collections,
            "current_collection": collection
        })
    
    # ==================== API ROUTES (for UI interactions) ====================
    
    @router.delete("/{collection}/{id}", name="delete_document")
    async def delete_document(collection: str, id: str):
        from ..operations.crud import CRUDOperations
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        await crud.delete(id)
        return {"success": True, "message": "Document deleted"}
    
    @router.put("/{collection}/{id}", name="update_document")
    async def update_document(collection: str, id: str, data: dict):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        updated = await crud.update(id, data)
        
        # Serialize for JSON response
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(updated)
        
        return {"success": True, "document": serialized}
    
    @router.post("/{collection}", name="create_document")
    async def create_document(collection: str, data: dict):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        created = await crud.create(data)
        
        # Serialize for JSON response
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(created)
        
        return {"success": True, "document": serialized}
    
    return router

def _setup_templates() -> Jinja2Templates:
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    
    def format_datetime(value):
        if value is None:
            return ""
        from datetime import datetime
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)
    
    def type_class(value):
        if isinstance(value, str):
            return "string"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, dict):
            return "object"
        elif isinstance(value, list):
            return "array"
        return ""
    
    def truncate(s, length=50):
        if not isinstance(s, str):
            s = str(s)
        return s[:length] + '...' if len(s) > length else s
    
    templates.env.filters['format_datetime'] = format_datetime
    templates.env.filters['type_class'] = type_class
    templates.env.filters['str'] = str
    templates.env.filters['truncate'] = truncate
    
    return templates

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
