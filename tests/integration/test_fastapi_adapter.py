
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router
from monglo.ui_helpers.fastapi import create_ui_router

@pytest.fixture
async def fastapi_app(test_db):
    from fastapi import FastAPI
    
    app = FastAPI()
    engine = MongloEngine(database=test_db, auto_discover=False)
    
    # Manually register a test collection
    from monglo.core.config import CollectionConfig
    await engine.register_collection(
        "users",
        config=CollectionConfig(
            list_fields=["name", "email"],
            search_fields=["name", "email"]
        )
    )
    
    # Mount routers
    app.include_router(create_fastapi_router(engine))
    app.include_router(create_ui_router(engine))
    
    return app

@pytest.mark.integration
class TestFastAPIAdapter:
    
    def test_list_collections(self, fastapi_app):
        client = TestClient(fastapi_app)
        response = client.get("/api/admin/")
        
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data
        assert len(data["collections"]) > 0
    
    async def test_create_document(self, fastapi_app, test_db):
        client = TestClient(fastapi_app)
        
        doc_data = {
            "name": "Alice",
            "email": "alice@example.com"
        }
        
        response = client.post("/api/admin/users", json=doc_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "document" in data
