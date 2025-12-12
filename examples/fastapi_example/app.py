from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.ui_helpers.fastapi import create_ui_router
from monglo.adapters.fastapi import create_fastapi_router

# ============================================================================
# APPLICATION CODE - This is ALL the developer writes!
# ============================================================================

# Step 1: Connect to MongoDB (standard Motor code)
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_demo

# Step 2: Create FastAPI app (standard FastAPI code)
app = FastAPI(title="Monglo Admin")

# Step 3: Initialize Monglo (ONE line!)
engine = MongloEngine(database=db, auto_discover=True)

@app.on_event("startup")
async def startup():
    await engine.initialize()
    
    # Mount UI - library handles EVERYTHING (templates, static, routing, serialization)
    app.include_router(create_ui_router(engine))
    
    # Mount API - optional, for programmatic access
    app.include_router(create_fastapi_router(engine, prefix="/api"))
    
    # Pretty startup message
    print("\n" + "="*70)
    print("🎉 Monglo Admin is Ready!")
    print("="*70)
    print(f"📊 Collections: {len(engine.registry._collections)}")
    print(f"🌐 Admin UI:    http://localhost:8000/admin")
    print(f"📡 API:         http://localhost:8000/api")
    print(f"📚 Docs:        http://localhost:8000/docs")
    print("="*70 + "\n")

@app.on_event("shutdown")
async def shutdown():
    client.close()

# ============================================================================
# That's it! TRULY minimal. No templates, no routes, no filters, no config!
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
