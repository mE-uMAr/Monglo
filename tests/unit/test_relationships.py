
import pytest
from bson import ObjectId, DBRef

from monglo.core.relationships import (
    Relationship,
    RelationshipType,
    RelationshipDetector,
    RelationshipResolver,
)
from monglo.core.config import CollectionConfig

class TestRelationshipType:

    def test_enum_values(self):
        assert RelationshipType.ONE_TO_ONE.value == "one_to_one"
        assert RelationshipType.ONE_TO_MANY.value == "one_to_many"
        assert RelationshipType.MANY_TO_MANY.value == "many_to_many"
        assert RelationshipType.EMBEDDED.value == "embedded"

    def test_enum_comparison(self):
        rel1 = RelationshipType.ONE_TO_ONE
        rel2 = RelationshipType.ONE_TO_ONE
        rel3 = RelationshipType.ONE_TO_MANY

        assert rel1 == rel2
        assert rel1 != rel3

class TestRelationship:

    def test_creation(self):
        rel = Relationship(
            source_collection="orders",
            source_field="user_id",
            target_collection="users",
            target_field="_id",
            type=RelationshipType.ONE_TO_ONE,
        )

        assert rel.source_collection == "orders"
        assert rel.source_field == "user_id"
        assert rel.target_collection == "users"
        assert rel.target_field == "_id"
        assert rel.type == RelationshipType.ONE_TO_ONE
        assert rel.reverse_name is None

    def test_defaults(self):
        rel = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )

        assert rel.target_field == "_id"  # Default
        assert rel.type == RelationshipType.ONE_TO_ONE  # Default

    def test_with_reverse_name(self):
        rel = Relationship(
            source_collection="orders",
            source_field="user_id",
            target_collection="users",
            reverse_name="orders",
        )

        assert rel.reverse_name == "orders"

    def test_equality(self):
        rel1 = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )
        rel2 = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )
        rel3 = Relationship(
            source_collection="orders", source_field="product_id", target_collection="products"
        )

        assert rel1 == rel2
        assert rel1 != rel3

    def test_hashable(self):
        rel1 = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )
        rel2 = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )

        # Can be added to set
        rel_set = {rel1, rel2}
        assert len(rel_set) == 1  # Same relationship

        # Can be used as dict key
        rel_dict = {rel1: "value"}
        assert rel_dict[rel2] == "value"

class TestRelationshipDetector:

    @pytest.fixture
    def mock_db(self, mocker):
        db = mocker.AsyncMock()
        db.list_collection_names = mocker.AsyncMock(
            return_value=["users", "orders", "products", "categories"]
        )
        return db

    @pytest.fixture
    def detector(self, mock_db):
        return RelationshipDetector(mock_db)

    @pytest.mark.asyncio
    async def test_initialization(self, detector, mock_db):
        assert detector.db is mock_db
        assert detector._collection_cache == set()

    @pytest.mark.asyncio
    async def test_detect_naming_convention_single(self, detector, mock_db, mocker):
        # Mock collection find
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=[{"_id": ObjectId(), "user_id": ObjectId(), "total": 100}]
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        config = CollectionConfig()
        relationships = await detector.detect("orders", config)

        # Should detect user_id → users
        user_rels = [r for r in relationships if r.source_field == "user_id"]
        assert len(user_rels) == 1
        assert user_rels[0].target_collection == "users"
        assert user_rels[0].type == RelationshipType.ONE_TO_ONE

    @pytest.mark.asyncio
    async def test_detect_naming_convention_plural(self, detector, mock_db, mocker):
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=[
                {"_id": ObjectId(), "product_ids": [ObjectId(), ObjectId()], "total": 200}
            ]
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        config = CollectionConfig()
        relationships = await detector.detect("orders", config)

        # Should detect product_ids → products (one-to-many)
        product_rels = [r for r in relationships if r.source_field == "product_ids"]
        assert len(product_rels) == 1
        assert product_rels[0].target_collection == "products"
        assert product_rels[0].type == RelationshipType.ONE_TO_MANY

    @pytest.mark.asyncio
    async def test_detect_objectid_field(self, detector, mock_db, mocker):
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=[{"_id": ObjectId(), "author": ObjectId(), "title": "Post"}]
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        detector._collection_cache = {"users", "orders", "products", "authors"}

        config = CollectionConfig()
        relationships = await detector.detect("posts", config)

        # Should detect author → authors
        author_rels = [r for r in relationships if r.source_field == "author"]
        assert len(author_rels) == 1
        assert author_rels[0].target_collection == "authors"

    @pytest.mark.asyncio
    async def test_detect_dbref(self, detector, mock_db, mocker):
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=[{"_id": ObjectId(), "owner": DBRef("users", ObjectId())}]
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        config = CollectionConfig()
        relationships = await detector.detect("documents", config)

        # Should detect DBRef to users
        owner_rels = [r for r in relationships if r.source_field == "owner"]
        assert len(owner_rels) == 1
        assert owner_rels[0].target_collection == "users"
        assert owner_rels[0].type == RelationshipType.ONE_TO_ONE

    @pytest.mark.asyncio
    async def test_detect_empty_collection(self, detector, mock_db, mocker):
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=[]
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        config = CollectionConfig()
        relationships = await detector.detect("empty_collection", config)

        assert relationships == []

    @pytest.mark.asyncio
    async def test_detect_with_manual_relationships(self, detector, mock_db, mocker):
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.limit.return_value.to_list = mocker.AsyncMock(
            return_value=[{"_id": ObjectId()}]
        )
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        manual_rel = Relationship(
            source_collection="orders",
            source_field="custom_field",
            target_collection="custom_collection",
        )
        config = CollectionConfig(relationships=[manual_rel])

        relationships = await detector.detect("orders", config)

        # Manual relationship should be included
        assert manual_rel in relationships

    def test_guess_collection_from_field(self, detector):
        assert detector._guess_collection_from_field("user_id") == "users"
        assert detector._guess_collection_from_field("author_id") == "authors"
        assert detector._guess_collection_from_field("category_ids") == "categories"
        assert detector._guess_collection_from_field("product_ids") == "products"

    def test_pluralize(self, detector):
        assert detector._pluralize("user") == "users"
        assert detector._pluralize("author") == "authors"
        assert detector._pluralize("category") == "categories"
        assert detector._pluralize("class") == "classes"
        assert detector._pluralize("box") == "boxes"

