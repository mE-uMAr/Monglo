from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.ui_helpers.fastapi import setup_ui
from monglo.adapters.fastapi import create_fastapi_router
from db import seed_database

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_demo

app = FastAPI(title="Monglo Admin")

#instantiate monglo engine
engine = MongloEngine(database=db, auto_discover=True)

@app.on_event("startup")
async def startup():
    
    # Seed example data
    await seed_database(db)
    
    #initialize monglo engine
    await engine.initialize()
    
    #setup monglo ui with custom branding
    setup_ui(
        app, 
        engine=engine,
        title="My Custom App",  # Custom title
    )
    
    #setup monglo router
    app.include_router(create_fastapi_router(engine, prefix="/api"))

@app.on_event("shutdown")
async def shutdown():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
