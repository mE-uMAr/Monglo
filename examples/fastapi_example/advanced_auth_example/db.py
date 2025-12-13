"""
Database seeding for advanced auth example
Creates users, products, and orders with relationships
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


async def seed_database(db: AsyncIOMotorDatabase):
    """Seed database with example data"""
    
    print("🌱 Seeding database...")
    
    # Clear existing data
    await db.users.delete_many({})
    await db.products.delete_many({})
    await db.orders.delete_many({})
    await db.categories.delete_many({})
    
    # USERS
    # Create admin user with hashed password for authentication
    import hashlib
    
    def hash_password(password: str) -> str:
        """Hash password using SHA256 (for demo - use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    users_data = [
        {
            "_id": ObjectId(),
            "name": "Admin User",
            "email": "admin@example.com",
            "hashed_password": hash_password("admin123"),  # Password: admin123
            "role": "admin",
            "status": "active",
            "created_at": "2024-01-01"
        },
        {
            "_id": ObjectId(),
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "hashed_password": hash_password("alice123"),  # Password: alice123
            "role": "customer",
            "status": "active",
            "created_at": "2024-01-15"
        },
        {
            "_id": ObjectId(),
            "name": "Bob Smith",
            "email": "bob@example.com",
            "hashed_password": hash_password("bob123"),  # Password: bob123
            "role": "customer",
            "status": "active",
            "created_at": "2024-02-20"
        },
        {
            "_id": ObjectId(),
            "name": "Charlie Manager",
            "email": "charlie@example.com",
            "hashed_password": hash_password("charlie123"),  # Password: charlie123
            "role": "admin",
            "status": "active",
            "created_at": "2024-01-01"
        }
    ]
    
    await db.users.insert_many(users_data)
    user_ids = [u["_id"] for u in users_data]
    print(f"✅ Created {len(users_data)} users")
    print(f"   🔐 Admin credentials: admin@example.com / admin123")

    
    # CATEGORIES
    categories_data = [
        {"_id": ObjectId(), "name": "Electronics", "slug": "electronics"},
        {"_id": ObjectId(), "name": "Books", "slug": "books"},
        {"_id": ObjectId(), "name": "Clothing", "slug": "clothing"},
    ]
    
    await db.categories.insert_many(categories_data)
    category_ids = [c["_id"] for c in categories_data]
    print(f"✅ Created {len(categories_data)} categories")
    
    # PRODUCTS
    products_data = [
        {
            "_id": ObjectId(),
            "name": "Laptop",
            "price": 999.99,
            "category_id": category_ids[0],
            "stock": 50,
            "status": "active"
        },
        {
            "_id": ObjectId(),
            "name": "Python Book",
            "price": 29.99,
            "category_id": category_ids[1],
            "stock": 100,
            "status": "active"
        },
        {
            "_id": ObjectId(),
            "name": "T-Shirt",
            "price": 19.99,
            "category_id": category_ids[2],
            "stock": 200,
            "status": "active"
        }
    ]
    
    await db.products.insert_many(products_data)
    product_ids = [p["_id"] for p in products_data]
    print(f"✅ Created {len(products_data)} products")
    
    # ORDERS
    orders_data = [
        {
            "_id": ObjectId(),
            "user_id": user_ids[0],
            "order_number": "ORD-001",
            "status": "completed",
            "total": 1029.98,
            "items": [
                {"product_id": product_ids[0], "quantity": 1, "price": 999.99},
                {"product_id": product_ids[1], "quantity": 1, "price": 29.99}
            ],
            "created_at": "2024-03-01"
        },
        {
            "_id": ObjectId(),
            "user_id": user_ids[1],
            "order_number": "ORD-002",
            "status": "pending",
            "total": 19.99,
            "items": [
                {"product_id": product_ids[2], "quantity": 1, "price": 19.99}
            ],
            "created_at": "2024-03-10"
        }
    ]
    
    await db.orders.insert_many(orders_data)
    print(f"✅ Created {len(orders_data)} orders")
    
    print("✨ Database seeding complete!")
