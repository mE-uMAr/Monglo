from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.ui_helpers.fastapi import setup_ui
from monglo.adapters.fastapi import create_fastapi_router
from monglo.auth import MongoDBAuthenticationBackend

# Import our modules
from db import seed_database
from admin_setup import setup_admin

# APP CONFIGURATION
app = FastAPI(
    title="Monglo with Auth",
    description="Advanced admin panel with session authentication",
    version="1.0.0"
)

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_auth_example

# Initialize Monglo engine
engine = MongloEngine(
    database=db,
    auto_discover=False
)

# Helper function for password verification (example)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    import hashlib
    hashed = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed == hashed_password


# Setup MongoDB-based authentication backend
auth_backend = MongoDBAuthenticationBackend(
    secret_key="your-secret-key-change-in-production",  # Use env variable in production
    user_collection=db.users,                           # Your users collection
    username_field="email",                             # Field for username/email
    password_field="hashed_password",                   # Field for hashed password
    role_field="role",                                  # Field for user role
    admin_role="admin",                           # Required role for admin access
    password_verifier=verify_password                   # Your password verification function
)

# Setup admin UI with authentication
# NOTE: Must be called BEFORE @app.on_event("startup") to register middleware
setup_ui(
    app,
    engine,
    prefix="/admin",
    title="Secured Admin Panel",
    brand_color="#6366f1",
    auth_backend=auth_backend  # pass the auth backend!
)

# Setup REST API
app.include_router(
    create_fastapi_router(engine, prefix="/api"),
    prefix="/api",
    tags=["API"]
)


# STARTUP & SHUTDOWN

@app.on_event("startup")
async def startup():
    """Initialize application"""
    
    print("🚀 Starting Monglo Auth Example...")
    
    # Seed database
    await seed_database(db)
    
    # Setup custom admin configurations
    await setup_admin(engine)
    
    # Initialize Monglo engine
    await engine.initialize()
    
    print("✅ Application started successfully!")
    print(f"   🔐 Login: http://localhost:8000/admin/login")
    print(f"   📊 Admin Panel: http://localhost:8000/admin")
    print(f"   🔌 API Docs: http://localhost:8000/docs")
    print(f"\n   Credentials: admin@example.com / admin123")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup"""
    client.close()
    print("👋 Application shut down")


# HEALTH CHECK

@app.get("/", tags=["Health"])
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "app": "Monglo Auth Example",
        "version": "1.0.0",
        "auth": "MongoDB-based authentication with AuthenticationBackend",
        "endpoints": {
            "login": "/admin/login",
            "admin": "/admin",
            "api": "/api",
            "docs": "/docs"
        }
    }
