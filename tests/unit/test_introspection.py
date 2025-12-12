
import pytest
from datetime import datetime, date
from bson import ObjectId, DBRef

from monglo.core.introspection import SchemaIntrospector

class TestSchemaIntrospector:

    @pytest.fixture
    def mock_db(self, mocker):
        return mocker.AsyncMock()

    @pytest.fixture
    def introspector(self, mock_db):
        return SchemaIntrospector(mock_db)

    @pytest.mark.asyncio
    async def test_introspect_basic_types(self, introspector, mock_db, mocker):
        documents = [
            {
                "_id": ObjectId(),
                "name": "Alice",
                "age": 30,
                "is_active": True,
                "score": 95.5,
                "created_at": datetime.now(),
            },
            {
                "_id": ObjectId(),
                "name": "Bob",
                "age": 25,
                "is_active": False,
                "score": 87.3,
                "created_at": datetime.now(),
            },
        ]

        # Mock collection
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("users")

        assert schema["name"]["type"] == "string"
        assert schema["age"]["type"] == "integer"
        assert schema["is_active"]["type"] == "boolean"
        assert schema["score"]["type"] == "number"
        assert schema["created_at"]["type"] == "datetime"

    @pytest.mark.asyncio
    async def test_introspect_frequency(self, introspector, mock_db, mocker):
        documents = [
            {"_id": ObjectId(), "name": "Alice", "email": "alice@example.com"},
            {"_id": ObjectId(), "name": "Bob", "email": "bob@example.com"},
            {"_id": ObjectId(), "name": "Charlie"},  # Missing email
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("users")

        # name appears in all 3 docs
        assert schema["name"]["frequency"] == 1.0

        # email appears in 2 out of 3 docs
        assert schema["email"]["frequency"] == pytest.approx(2 / 3)

    @pytest.mark.asyncio
    async def test_introspect_nullable(self, introspector, mock_db, mocker):
        documents = [
            {"_id": ObjectId(), "name": "Alice", "bio": "Developer"},
            {"_id": ObjectId(), "name": "Bob", "bio": None},
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("users")

        assert schema["name"]["nullable"] is False
        assert schema["bio"]["nullable"] is True

    @pytest.mark.asyncio
    async def test_introspect_mongodb_types(self, introspector, mock_db, mocker):
        documents = [
            {
                "_id": ObjectId(),
                "user_id": ObjectId(),
                "owner": DBRef("users", ObjectId()),
                "data": b"binary data",
            }
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("documents")

        assert schema["user_id"]["type"] == "objectid"
        assert schema["owner"]["type"] == "dbref"
        assert schema["data"]["type"] == "binary"

    @pytest.mark.asyncio
    async def test_introspect_nested_documents(self, introspector, mock_db, mocker):
        documents = [
            {
                "_id": ObjectId(),
                "name": "Alice",
                "address": {"street": "123 Main St", "city": "NYC", "zip": "10001"},
            }
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("users")

        # Parent field should be marked as embedded
        assert schema["address"]["type"] == "embedded"

        # Nested fields should be detected with dot notation
        assert "address.street" in schema
        assert schema["address.street"]["type"] == "string"
        assert schema["address.city"]["type"] == "string"

    @pytest.mark.asyncio
    async def test_introspect_arrays(self, introspector, mock_db, mocker):
        documents = [
            {
                "_id": ObjectId(),
                "name": "Product",
                "tags": ["electronics", "sale"],
                "related_ids": [ObjectId(), ObjectId()],
            }
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("products")

        assert schema["tags"]["type"] == "array"
        assert schema["tags"]["array_item_type"] == "string"

        assert schema["related_ids"]["type"] == "array"
        assert schema["related_ids"]["array_item_type"] == "objectid"

    @pytest.mark.asyncio
    async def test_introspect_array_of_objects(self, introspector, mock_db, mocker):
        documents = [
            {
                "_id": ObjectId(),
                "name": "Order",
                "items": [
                    {"product": "Widget", "quantity": 2},
                    {"product": "Gadget", "quantity": 1},
                ],
            }
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("orders")

        assert schema["items"]["type"] == "array"
        assert schema["items"]["array_item_type"] == "embedded"

        # Array item fields with special notation
        assert "items.[].product" in schema
        assert schema["items.[].product"]["type"] == "string"

    @pytest.mark.asyncio
    async def test_introspect_empty_collection(self, introspector, mock_db, mocker):
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=[]
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("empty")

        assert schema == {}

    @pytest.mark.asyncio
    async def test_introspect_sample_values(self, introspector, mock_db, mocker):
        documents = [
            {"_id": ObjectId(), "status": "active"},
            {"_id": ObjectId(), "status": "inactive"},
            {"_id": ObjectId(), "status": "pending"},
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("records")

        assert "sample_values" in schema["status"]
        assert len(schema["status"]["sample_values"]) <= 5  # Max 5 samples

    @pytest.mark.asyncio
    async def test_introspect_alternative_types(self, introspector, mock_db, mocker):
        documents = [
            {"_id": ObjectId(), "value": 123},  # integer
            {"_id": ObjectId(), "value": "text"},  # string
            {"_id": ObjectId(), "value": 45.6},  # float
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=documents
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        schema = await introspector.introspect("mixed")

        # Should have alternative_types since field has multiple types
        assert "alternative_types" in schema["value"]
        assert "string" in schema["value"]["alternative_types"]

    def test_detect_type(self, introspector):
        assert introspector._detect_type(None) == "null"
        assert introspector._detect_type(True) == "boolean"
        assert introspector._detect_type(42) == "integer"
        assert introspector._detect_type(3.14) == "number"
        assert introspector._detect_type("hello") == "string"
        assert introspector._detect_type(datetime.now()) == "datetime"
        assert introspector._detect_type(date.today()) == "date"
        assert introspector._detect_type(ObjectId()) == "objectid"
        assert introspector._detect_type(DBRef("coll", ObjectId())) == "dbref"
        assert introspector._detect_type({}) == "embedded"
        assert introspector._detect_type([]) == "array"
        assert introspector._detect_type(b"bytes") == "binary"

    @pytest.mark.asyncio
    async def test_get_indexes(self, introspector, mock_db, mocker):
        indexes = [
            {"name": "_id_", "key": [("_id", 1)]},
            {"name": "email_1", "key": [("email", 1)], "unique": True},
        ]

        mock_collection = mocker.AsyncMock()
        mock_collection.list_indexes = mocker.MagicMock()
        mock_collection.list_indexes.return_value.to_list = mocker.AsyncMock(return_value=indexes)
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        result = await introspector.get_indexes("users")

        assert len(result) == 2
        assert result[0]["name"] == "_id_"
        assert result[1]["unique"] is True

    @pytest.mark.asyncio
    async def test_analyze_field_cardinality(self, introspector, mock_db, mocker):
        mock_collection = mocker.AsyncMock()
        mock_collection.count_documents = mocker.AsyncMock(return_value=100)
        mock_collection.distinct = mocker.AsyncMock(return_value=["active", "inactive", "pending"])
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        result = await introspector.analyze_field_cardinality("users", "status")

        assert result["field"] == "status"
        assert result["total_documents"] == 100
        assert result["distinct_count"] == 3
        assert result["cardinality_ratio"] == 0.03
        assert result["is_unique"] is False
        assert result["is_low_cardinality"] is True
        assert len(result["sample_values"]) == 3
