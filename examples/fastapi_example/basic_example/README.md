# FastAPI Example - Monglo Admin

A complete example demonstrating Monglo Admin with FastAPI, including seeded data with relationships.

## What's Included

### Collections

The example creates **7 collections** with realistic data:

1. **users** (5 records) - User accounts with roles (admin, editor, moderator, user)
2. **posts** (5 records) - Blog posts with author relationships, categories, and tags
3. **comments** (7 records) - Comments linked to posts and users
4. **categories** (5 records) - Post categories  
5. **tags** (8 records) - Post tags (many-to-many relationship via post.tag_ids)
6. **products** (5 records) - E-commerce products with various statuses
7. **orders** (4 records) - Customer orders with user and product relationships

### Relationships

- `posts.author_id` → `users._id` (one-to-many)
- `posts.category_id` → `categories._id` (many-to-one)
- `posts.tag_ids` → `tags._id` (many-to-many)
- `comments.author_id` → `users._id` (many-to-one)
- `comments.post_id` → `posts._id` (many-to-one)
- `orders.user_id` → `users._id` (many-to-one)
- `orders.items[].product_id` → `products._id` (embedded many-to-one)

## Running the Example

1. **Start MongoDB** (ensure MongoDB is running on `localhost:27017`)

2. **Install dependencies**:
   ```bash
   pip install fastapi motor uvicorn
   ```

3. **Run the application**:
   ```bash
   python app.py
   # or
   fastapi dev app.py
   ```

4. **Open the admin interface**:
   - Admin UI: http://localhost:8000/admin
   - API Docs: http://localhost:8000/docs
   - API: http://localhost:8000/api

## Features to Test

### Table Views
- ✅ Sort by any column (click headers)
- ✅ Search across multiple fields
- ✅ Pagination with customizable page size
- ✅ Filter by status, role, etc.

### Document Views
- ✅ View detailed document information
- ✅ Edit documents with validation
- ✅ Navigate relationships (click author to see user, etc.)
- ✅ See nested objects and arrays

### CRUD Operations
- ✅ Create new documents via the UI
- ✅ Edit existing documents
- ✅ Delete documents
- ✅ Bulk operations

### Relationships
- ✅ Click `author_id` in posts to navigate to the user
- ✅ Click `post_id` in comments to navigate to the post
- ✅ See related data in context

## Data Seeding

The `db.py` file seeds the database on every startup. To **preserve data** between restarts:

```python
# Comment out this line in app.py after first run:
# await seed_database(db)
```

## Code Structure

```
fastapi_example/
├── app.py          # Main FastAPI application (minimal - just 37 lines!)
├── db.py           # Database seeding script with example data
└── README.md       # This file
```

## Minimal Code

The entire application is just **~25 lines of actual code**:

```python
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from monglo import MongloEngine
from monglo.ui_helpers.fastapi import setup_ui
from monglo.adapters.fastapi import create_fastapi_router
from db import seed_database

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_demo

app = FastAPI(title="Monglo Admin")
engine = MongloEngine(database=db, auto_discover=True)

@app.on_event("startup")
async def startup():
    await engine.initialize()
    await seed_database(db)  # Seed example data
    
    setup_ui(app, engine)  # Setup admin UI (handles everything!)
    app.include_router(create_fastapi_router(engine, prefix="/api"))

@app.on_event("shutdown")
async def shutdown():
    client.close()
```

That's it! **No templates, no forms, no route definitions** - Monglo handles everything automatically!
