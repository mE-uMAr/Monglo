"""
E-Commerce Admin - Advanced FastAPI Example
Demonstrates modular architecture with custom admin configuration
"""

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.ui_helpers.fastapi import setup_ui
from monglo.adapters.fastapi import create_fastapi_router

# Import our custom modules
from db import seed_database
from admin_setup import setup_admin


#APP CONFIGURATION 

app = FastAPI(
    title="E-Commerce Admin",
    description="Advanced admin panel with custom configurations",
    version="1.0.0"
)

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.ecommerce_advanced

# Initialize Monglo engine
engine = MongloEngine(
    database=db,
    auto_discover=False  # Don't auto-discover - we'll register custom admins manually
)

# Setup admin UI with branding
setup_ui(
    app,
    engine=engine,
    title="E-Commerce Admin",
    prefix="/custom_admin",
)

# STARTUP & SHUTDOWN

@app.on_event("startup")
async def startup():
    """Initialize application on startup"""
    
    print("🚀 Starting E-Commerce Admin...")
    
    # Seed database with example data
    await seed_database(db)
    
    # Setup custom admin configurations FIRST
    await setup_admin(engine)
    
    # Then initialize monglo engine (discover relationships, etc.)
    await engine.initialize()
    
    # Setup REST API router
    app.include_router(
        create_fastapi_router(engine, prefix="/api"),
        prefix="/api",
        tags=["API"]
    )
    

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    client.close()
    print("👋 Application shut down")


# HEALTH CHECK

@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "E-Commerce Admin",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin",
            "api": "/api",
            "docs": "/docs"
        }
    }

