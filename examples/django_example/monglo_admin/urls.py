
from django.urls import path
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.ui_helpers.django import create_ui_urlpatterns
from monglo.adapters.django import create_django_urls

# ============================================================================
# APPLICATION CODE - This is ALL the developer writes!
# ============================================================================

# Step 1: Connect to MongoDB (standard Motor code)
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_demo

# Step 2: Initialize Monglo (ONE line!)
engine = MongloEngine(database=db, auto_discover=True)

async def initialize():
    await engine.initialize()
    print("\n" + "="*70)
    print("🎉 Monglo Admin is Ready!")
    print("="*70)
    print(f"📊 Collections: {len(engine.registry._collections)}")
    print(f"🌐 Admin UI:    http://localhost:8000/admin")
    print(f"📡 API:         http://localhost:8000/api")
    print("="*70 + "\n")

# Step 3: URL Configuration - Just include the patterns!
urlpatterns = [
    # Monglo UI routes - automatic templates, views, everything!
    *create_ui_urlpatterns(engine, prefix="admin"),
    
    # Monglo API routes - automatic REST API
    *create_django_urls(engine, prefix="api"),
]

# ============================================================================
# That's it! TRULY minimal. No views, no templates, no serializers!
# ============================================================================
