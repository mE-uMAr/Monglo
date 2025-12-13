
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware


if TYPE_CHECKING:
    from ..core.engine import MongloEngine

UI_DIR = Path(__file__).parent.parent.parent / "monglo_ui"
STATIC_DIR = UI_DIR / "static"
TEMPLATES_DIR = UI_DIR / "templates"

def setup_ui(
    app,
    engine: MongloEngine,
    prefix: str = "/admin",
    title: str = "Monglo Admin",
    logo: str | None = None,
    brand_color: str = "#10b981",
    auth_backend: Any | None = None,  # NEW: AuthenticationBackend instance
) -> None:
    """
    Setup Monglo UI on a FastAPI application.
    
    This automatically mounts static files and includes the UI router.
    Users don't need to manually configure anything.
    
    Args:
        app: FastAPI application instance
        engine: MongloEngine instance
        prefix: URL prefix for admin UI (default: "/admin")
        title: Page title
        logo: Optional logo URL
        brand_color: Brand color in hex
        auth_backend: Optional AuthenticationBackend instance for authentication
                     When provided, automatically sets up session middleware,
                     login/logout routes, and protects admin routes
    """
    # Setup session middleware if auth is enabled
    if auth_backend:
        # Add session middleware for auth
        app.add_middleware(SessionMiddleware, secret_key=auth_backend.secret_key)
        
        # Add 401 redirect middleware
        app.add_middleware(AuthRedirectMiddleware, prefix=prefix)
    
    # Mount static files on the main app
    app.mount(f"{prefix}/static", StaticFiles(directory=str(STATIC_DIR)), name="admin_static")
    
    # Include the UI router
    router = create_ui_router(engine, prefix, title, logo, brand_color, auth_backend)
    app.include_router(router)


class AuthRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect 401 errors to login page.
    Only active when authentication is enabled.
    """
    
    def __init__(self, app, prefix: str = "/admin"):
        super().__init__(app)
        self.prefix = prefix
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # If 401 and it's an admin request, redirect to login
        if response.status_code == 401:
            if request.url.path.startswith(self.prefix):
                # Check if it's not already the login page
                if "/login" not in request.url.path:
                    return RedirectResponse(url=f"{self.prefix}/login", status_code=303)
        
        return response



def create_ui_router(
    engine: MongloEngine,
    prefix: str = "/admin",
    title: str = "Monglo Admin",
    logo: str | None = None,
    brand_color: str = "#10b981", 
    auth_backend: Any | None = None, 
) -> APIRouter:
    from fastapi import Depends, HTTPException, status
    
    # Exclude admin routes from OpenAPI schema
    router = APIRouter(prefix=prefix, tags=["Monglo Admin UI"], include_in_schema=False)
    
    # Setup Jinja2 templates with all filters
    templates = _setup_templates()
    
    # Helper to conditionally apply auth dependency
    def get_dependencies():
        if auth_backend:
            return [Depends(create_auth_dependency(auth_backend))]
        return []
    
    # Built-in login/logout routes (if auth is enabled)
    if auth_backend:
        @router.get("/login", response_class=HTMLResponse, include_in_schema=False)
        async def login_page(request: Request, error: str = None):
            """Built-in login page"""
            return templates.TemplateResponse("login.html", {
                "request": request,
                "title": title,
                "logo": logo,
                "brand_color": brand_color,
                "prefix": prefix,
                "error": error
            })
        
        @router.post("/login", include_in_schema=False)
        async def handle_login(request: Request):
            """Built-in login handler using auth backend"""
            success = await auth_backend.login(request)
            
            if success:
                return RedirectResponse(url=f"{prefix}/", status_code=303)
            else:
                return RedirectResponse(
                    url=f"{prefix}/login?error=Invalid+credentials",
                    status_code=303
                )
        
        @router.get("/logout", include_in_schema=False)
        async def logout_route(request: Request):
            """Built-in logout route using auth backend"""
            await auth_backend.logout(request)
            return RedirectResponse(url=f"{prefix}/login", status_code=303)


    
    #  UI ROUTES 
    
    @router.get("/", response_class=HTMLResponse, name="admin_home", dependencies=get_dependencies(), include_in_schema=False)
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
            "current_collection": None,
            "prefix": prefix
        })
    
    @router.get("/relationships", response_class=HTMLResponse, name="relationship_graph", dependencies=get_dependencies(), include_in_schema=False)
    async def relationship_graph(request: Request):
        """Display relationship graph visualization"""
        # Collect all relationships across collections
        all_relationships = []
        for name, admin in engine.registry._collections.items():
            for rel in admin.relationships:
                all_relationships.append({
                    "source_collection": name,
                    "target_collection": rel.target_collection,
                    "source_field": rel.source_field,
                    "type": rel.type.value
                })
        
        collections = await _get_all_collections(engine)
        
        return templates.TemplateResponse("relationship_graph.html", {
            "request": request,
            "title": title,
            "logo": logo,
            "brand_color": brand_color,
            "relationships": all_relationships,
            "collections": collections,
            "current_collection": None,
            "prefix": prefix
        })
    
    @router.get("/{collection}", response_class=HTMLResponse, name="table_view", dependencies=get_dependencies(), include_in_schema=False)
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
            "current_collection": collection,
            "prefix": prefix
        })
    
    @router.get("/{collection}/document/{id}", response_class=HTMLResponse, name="document_view", dependencies=get_dependencies(), include_in_schema=False)
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
            "current_collection": collection,
            "prefix": prefix
        })
    
    
    #  API ROUTES (for UI interactions) 
    
    @router.get("/{collection}/{id}/json", name="get_document_json", dependencies=get_dependencies(), include_in_schema=False)
    async def get_document_json(collection: str, id: str):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        document = await crud.get(id)
        
        # Serialize for JSON response
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(document)
        
        return {" success": True, "document": serialized}
    
    @router.get("/{collection}/list", name="list_documents_json", dependencies=get_dependencies(), include_in_schema=False)
    async def list_documents_json(
        collection: str,
        per_page: int = 20,
        page: int = 1,
        search: str = "",
        sort: str = ""
    ):
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            # Collection doesn't exist, return empty result
            return {
                "success": False,
                "items": [],
                "total": 0,
                "page": 1,
                "pages": 0,
                "per_page": per_page,
                "error": f"Collection '{collection}' not found"
            }
        
        crud = CRUDOperations(admin)
        
        sort_list = None
        if sort:
            parts = sort.split(":")
            if len(parts) == 2:
                field, direction = parts
                sort_list = [(field, -1 if direction == "desc" else 1)]
        
        result = await crud.list(
            page=page,
            per_page=per_page,
            search=search if search else None,
            sort=sort_list
        )
        
        # Serialize items
        serializer = JSONSerializer()
        items = [serializer._serialize_value(item) for item in result["items"]]
        
        return {
            "success": True,
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "pages": result["pages"],
            "per_page": result["per_page"]
        }
    
    @router.delete("/{collection}/{id}", name="delete_document", dependencies=get_dependencies(), include_in_schema=False)
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
    
    @router.post("/{collection}", name="create_document", dependencies=get_dependencies(), include_in_schema=False)
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


def create_auth_dependency(auth_backend: Any):
    """
    Create a FastAPI dependency from an AuthenticationBackend instance.
    
    This dependency will check authentication and raise 401 if not authenticated.
    """
    async def auth_dependency(request: Request):
        from fastapi import HTTPException, status
        
        is_authenticated = await auth_backend.authenticate(request)
        if not is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        return True
    
    return auth_dependency


async def _get_all_collections(engine: MongloEngine) -> list[dict[str, Any]]:
    collections = []
    for name, admin in engine.registry._collections.items():
        count = await admin.collection.count_documents({})
        collections.append({
            "name": name,
            "display_name": admin.display_name,
            "count": count,
            "relationships": len(admin.relationships) 
        })
    return collections
