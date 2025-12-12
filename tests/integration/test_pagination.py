
import pytest
from monglo.operations.pagination import PaginationHandler

@pytest.mark.integration
@pytest.mark.asyncio
async def test_offset_pagination(test_db):
    test_docs = [{"value": i} for i in range(100)]
    await test_db.items.insert_many(test_docs)

    pag = PaginationHandler(test_db.items)

    # Test first page
    page1 = await pag.paginate_offset({}, page=1, per_page=20)
    assert len(page1["items"]) == 20
    assert page1["pagination"]["total"] == 100
    assert page1["pagination"]["page"] == 1
    assert page1["pagination"]["total_pages"] == 5
    assert page1["pagination"]["has_next"] is True
    assert page1["pagination"]["has_prev"] is False

    # Test middle page
    page3 = await pag.paginate_offset({}, page=3, per_page=20)
    assert len(page3["items"]) == 20
    assert page3["pagination"]["page"] == 3
    assert page3["pagination"]["has_next"] is True
    assert page3["pagination"]["has_prev"] is True

    # Test last page
    page5 = await pag.paginate_offset({}, page=5, per_page=20)
    assert len(page5["items"]) == 20
    assert page5["pagination"]["page"] == 5
    assert page5["pagination"]["has_next"] is False
    assert page5["pagination"]["has_prev"] is True

@pytest.mark.integration
@pytest.mark.asyncio
async def test_cursor_pagination(test_db):
    from bson import ObjectId

    test_ids = [ObjectId() for _ in range(50)]
    test_docs = [{"_id": test_ids[i], "value": i} for i in range(50)]
    await test_db.items.insert_many(test_docs)

    pag = PaginationHandler(test_db.items)

    # First page (no cursor)
    page1 = await pag.paginate_cursor({}, per_page=15)
    assert len(page1["items"]) == 15
    assert page1["pagination"]["has_next"] is True
    assert page1["pagination"]["next_cursor"] is not None

    # Second page using cursor
    page2 = await pag.paginate_cursor({}, per_page=15, cursor=page1["pagination"]["next_cursor"])
    assert len(page2["items"]) == 15
    assert page2["pagination"]["has_next"] is True

    # Verify no overlap
    page1_ids = {doc["_id"] for doc in page1["items"]}
    page2_ids = {doc["_id"] for doc in page2["items"]}
    assert len(page1_ids & page2_ids) == 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_with_filtering(test_db):
    await test_db.items.insert_many(
        [
            *[{"category": "A", "value": i} for i in range(30)],
            *[{"category": "B", "value": i} for i in range(30)],
        ]
    )

    pag = PaginationHandler(test_db.items)

    # Paginate filtered results
    page1 = await pag.paginate_offset({"category": "A"}, page=1, per_page=10)

    assert page1["pagination"]["total"] == 30
    assert len(page1["items"]) == 10
    assert all(doc["category"] == "A" for doc in page1["items"])

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_with_sorting(test_db):
    import random

    values = list(range(50))
    random.shuffle(values)
    await test_db.items.insert_many([{"value": v} for v in values])

    pag = PaginationHandler(test_db.items)

    # Paginate with descending sort
    page1 = await pag.paginate_offset({}, page=1, per_page=10, sort=[("value", -1)])

    # Should be sorted descending
    page1_values = [doc["value"] for doc in page1["items"]]
    assert page1_values == sorted(page1_values, reverse=True)

    # Continue to page 2
    page2 = await pag.paginate_offset({}, page=2, per_page=10, sort=[("value", -1)])

    # Page 2 values should all be less than page 1's minimum
    page2_values = [doc["value"] for doc in page2["items"]]
    assert max(page2_values) < min(page1_values)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_edge_cases(test_db):
    await test_db.items.insert_many([{"value": i} for i in range(25)])

    pag = PaginationHandler(test_db.items)

    # Test requesting beyond last page
    page10 = await pag.paginate_offset({}, page=10, per_page=10)
    assert page10["items"] == []
    assert page10["pagination"]["page"] == 10
    assert page10["pagination"]["total"] == 25
    assert page10["pagination"]["has_next"] is False

    # Test per_page larger than total
    page1_big = await pag.paginate_offset({}, page=1, per_page=100)
    assert len(page1_big["items"]) == 25
    assert page1_big["pagination"]["total_pages"] == 1

    # Test per_page = 1
    page1_single = await pag.paginate_offset({}, page=1, per_page=1)
    assert len(page1_single["items"]) == 1
    assert page1_single["pagination"]["total_pages"] == 25

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_metadata_accuracy(test_db):
    await test_db.items.insert_many([{"value": i} for i in range(47)])

    pag = PaginationHandler(test_db.items)

    # Test with per_page=10
    page1 = await pag.paginate_offset({}, page=1, per_page=10)
    assert page1["pagination"]["total"] == 47
    assert page1["pagination"]["total_pages"] == 5  # Ceiling of 47/10
    assert page1["pagination"]["per_page"] == 10

    # Last page should have only 7 items
    page5 = await pag.paginate_offset({}, page=5, per_page=10)
    assert len(page5["items"]) == 7
    assert page5["pagination"]["has_next"] is False
