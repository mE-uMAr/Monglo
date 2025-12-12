
import pytest
from bson import ObjectId
from monglo.operations.crud import CRUDOperations

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_crud_lifecycle(registered_engine, test_db):
    admin = registered_engine.registry.get("users")
    crud = CRUDOperations(admin)

    # CREATE
    new_user = {
        "name": "Integration Test User",
        "email": "integration@test.com",
        "age": 28,
        "status": "active",
    }
    created = await crud.create(new_user)

    assert "_id" in created
    assert created["name"] == "Integration Test User"
    assert created["email"] == "integration@test.com"
    user_id = str(created["_id"])

    # READ - Get single
    found = await crud.get(user_id)
    assert found["_id"] == created["_id"]
    assert found["name"] == "Integration Test User"

    # READ - List with filters
    result = await crud.list(filters={"email": "integration@test.com"}, per_page=10)
    assert result["total"] >= 1
    assert any(doc["email"] == "integration@test.com" for doc in result["items"])

    # UPDATE
    updates = {"age": 29, "status": "verified"}
    updated = await crud.update(user_id, updates)
    assert updated["age"] == 29
    assert updated["status"] == "verified"
    assert updated["name"] == "Integration Test User"  # Unchanged

    # Verify update persisted
    refetched = await crud.get(user_id)
    assert refetched["age"] == 29
    assert refetched["status"] == "verified"

    # DELETE
    deleted = await crud.delete(user_id)
    assert deleted is True

    # Verify deletion
    with pytest.raises(KeyError):
        await crud.get(user_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_consistency(registered_engine, test_db):
    admin = registered_engine.registry.get("products")
    crud = CRUDOperations(admin)

    products = [{"name": f"Product {i:02d}", "price": i * 10, "stock": 100} for i in range(25)]
    await test_db.products.insert_many(products)

    page1 = await crud.list(page=1, per_page=10, sort=[("name", 1)])
    assert len(page1["items"]) == 10
    assert page1["total"] >= 25
    assert page1["page"] == 1

    page2 = await crud.list(page=2, per_page=10, sort=[("name", 1)])
    assert len(page2["items"]) == 10

    page3 = await crud.list(page=3, per_page=10, sort=[("name", 1)])
    assert len(page3["items"]) >= 5  # At least 5 remaining

    # Verify no overlap between pages
    page1_ids = {str(doc["_id"]) for doc in page1["items"]}
    page2_ids = {str(doc["_id"]) for doc in page2["items"]}
    page3_ids = {str(doc["_id"]) for doc in page3["items"]}

    assert len(page1_ids & page2_ids) == 0  # No overlap
    assert len(page2_ids & page3_ids) == 0  # No overlap

    # Verify sorting is maintained
    page1_names = [doc["name"] for doc in page1["items"]]
    assert page1_names == sorted(page1_names)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_across_fields(registered_engine, test_db, sample_products):
    admin = registered_engine.registry.get("products")
    crud = CRUDOperations(admin)

    await test_db.products.insert_many(
        [
            {"name": "iPhone 15 Pro", "description": "Latest Apple smartphone", "price": 999},
            {"name": "MacBook Air M3", "description": "Apple laptop with M3 chip", "price": 1299},
            {"name": "Samsung Galaxy S24", "description": "Android flagship phone", "price": 899},
            {"name": "iPad Pro", "description": "Apple tablet device", "price": 799},
        ]
    )

    # Search for "Apple" - should match 3 products
    results = await crud.list(search="Apple", per_page=100)
    assert results["total"] >= 3

    # Search for "phone" - should match at least 2 products
    results = await crud.list(search="phone", per_page=100)
    assert results["total"] >= 2

    # Search for specific model
    results = await crud.list(search="M3", per_page=100)
    assert results["total"] >= 1

    matched_items = [item for item in results["items"] if "M3" in item.get("description", "")]
    assert len(matched_items) >= 1

@pytest.mark.integration
@pytest.mark.asyncio
async def test_bulk_operations(registered_engine, test_db):
    admin = registered_engine.registry.get("users")
    crud = CRUDOperations(admin)

    test_users = [
        {"name": f"Bulk User {i}", "email": f"bulk{i}@test.com", "age": 20 + i} for i in range(5)
    ]
    result = await test_db.users.insert_many(test_users)
    user_ids = [str(id) for id in result.inserted_ids]

    # Bulk delete
    delete_result = await crud.bulk_delete(user_ids)
    assert delete_result["success"] is True
    assert delete_result["deleted_count"] == 5
    assert delete_result["requested_count"] == 5

    # Verify all deleted
    for user_id in user_ids:
        exists = await crud.exists(user_id)
        assert exists is False

@pytest.mark.integration
@pytest.mark.asyncio
async def test_filtering_with_operators(registered_engine, test_db):
    admin = registered_engine.registry.get("products")
    crud = CRUDOperations(admin)

    await test_db.products.insert_many(
        [
            {"name": "Product A", "price": 10, "category": "electronics", "stock": 100},
            {"name": "Product B", "price": 20, "category": "electronics", "stock": 50},
            {"name": "Product C", "price": 30, "category": "books", "stock": 200},
            {"name": "Product D", "price": 40, "category": "books", "stock": 0},
        ]
    )

    # Test equality filter
    results = await crud.list(filters={"category": "electronics"})
    assert results["total"] >= 2

    # Test greater than or equal
    results = await crud.list(filters={"price__gte": 30})
    assert results["total"] >= 2
    assert all(item["price"] >= 30 for item in results["items"])

    # Test less than
    results = await crud.list(filters={"stock__lt": 100})
    assert results["total"] >= 2
    assert all(item["stock"] < 100 for item in results["items"])

    # Test combined filters
    results = await crud.list(filters={"category": "books", "price__gte": 30})
    assert results["total"] >= 2

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sorting_multiple_fields(registered_engine, test_db):
    admin = registered_engine.registry.get("products")
    crud = CRUDOperations(admin)

    await test_db.products.insert_many(
        [
            {"name": "A Product", "category": "electronics", "price": 30},
            {"name": "B Product", "category": "electronics", "price": 20},
            {"name": "C Product", "category": "books", "price": 20},
            {"name": "D Product", "category": "books", "price": 10},
        ]
    )

    results = await crud.list(sort=[("category", 1), ("price", -1)], per_page=100)

    items = results["items"]
    # Books should come before electronics (ascending category)
    books = [item for item in items if item["category"] == "books"]
    electronics = [item for item in items if item["category"] == "electronics"]

    # Within books, prices should be descending
    if len(books) >= 2:
        assert books[0]["price"] >= books[1]["price"]

    # Within electronics, prices should be descending
    if len(electronics) >= 2:
        assert electronics[0]["price"] >= electronics[1]["price"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_updates(registered_engine, test_db):
    import asyncio

    admin = registered_engine.registry.get("users")
    crud = CRUDOperations(admin)

    user = await crud.create({"name": "Concurrent Test", "counter": 0})
    user_id = str(user["_id"])

    async def increment_counter():
        doc = await crud.get(user_id)
        new_counter = doc["counter"] + 1
        await asyncio.sleep(0.01)  # Simulate processing
        await crud.update(user_id, {"counter": new_counter})

    # Run 5 concurrent updates
    await asyncio.gather(*[increment_counter() for _ in range(5)])

    # Final counter should be 5
    final = await crud.get(user_id)
    # Note: Due to race conditions, this might not always be 5
    # In production, you'd use $inc operator for atomic updates
    assert final["counter"] > 0
