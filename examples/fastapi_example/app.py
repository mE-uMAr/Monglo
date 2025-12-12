"""
FastAPI Example with Monglo UI.

Complete working example with professional admin interface.
"""

from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
UI_DIR = BASE_DIR / "monglo_ui"

# Initialize FastAPI app
app = FastAPI(
    title="Monglo Admin - FastAPI Example",
    description="Professional MongoDB Admin Interface",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(UI_DIR / "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(UI_DIR / "templates"))

# Add custom Jinja2 filters
def format_datetime(value):
    """Format datetime for display."""
    if value is None:
        return ""
    from datetime import datetime
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)

def type_class(value):
    """Get CSS class for value type."""
    if isinstance(value, str):
        return "string"
    elif isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, bool):
        return "boolean"
    return ""

templates.env.filters['format_datetime'] = format_datetime
templates.env.filters['type_class'] = type_class
templates.env.filters['str'] = str
templates.env.filters['truncate'] = lambda s, length: s[:length] + '...' if len(s) > length else s

# MongoDB connection
client = None
engine = None


@app.on_event("startup")
async def startup():
    """Initialize MongoDB and Monglo engine."""
    global client, engine
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.example_db
    
    # Seed some example data
    await seed_example_data(db)
    
    # Initialize Monglo engine
    engine = MongloEngine(database=db, auto_discover=True)
    await engine.initialize()
    
    # Mount admin API routes
    admin_router = create_fastapi_router(engine, prefix="/api/admin")
    app.include_router(admin_router)
    
    print("✓ Monglo initialized")
    print(f"✓ Discovered {len(engine.registry._collections)} collections")
    print("✓ Admin UI available at http://localhost:8000/admin")


@app.on_event("shutdown")
async def shutdown():
    """Close MongoDB connection."""
    if client:
        client.close()


async def seed_example_data(db):
    """Seed example data for demonstration."""
    from datetime import datetime
    from bson import ObjectId
    
    # Clear existing data
    await db.users.delete_many({})
    await db.products.delete_many({})
    await db.orders.delete_many({})
    
    # Create users
    users = await db.users.insert_many([
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "status": "active",
            "created_at": datetime.now()
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "status": "active",
            "created_at": datetime.now()
        },
        {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "status": "inactive",
            "created_at": datetime.now()
        }
    ])
    
    # Create products
    products = await db.products.insert_many([
        {
            "name": "Laptop Pro",
            "price": 1299.99,
            "stock": 15,
            "category": "electronics",
            "created_at": datetime.now()
        },
        {
            "name": "Wireless Mouse",
            "price": 29.99,
            "stock": 50,
            "category": "electronics",
            "created_at": datetime.now()
        },
        {
            "name": "Desk Chair",
            "price": 199.99,
            "stock": 8,
            "category": "furniture",
            "created_at": datetime.now()
        }
    ])
    
    # Create orders
    await db.orders.insert_many([
        {
            "user_id": users.inserted_ids[0],
            "product_ids": [products.inserted_ids[0], products.inserted_ids[1]],
            "total": 1329.98,
            "status": "completed",
            "created_at": datetime.now()
        },
        {
            "user_id": users.inserted_ids[1],
            "product_ids": [products.inserted_ids[2]],
            "total": 199.99,
            "status": "pending",
            "created_at": datetime.now()
        }
    ])
    
    print("✓ Example data seeded")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - redirect to admin."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Monglo Admin"
    })


@app.get("/admin", response_class=HTMLResponse)
async def admin_home(request: Request):
    """Admin home page."""
    # Get all collections with counts
    collections = []
    for name, admin in engine.registry._collections.items():
        count = await admin.collection.count_documents({})
        collections.append({
            "name": name,
            "display_name": admin.display_name,
            "count": count
        })
    
    return templates.TemplateResponse("admin_home.html", {
        "request": request,
        "collections": collections,
        "current_collection": None
    })


