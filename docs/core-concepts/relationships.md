# Understanding Relationships

Monglo's relationship detection is one of its most powerful features. It automatically discovers how your collections relate to each other.

---

## How It Works

Monglo uses **4 detection strategies** to find relationships:

### 1. Naming Conventions

Fields ending in `_id` or `_ids` are assumed to reference other collections.

```javascript
// MongoDB documents
{
  "title": "My  Post",
  "user_id": ObjectId("..."),      // → users._id
  "category_id": ObjectId("..."),  // → categories._id
  "tag_ids": [ObjectId("...")]     // → tags._id (one-to-many)
}
```

Monglo automatically:
- Strips `_id` suffix → `user`
- Pluralizes for collection name → `users`
- Detects relationship type (one-to-one vs many)

### 2. ObjectId Field Detection

Any field containing ObjectIds is checked against existing collections:

```javascript
{
  "author": ObjectId("..."),  // Checks if 'author' or 'authors' collection exists
  "owner": ObjectId("...")    // Checks if 'owner' or 'owners' collection exists
}
```

### 3. DBRef Support

Full support for MongoDB DBRef:

```javascript
{
  "author": {
    "$ref": "users",
    "$id": ObjectId("..."),
    "$db": "myapp"
  }
}
```

### 4. Manual Configuration

Override auto-detection:

```python
from monglo.core.config import CollectionConfig
from monglo.core.relationships import Relationship, RelationshipType

config = CollectionConfig(
    relationships=[
        Relationship(
            source_collection="posts",
            source_field="author",
            target_collection="users",
            target_field="_id",
            type=RelationshipType.ONE_TO_ONE,
            reverse_name="posts"  # For bidirectional navigation
        )
    ]
)

await engine.register_collection("posts", config=config)
```

---

## Relationship Types

### ONE_TO_ONE

Single reference to another document:

```javascript
// Order → User
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("123"),  // One user
  "total": 100
}
```

### ONE_TO_MANY

Array of references:

```javascript
// Post → Tags
{
  "_id": ObjectId("..."),
  "title": "My Post",
  "tag_ids": [              // Many tags
    ObjectId("tag1"),
    ObjectId("tag2")
  ]
}
```

### MANY_TO_ONE

Inverse of ONE_TO_MANY (represented by reverse relationships):

```javascript
// Tag → Posts (via reverse relationship)
// Automatically detected when Post has tag_ids
```

### EMBEDDED

Nested documents (not references):

```javascript
{
  "name": "John",
  "address": {              // Embedded document
    "street": "123 Main St",
    "city": "NYC"
  }
}
```

---

## Resolution

### Basic Resolution

```python
from monglo.core.relationships import RelationshipResolver

resolver = RelationshipResolver(db)
collection_admin = engine.registry.get("orders")

order = await collection_admin.collection.find_one()
resolved = await resolver.resolve(order, collection_admin.relationships, depth=1)

print(resolved["_relationships"]["user_id"])  # User document populated
```

Output:
```python
{
  "_id": ObjectId("order1"),
  "user_id": ObjectId("user1"),
  "total": 100,
  "_relationships": {
    "user_id": {
      "_id": ObjectId("user1"),
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

### Nested Resolution (Depth)

```python
# comment -> post -> user
resolved = await resolver.resolve(comment, relationships, depth=2)

# Resolves:
# - comment.post_id → post document
# - post.user_id → user document
```

### Batch Resolution

Avoids N+1 queries:

```python
posts = await db.posts.find().to_list(100)
resolved_posts = await resolver.resolve_batch(posts, relationships, depth=1)

# Makes 1 query to fetch all referenced users, not 100!
```

---

## Examples

### Auto-Detection Example

```python
# Your MongoDB data
await db.users.insert_one({"_id": ObjectId("user1"), "name": "Alice"})
await db.posts.insert_one({
    "title": "Hello World",
    "user_id": ObjectId("user1")  # Relationship field
})

# Monglo automatically detects this!
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()

posts_admin = engine.registry.get("posts")
print(posts_admin.relationships)
# [Relationship(source_field="user_id", target_collection="users", ...)]
```

### Manual Override

```python
# Disable auto-detection for specific collection
engine = MongloEngine(database=db, relationship_detection="manual")

# Define relationships explicitly
config = CollectionConfig(
    relationships=[
        Relationship(
            source_collection="orders",
            source_field="customer",  # Not _id suffix
            target_collection="users",
            type=RelationshipType.ONE_TO_ONE
        )
    ]
)

await engine.register_collection("orders", config=config)
```

### Bidirectional Relationships

```python
# Define reverse relationship
config = CollectionConfig(
    relationships=[
        Relationship(
            source_collection="posts",
            source_field="user_id",
            target_collection="users",
            type=RelationshipType.ONE_TO_ONE,
            reverse_name="posts"  # Users can navigate to their posts
        )
    ]
)
```

---

## UI Visualization

Relationships are visualized in the admin UI:

1. **Table View** - Related fields show as links
2. **Document View** - Click to navigate to related documents
3. **Relationship Graph** - D3.js visualization of all relationships (coming soon)

---

## Performance

### Indexing

Monglo recommends creating indexes on relationship fields:

```python
# Create indexes for better performance
await db.posts.create_index("user_id")
await db.orders.create_index("customer_id")
```

### Batch Queries

Monglo uses batch queries to avoid N+1 problems:

```python
# Fetches 100 posts
posts = await crud.list(per_page=100)

# Resolves all user relationships in 1 query, not 100!
# MongoDB: db.users.find({_id: {$in: [all_user_ids]}})
```

---

## Best Practices

1. **Use Naming Conventions** - `user_id`, `category_id` for auto-detection
2. **Create Indexes** - On all relationship fields
3. **Limit Depth** - Don't resolve too deeply (depth=1 or 2 is usually enough)
4. **Batch Resolution** - Use `resolve_batch` for multiple documents

---

## Next Steps

- [Custom Fields](../guides/custom-fields.md) - Define field types
- [Views](views.md) - Table and document views
- [API Reference](../api-reference/engine.md) - Engine documentation
