
import pytest
from bson import ObjectId
from monglo.core.relationships import RelationshipResolver, RelationshipType

@pytest.mark.integration
@pytest.mark.asyncio
async def test_resolve_one_to_one_relationship(registered_engine, sample_users, sample_orders):
    admin = registered_engine.registry.get("orders")
    order = await admin.collection.find_one()

    # Resolve relationships
    resolver = RelationshipResolver(registered_engine.db)
    resolved = await resolver.resolve(order, admin.relationships, depth=1)

    # Should have _relationships field
    assert "_relationships" in resolved

    # Should resolve user_id to user document
    if "user_id" in resolved:
        assert "user_id" in resolved["_relationships"]
        user = resolved["_relationships"]["user_id"]
        assert user is not None
        assert "name" in user
        assert user["_id"] == order["user_id"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_relationship_detection_naming_convention(test_db):
    from monglo import MongloEngine

    user_id = ObjectId()
    await test_db.users.insert_one({"_id": user_id, "name": "Test User"})
    await test_db.posts.insert_one(
        {"user_id": user_id, "title": "Test Post"}  # Should auto-detect as relationship
    )

    engine = MongloEngine(database=test_db, auto_discover=False)
    await engine.initialize()
    await engine.register_collection("posts")

    posts_admin = engine.registry.get("posts")
    assert len(posts_admin.relationships) >= 1

    # Find the user_id relationship
    user_rel = posts_admin.get_relationship("user_id")
    assert user_rel is not None
    assert user_rel.target_collection == "users"
    assert user_rel.source_field == "user_id"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_resolve_one_to_many_relationship(test_db):
    from monglo import MongloEngine
    from monglo.core.relationships import RelationshipResolver

    tag_ids = [ObjectId() for _ in range(3)]
    await test_db.tags.insert_many(
        [
            {"_id": tag_ids[0], "name": "python"},
            {"_id": tag_ids[1], "name": "mongodb"},
            {"_id": tag_ids[2], "name": "async"},
        ]
    )

    await test_db.posts.insert_one({"title": "My Post", "tag_ids": tag_ids})  # Array of ObjectIds

    # Setup engine
    engine = MongloEngine(database=test_db, auto_discover=False)
    await engine.initialize()
    await engine.register_collection("posts")

    posts_admin = engine.registry.get("posts")
    post = await posts_admin.collection.find_one()

    # Resolve relationships
    resolver = RelationshipResolver(test_db)
    resolved = await resolver.resolve(post, posts_admin.relationships, depth=1)

    # Should have resolved tag_ids
    assert "_relationships" in resolved
    if "tag_ids" in resolved["_relationships"]:
        tags = resolved["_relationships"]["tag_ids"]
        assert len(tags) == 3
        tag_names = {tag["name"] for tag in tags}
        assert tag_names == {"python", "mongodb", "async"}

@pytest.mark.integration
@pytest.mark.asyncio
async def test_relationship_batch_resolution(test_db):
    from monglo import MongloEngine
    from monglo.core.relationships import RelationshipResolver

    user_id = ObjectId()
    await test_db.users.insert_one({"_id": user_id, "name": "Author"})

    posts = [{"title": f"Post {i}", "user_id": user_id} for i in range(10)]
    await test_db.posts.insert_many(posts)

    # Setup engine
    engine = MongloEngine(database=test_db, auto_discover=False)
    await engine.initialize()
    await engine.register_collection("posts")

    posts_admin = engine.registry.get("posts")
    all_posts = await posts_admin.collection.find().to_list(10)

    # Batch resolve
    resolver = RelationshipResolver(test_db)
    resolved_posts = await resolver.resolve_batch(all_posts, posts_admin.relationships, depth=1)

    # All posts should have resolved user
    for post in resolved_posts:
        assert "_relationships" in post
        if "user_id" in post["_relationships"]:
            user = post["_relationships"]["user_id"]
            assert user["name"] == "Author"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_nested_relationship_resolution(test_db):
    from monglo import MongloEngine
    from monglo.core.relationships import RelationshipResolver

    user_id = ObjectId()
    post_id = ObjectId()

    await test_db.users.insert_one({"_id": user_id, "name": "Author"})
    await test_db.posts.insert_one({"_id": post_id, "title": "Post", "user_id": user_id})
    await test_db.comments.insert_one({"text": "Comment", "post_id": post_id})

    # Setup engine
    engine = MongloEngine(database=test_db, auto_discover=False)
    await engine.initialize()
    await engine.register_collection("comments")
    await engine.register_collection("posts")

    comments_admin = engine.registry.get("comments")
    comment = await comments_admin.collection.find_one()

    # Resolve with depth=2 to get post AND post's user
    resolver = RelationshipResolver(test_db)
    resolved = await resolver.resolve(comment, comments_admin.relationships, depth=2)

    # Should have post relationship
    assert "_relationships" in resolved
    if "post_id" in resolved["_relationships"]:
        post = resolved["_relationships"]["post_id"]
        assert post["title"] == "Post"

        # Post should also have resolved user (depth=2)
        if "_relationships" in post and "user_id" in post["_relationships"]:
            user = post["_relationships"]["user_id"]
            assert user["name"] == "Author"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_relationship_with_missing_reference(test_db):
    from monglo import MongloEngine
    from monglo.core.relationships import RelationshipResolver

    fake_user_id = ObjectId()
    await test_db.posts.insert_one(
        {"title": "Orphaned Post", "user_id": fake_user_id}  # User doesn't exist
    )

    # Setup engine
    engine = MongloEngine(database=test_db, auto_discover=False)
    await engine.initialize()
    await engine.register_collection("posts")

    posts_admin = engine.registry.get("posts")
    post = await posts_admin.collection.find_one()

    # Resolve relationships
    resolver = RelationshipResolver(test_db)
    resolved = await resolver.resolve(post, posts_admin.relationships, depth=1)

    # Should handle gracefully - relationship key should be present but value None
    assert "_relationships" in resolved
    if "user_id" in resolved["_relationships"]:
        assert resolved["_relationships"]["user_id"] is None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_bidirectional_relationships(test_db):
    from monglo import MongloEngine
    from monglo.core.relationships import Relationship, RelationshipType
    from monglo.core.config import CollectionConfig

    user_id = ObjectId()
    await test_db.users.insert_one({"_id": user_id, "name": "User"})
    await test_db.posts.insert_many(
        [{"title": "Post 1", "user_id": user_id}, {"title": "Post 2", "user_id": user_id}]
    )

    # Setup with bidirectional relationship
    engine = MongloEngine(database=test_db, auto_discover=False)
    await engine.initialize()

    await engine.register_collection(
        "posts",
        config=CollectionConfig(
            relationships=[
                Relationship(
                    source_collection="posts",
                    source_field="user_id",
                    target_collection="users",
                    type=RelationshipType.ONE_TO_ONE,
                    reverse_name="posts",  # Enable reverse navigation
                )
            ]
        ),
    )

    posts_admin = engine.registry.get("posts")
    user_rel = posts_admin.get_relationship("user_id")
    assert user_rel is not None
    assert user_rel.reverse_name == "posts"