@app.get("/admin/{collection}", response_class=HTMLResponse)
async def collection_table_view(request: Request, collection: str):
    """Table view for a collection."""
    from monglo.views import TableView
    from monglo.operations.crud import CRUDOperations
    
    # Get collection admin
    admin = engine.registry.get(collection)
    
    # Get query params
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 20))
    search = request.query_params.get("search", "")
    sort = request.query_params.get("sort", "")
    
    # Parse sort
    sort_list = None
    if sort:
        field, direction = sort.split(":")
        sort_list = [(field, -1 if direction == "desc" else 1)]
    
    # Get data
    crud = CRUDOperations(admin)
    data = await crud.list(
        page=page,
        per_page=per_page,
        search=search if search else None,
        sort=sort_list
    )
    
    # Get view config
    table_view = TableView(admin)
    config = table_view.render_config()
    
    # Get all collections for sidebar
    collections = []
    for name, coll_admin in engine.registry._collections.items():
        count = await coll_admin.collection.count_documents({})
        collections.append({
            "name": name,
            "display_name": coll_admin.display_name,
            "count": count
        })
    
    return templates.TemplateResponse("table_view.html", {
        "request": request,
        "collection": admin,
        "config": config,
        "data": data,
        "collections": collections,
        "current_collection": collection
    })


@app.get("/admin/{collection}/document/{id}", response_class=HTMLResponse)
async def document_view(request: Request, collection: str, id: str):
    """Document view for a single document."""
    from monglo.views import DocumentView
    from monglo.operations.crud import CRUDOperations
    from monglo.serializers.json import JSONSerializer
    from fastapi.responses import RedirectResponse
    
    # Get collection admin
    admin = engine.registry.get(collection)
    
    # Get document
    crud = CRUDOperations(admin)
    try:
        document = await crud.get(id)
    except KeyError:
        # Document not found - redirect back to collection
        return RedirectResponse(url=f"/admin/{collection}", status_code=302)
    
    # Serialize document to make it template-safe (dict with strings, not ObjectId)
    serializer = JSONSerializer()
    # Use _serialize_value to get dict, not JSON string
    serialized_doc = serializer._serialize_value(document)
    
    # Get view config
    doc_view = DocumentView(admin)
    config = doc_view.render_config()
    
    # Get all collections for sidebar
    collections = []
    for name, coll_admin in engine.registry._collections.items():
        count = await coll_admin.collection.count_documents({})
        collections.append({
            "name": name,
            "display_name": coll_admin.display_name,
            "count": count
        })
    
    return templates.TemplateResponse("document_view.html", {
        "request": request,
        "collection": admin,
        "document": serialized_doc,
        "relationships": admin.relationships,
        "collections": collections,
        "current_collection": collection
    })


@app.delete("/api/admin/{collection}/{id}")
async def delete_document(collection: str, id: str):
    """Delete a document."""
    from monglo.operations.crud import CRUDOperations
    
    admin = engine.registry.get(collection)
    crud = CRUDOperations(admin)
    
    await crud.delete(id)
    return {"success": True, "message": "Document deleted"}


@app.put("/api/admin/{collection}/{id}")
async def update_document(collection: str, id: str, data: dict):
    """Update a document."""
    from monglo.operations.crud import CRUDOperations
    from monglo.serializers.json import JSONSerializer
    
    admin = engine.registry.get(collection)
    crud = CRUDOperations(admin)
    
    updated = await crud.update(id, data)
    
    # Serialize ObjectId to dict for JSON response (not JSON string)
    serializer = JSONSerializer()
    serialized = serializer._serialize_value(updated)
    
    return {"success": True, "document": serialized}


@app.post("/api/admin/{collection}")
async def create_document(collection: str, data: dict):
    """Create a new document."""
    from monglo.operations.crud import CRUDOperations
    from monglo.serializers.json import JSONSerializer
    
    admin = engine.registry.get(collection)
    crud = CRUDOperations(admin)
    
    created = await crud.create(data)
    
    # Serialize ObjectId to dict for JSON response (not JSON string)
    serializer = JSONSerializer()
    serialized = serializer._serialize_value(created)
    
    return {"success": True, "document": serialized}


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "ui": "enabled"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting Monglo Admin with Professional UI")
    print("="*60)
    print("📍 Admin UI: http://localhost:8000/admin")
    print("📍 API Docs: http://localhost:8000/docs")
    print("📍 Health: http://localhost:8000/health")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
