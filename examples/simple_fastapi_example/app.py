
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router
from monglo.ui_helpers.fastapi import create_ui_router

# ============= APPLICATION CODE (Developer writes this) =============

# 1. Setup MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_demo

# 2. Create FastAPI app
app = FastAPI(title="Monglo Admin - Minimal Example")

# 3. Initialize Monglo engine
engine = MongloEngine(database=db, auto_discover=True)

@app.on_event("startup")
async def startup():
    await engine.initialize()
    
    # Mount API routes (for programmatic access)
    api_router = create_fastapi_router(engine, prefix="/api/admin")
    app.include_router(api_router)
    
    # Mount UI routes (for browser-based admin) - LIBRARY DOES EVERYTHING!
    ui_router = create_ui_router(engine, prefix="/admin")
    app.include_router(ui_router)
    
    print("\n" + "="*60)
    print("✅ Monglo Admin Ready!")
    print("="*60)
    print(f"📊 Discovered {len(engine.registry._collections)} collections")
    print(f"🌐 Admin UI:  http://localhost:8000/admin")
    print(f"📡 API:      http://localhost:8000/api/admin")
    print(f"📚 Docs:     http://localhost:8000/docs")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown():
    client.close()

# ============= That's it! No templates, no serialization, no routing! =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
