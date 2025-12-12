
import pytest
from monglo.operations.aggregations import AggregationOperations

@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_aggregation(test_db):
    await test_db.sales.insert_many(
        [
            {"product": "A", "quantity": 10, "price": 100},
            {"product": "A", "quantity": 5, "price": 100},
            {"product": "B", "quantity": 20, "price": 50},
            {"product": "B", "quantity": 15, "price": 50},
        ]
    )

    agg_ops = AggregationOperations(test_db.sales)

    # Group by product and sum quantities
    pipeline = [
        {
            "$group": {
                "_id": "$product",
                "total_quantity": {"$sum": "$quantity"},
                "count": {"$sum": 1},
            }
        }
    ]

    results = await agg_ops.aggregate(pipeline)

    # Should have 2 groups
    assert len(results) == 2

    results_dict = {r["_id"]: r for r in results}
    assert results_dict["A"]["total_quantity"] == 15
    assert results_dict["B"]["total_quantity"] == 35

@pytest.mark.integration
@pytest.mark.asyncio
async def test_collection_statistics(test_db):
    await test_db.products.insert_many(
        [{"name": f"Product {i}", "price": i * 10, "stock": i * 5} for i in range(1, 11)]
    )

    agg_ops = AggregationOperations(test_db.products)

    stats = await agg_ops.get_statistics(["price", "stock"])

    assert "_id" in stats
    assert "price_avg" in stats
    assert "price_min" in stats
    assert "price_max" in stats
    assert "stock_avg" in stats

@pytest.mark.integration
@pytest.mark.asyncio
async def test_group_by_aggregation(test_db):
    await test_db.orders.insert_many(
        [
            {"status": "completed", "total": 100},
            {"status": "completed", "total": 150},
            {"status": "pending", "total": 200},
            {"status": "cancelled", "total": 50},
        ]
    )

    agg_ops = AggregationOperations(test_db.orders)

    # Group by status
    results = await agg_ops.group_by(
        field="status", aggregations={"total_sum": {"$sum": "$total"}, "count": {"$sum": 1}}
    )

    results_dict = {r["_id"]: r for r in results}
    assert results_dict["completed"]["total_sum"] == 250
    assert results_dict["completed"]["count"] == 2

@pytest.mark.integration
@pytest.mark.asyncio
async def test_date_range_aggregation(test_db):
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    await test_db.events.insert_many(
        [
            {"name": "Event 1", "date": now - timedelta(days=5)},
            {"name": "Event 2", "date": now - timedelta(days=3)},
            {"name": "Event 3", "date": now - timedelta(days=1)},
            {"name": "Event 4", "date": now + timedelta(days=1)},
        ]
    )

    agg_ops = AggregationOperations(test_db.events)

    # Count events in last 7 days
    pipeline = [{"$match": {"date": {"$gte": now - timedelta(days=7)}}}, {"$count": "total"}]

    results = await agg_ops.aggregate(pipeline)
    assert results[0]["total"] == 4

@pytest.mark.integration
@pytest.mark.asyncio
async def test_nested_aggregation(test_db):
    await test_db.orders.insert_many(
        [
            {
                "customer": "John",
                "items": [
                    {"product": "A", "qty": 2, "price": 10},
                    {"product": "B", "qty": 1, "price": 20},
                ],
            },
            {"customer": "Jane", "items": [{"product": "A", "qty": 3, "price": 10}]},
        ]
    )

    agg_ops = AggregationOperations(test_db.orders)

    # Unwind and group
    pipeline = [
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product",
                "total_qty": {"$sum": "$items.qty"},
                "total_revenue": {"$sum": {"$multiply": ["$items.qty", "$items.price"]}},
            }
        },
    ]

    results = await agg_ops.aggregate(pipeline)
    results_dict = {r["_id"]: r for r in results}

    # Product A: (2+3) qty, (2*10 + 3*10) revenue
    assert results_dict["A"]["total_qty"] == 5
    assert results_dict["A"]["total_revenue"] == 50

    # Product B: 1 qty, (1*20) revenue
    assert results_dict["B"]["total_qty"] == 1
    assert results_dict["B"]["total_revenue"] == 20
