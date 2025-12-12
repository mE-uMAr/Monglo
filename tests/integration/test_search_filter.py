
import pytest
from monglo.operations.search import SearchOperations
from monglo.core.query_builder import QueryBuilder

@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_search(test_db):
    await test_db.articles.insert_many(
        [
            {"title": "Python Programming", "content": "Learn Python basics"},
            {"title": "MongoDB Guide", "content": "Database fundamentals"},
            {"title": "Python and MongoDB", "content": "Building apps with Python"},
            {"title": "JavaScript Tutorial", "content": "Web development basics"},
        ]
    )

    search_ops = SearchOperations(test_db.articles, search_fields=["title", "content"])

    # Search for "Python"
    results = await search_ops.search("Python")
    assert len(results) == 3  # Should match 3 documents

    # Search for "MongoDB"
    results = await search_ops.search("MongoDB")
    assert len(results) == 2

@pytest.mark.integration
@pytest.mark.asyncio
async def test_case_insensitive_search(test_db):
    await test_db.articles.insert_many(
        [{"title": "PYTHON Guide"}, {"title": "python basics"}, {"title": "PyThOn advanced"}]
    )

    search_ops = SearchOperations(test_db.articles, search_fields=["title"])

    # All variations should match
    for query in ["python", "PYTHON", "PyThOn"]:
        results = await search_ops.search(query, case_sensitive=False)
        assert len(results) == 3

@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_with_highlighting(test_db):
    await test_db.articles.insert_many(
        [
            {"title": "Python Guide", "content": "JavaScript tutorial", "author": "John"},
            {"title": "Java Basics", "content": "Python and Java", "author": "Jane"},
        ]
    )

    search_ops = SearchOperations(test_db.articles, search_fields=["title", "content"])

    results = await search_ops.search_with_highlight("Python")

    for doc in results:
        assert "_matched_fields" in doc
        # Should highlight fields that contain "Python"
        matched = doc["_matched_fields"]
        has_python = any("python" in str(doc.get(field, "")).lower() for field in matched)
        assert has_python

@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_pagination(test_db):
    await test_db.articles.insert_many(
        [{"title": f"Test Article {i}", "content": "Content"} for i in range(50)]
    )

    search_ops = SearchOperations(test_db.articles, search_fields=["title"])

    # Paginated search
    page1 = await search_ops.search_paginated("Test", page=1, per_page=20)
    assert page1["total"] == 50
    assert len(page1["items"]) == 20
    assert page1["pages"] == 3

    page2 = await search_ops.search_paginated("Test", page=2, per_page=20)
    assert len(page2["items"]) == 20

    # Verify no overlap
    page1_titles = {doc["title"] for doc in page1["items"]}
    page2_titles = {doc["title"] for doc in page2["items"]}
    assert len(page1_titles & page2_titles) == 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_filter_building(test_db):
    await test_db.products.insert_many(
        [
            {"name": "Product A", "price": 10, "stock": 100, "category": "electronics"},
            {"name": "Product B", "price": 20, "stock": 50, "category": "electronics"},
            {"name": "Product C", "price": 30, "stock": 0, "category": "books"},
            {"name": "Product D", "price": 40, "stock": 200, "category": "books"},
        ]
    )

    # Test equality
    query = QueryBuilder.build_filter({"category": "electronics"})
    count = await test_db.products.count_documents(query)
    assert count == 2

    # Test __gte operator
    query = QueryBuilder.build_filter({"price__gte": 30})
    results = await test_db.products.find(query).to_list(10)
    assert len(results) == 2
    assert all(doc["price"] >= 30 for doc in results)

    # Test __lt operator
    query = QueryBuilder.build_filter({"stock__lt": 100})
    results = await test_db.products.find(query).to_list(10)
    assert all(doc["stock"] < 100 for doc in results)

    # Test __in operator
    query = QueryBuilder.build_filter({"category__in": ["electronics", "books"]})
    count = await test_db.products.count_documents(query)
    assert count == 4

@pytest.mark.integration
@pytest.mark.asyncio
async def test_combined_filters(test_db):
    await test_db.products.insert_many(
        [
            {"name": "Item 1", "price": 15, "stock": 100, "active": True},
            {"name": "Item 2", "price": 25, "stock": 50, "active": True},
            {"name": "Item 3", "price": 35, "stock": 0, "active": False},
            {"name": "Item 4", "price": 45, "stock": 200, "active": True},
        ]
    )

    filters = {"active": True, "price__gte": 20, "stock__gt": 0}
    query = QueryBuilder.build_filter(filters)
    results = await test_db.products.find(query).to_list(10)

    # Should match Item 2 and Item 4
    assert len(results) >= 2
    for doc in results:
        assert doc["active"] is True
        assert doc["price"] >= 20
        assert doc["stock"] > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_and_filter_combined(test_db):
    await test_db.products.insert_many(
        [
            {"name": "Python Book", "category": "books", "price": 30, "in_stock": True},
            {"name": "Python Course", "category": "courses", "price": 50, "in_stock": True},
            {"name": "Python Mug", "category": "merchandise", "price": 10, "in_stock": False},
            {"name": "Java Book", "category": "books", "price": 35, "in_stock": True},
        ]
    )

    search_query = QueryBuilder.build_search_query("Python", ["name"])

    filter_query = QueryBuilder.build_filter({"in_stock": True, "price__gte": 25})

    combined = QueryBuilder.combine_queries(search_query, filter_query)

    results = await test_db.products.find(combined).to_list(10)

    # Should match only: Python Book and Python Course
    assert len(results) == 2
    for doc in results:
        assert "Python" in doc["name"]
        assert doc["in_stock"] is True
        assert doc["price"] >= 25

@pytest.mark.integration
@pytest.mark.asyncio
async def test_regex_special_characters(test_db):
    await test_db.articles.insert_many(
        [
            {"title": "C++ Programming"},
            {"title": "C# Basics"},
            {"title": "Regular expressions (regex)"},
        ]
    )

    search_ops = SearchOperations(test_db.articles, search_fields=["title"])

    # Search for "C++" - should not break regex
    results = await search_ops.search("C++")
    # Should find "C++ Programming"
    assert len(results) >= 1

    # Search for parentheses
    results = await search_ops.search("(regex)")
    assert len(results) >= 1
