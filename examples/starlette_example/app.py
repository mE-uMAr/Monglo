
from starlette.applications import Starlette
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.adapters.starlette import create_starlette_routes

# ============= APPLICATION CODE =============

# 1. Setup MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_demo

# 2. Initialize Monglo
engine = MongloEngine(database=db, auto_discover=True)

async def startup():
    await engine.initialize()
    
    print("\n" + "="*60)
    print("✅ Monglo Admin Ready!")
    print("="*60)
    print(f"📊 Discovered {len(engine.registry._collections)} collections")
    print(f"📡 API:      http://localhost:8000/api/admin")
    print("="*60 + "\n")

# 3. Create Starlette app with auto-generated routes
app = Starlette(
    routes=create_starlette_routes(engine),
    on_startup=[startup]
)

# ============= That's it! =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