class TestRelationshipResolver:

    @pytest.fixture
    def mock_db(self, mocker):
        return mocker.AsyncMock()

    @pytest.fixture
    def resolver(self, mock_db):
        return RelationshipResolver(mock_db)

    @pytest.mark.asyncio
    async def test_resolve_one_to_one(self, resolver, mock_db, mocker):
        user_id = ObjectId()
        user_doc = {"_id": user_id, "name": "Alice", "email": "alice@example.com"}

        # Mock collection
        mock_collection = mocker.AsyncMock()
        mock_collection.find_one = mocker.AsyncMock(return_value=user_doc)
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        document = {"_id": ObjectId(), "user_id": user_id, "total": 100}
        relationship = Relationship(
            source_collection="orders",
            source_field="user_id",
            target_collection="users",
            type=RelationshipType.ONE_TO_ONE,
        )

        result = await resolver.resolve(document, [relationship])

        assert "_relationships" in result
        assert "user_id" in result["_relationships"]
        assert result["_relationships"]["user_id"]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_resolve_one_to_many(self, resolver, mock_db, mocker):
        product_ids = [ObjectId(), ObjectId()]
        product_docs = [
            {"_id": product_ids[0], "name": "Product A"},
            {"_id": product_ids[1], "name": "Product B"},
        ]

        # Mock collection
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.to_list = mocker.AsyncMock(return_value=product_docs)
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        document = {"_id": ObjectId(), "product_ids": product_ids}
        relationship = Relationship(
            source_collection="orders",
            source_field="product_ids",
            target_collection="products",
            type=RelationshipType.ONE_TO_MANY,
        )

        result = await resolver.resolve(document, [relationship])

        assert "_relationships" in result
        assert "product_ids" in result["_relationships"]
        assert len(result["_relationships"]["product_ids"]) == 2
        assert result["_relationships"]["product_ids"][0]["name"] == "Product A"

    @pytest.mark.asyncio
    async def test_resolve_missing_field(self, resolver, mock_db):
        document = {"_id": ObjectId(), "total": 100}
        relationship = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )

        result = await resolver.resolve(document, [relationship])

        # Should still have _relationships but it should be empty
        assert "_relationships" in result
        assert "user_id" not in result["_relationships"]

    @pytest.mark.asyncio
    async def test_resolve_depth_zero(self, resolver, mock_db):
        document = {"_id": ObjectId(), "user_id": ObjectId()}
        relationship = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )

        result = await resolver.resolve(document, [relationship], depth=0)

        assert result == document
        assert "_relationships" not in result

    @pytest.mark.asyncio
    async def test_resolve_batch(self, resolver, mock_db, mocker):
        user_ids = [ObjectId(), ObjectId()]
        user_docs = [{"_id": user_ids[0], "name": "Alice"}, {"_id": user_ids[1], "name": "Bob"}]

        # Mock collection
        mock_collection = mocker.AsyncMock()
        mock_collection.find = mocker.MagicMock()
        mock_collection.find.return_value.to_list = mocker.AsyncMock(return_value=user_docs)
        mock_db.__getitem__ = mocker.MagicMock(return_value=mock_collection)

        documents = [
            {"_id": ObjectId(), "user_id": user_ids[0]},
            {"_id": ObjectId(), "user_id": user_ids[1]},
        ]
        relationship = Relationship(
            source_collection="orders", source_field="user_id", target_collection="users"
        )

        results = await resolver.resolve_batch(documents, [relationship])

        assert len(results) == 2
        assert results[0]["_relationships"]["user_id"]["name"] == "Alice"
        assert results[1]["_relationships"]["user_id"]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_resolve_batch_empty(self, resolver, mock_db):
        results = await resolver.resolve_batch([], [])
        assert results == []
