from fastapi import FastAPI, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine, CollectionConfig
from monglo.adapters.fastapi import create_fastapi_router
from monglo.ui_helpers.fastapi import create_ui_router
from monglo.auth import SimpleAuthProvider
from monglo.operations.audit import AuditLogger
from monglo.operations.transactions import TransactionManager
from monglo.operations.validation import DataValidator

# =============================================================================
# APPLICATION CODE - Your Configuration
# =============================================================================

# 1. Your MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.advanced_demo

# 2. Your authentication rules
auth_provider = SimpleAuthProvider(users={
    "admin": {
        "password_hash": SimpleAuthProvider.hash_password("admin123"),
        "role": "admin"
    },
    "editor": {
        "password_hash": SimpleAuthProvider.hash_password("editor123"),
        "role": "user"
    },
    "viewer": {
        "password_hash": SimpleAuthProvider.hash_password("viewer123"),
        "role": "readonly"
    }
})

# 3. Your audit logging
audit_logger = AuditLogger(database=db, collection_name="admin_audit_log")

# 4. Your transaction manager
transaction_manager = TransactionManager(client)

# =============================================================================
# LIBRARY CODE - Monglo Handles Everything
# =============================================================================

engine = MongloEngine(
    database=db,
    auto_discover=True,
    auth_provider=auth_provider
)

app = FastAPI(
    title="Advanced Monglo Demo",
    description="Showcasing all Monglo features with clear library/app separation"
)

@app.on_event("startup")
async def startup():
    # Library initializes and auto-discovers
    await engine.initialize()
    
    # Optional: Your custom collection configs
    await engine.register_collection(
        "users",
        config=CollectionConfig(
            list_fields=["name", "email", "role", "created_at"],
            search_fields=["name", "email"],
            # Your business rules here
        )
    )
    
    # Library creates all routes automatically
    api_router = create_fastapi_router(engine)
    ui_router = create_ui_router(
        engine,
        title="Advanced Admin Demo",
        brand_color="#6366f1"
    )
    
    app.include_router(api_router)
    app.include_router(ui_router)
    
    print("\n" + "="*70)
    print("🚀 Advanced Monglo Demo")
    print("="*70)
    print(f"📊 Collections: {len(engine.registry._collections)}")
    print(f"🔐 Auth: Enabled (admin/admin123, editor/editor123, viewer/viewer123)")
    print(f"📝 Audit: Enabled (logs in 'admin_audit_log' collection)")
    print(f"💼 Transactions: Enabled")
    print("")
    print(f"🌐 Admin UI:    http://localhost:8000/admin")
    print(f"📡 API:         http://localhost:8000/api/admin")
    print(f"📚 API Docs:    http://localhost:8000/docs")
    print("="*70 + "\n")

# =============================================================================
# APPLICATION CODE - Your Custom Endpoints (Optional)
# =============================================================================

@app.post("/api/custom/bulk-create-users")
async def custom_bulk_create(count: int):
    from monglo.operations.crud import CRUDOperations
    
    # Your business logic
    if count > 1000:
        raise HTTPException(400, "Maximum 1000 users at once")
    
    users_admin = engine.registry.get("users")
    crud = CRUDOperations(users_admin)
    
    # Your data generation
    new_users = [
        {
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "role": "user"
        }
        for i in range(count)
    ]
    
    # Library handles bulk insert efficiently
    created = await crud.bulk_create(new_users)
    
    # Your logging (library provides the tools)
    await audit_logger.log_bulk_operation(
        collection="users",
        action="bulk_create",
        count=len(created),
        details={"count": count}
    )
    
    return {"success": True, "created": len(created)}

@app.post("/api/custom/create-order-with-transaction")
async def custom_create_order(user_id: str, items: list[dict]):
    from monglo.operations.crud import CRUDOperations
    
    # Your business validation
    if not items:
        raise HTTPException(400, "Order must have items")
    
    users_crud = CRUDOperations(engine.registry.get("users"))
    orders_crud = CRUDOperations(engine.registry.get("orders"))
    
    # Library handles transaction atomicity
    async with transaction_manager.transaction() as session:
        # Verify user exists (your logic)
        user = await users_crud.get(user_id)
        
        order = await orders_crud.create({
            "user_id": user_id,
            "items": items,
            "total": sum(item.get("price", 0) for item in items)
        })
        
        # Both operations succeed or both fail (library guarantees)
        
    return {"success": True, "order_id": str(order["_id"])}

# =============================================================================
# Run the Application
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
