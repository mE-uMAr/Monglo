"""
E-Commerce Database - Advanced Example
Comprehensive data seeding with relationships and realistic data
"""

from datetime import datetime, timedelta
from bson import ObjectId
import random

async def seed_database(db):
    """Seed database with realistic e-commerce data"""
    
    # Clear existing data
    collections = await db.list_collection_names()
    for coll in collections:
        await db[coll].delete_many({})
    
    print("🌱 Seeding database...")
    
    #  USERS
    users_data = [
        {
            "_id": ObjectId(),
            "email": "john.doe@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "role": "customer",
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow() - timedelta(days=180),
            "last_login": datetime.utcnow() - timedelta(hours=2),
            "avatar_url": "https://i.pravatar.cc/150?img=12",
            "phone": "+1-555-0123",
            "preferences": {
                "newsletter": True,
                "notifications": {"email": True, "sms": False},
                "theme": "dark"
            }
        },
        {
            "_id": ObjectId(),
            "email": "jane.smith@example.com",
            "username": "janesmith",
            "full_name": "Jane Smith",
            "role": "admin",
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow() - timedelta(days=365),
            "last_login": datetime.utcnow() - timedelta(minutes=15),
            "avatar_url": "https://i.pravatar.cc/150?img=5",
            "phone": "+1-555-0124",
            "preferences": {
                "newsletter": True,
                "notifications": {"email": True, "sms": True},
                "theme": "light"
            }
        },
        {
            "_id": ObjectId(),
            "email": "bob.wilson@example.com",
            "username": "bobwilson",
            "full_name": "Bob Wilson",
            "role": "customer",
            "is_active": True,
            "email_verified": False,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "last_login": datetime.utcnow() - timedelta(days=5),
            "avatar_url": "https://i.pravatar.cc/150?img=33",
            "phone": "+1-555-0125",
            "preferences": {
                "newsletter": False,
                "notifications": {"email": False, "sms": False},
                "theme": "auto"
            }
        }
    ]
    
    await db.users.insert_many(users_data)
    user_ids = [u["_id"] for u in users_data]
    print(f"✅ Created {len(users_data)} users")
    
    #   CATEGORIES  
    categories_data = [
        {"_id": ObjectId(), "name": "Electronics", "slug": "electronics", "description": "Electronic devices and gadgets", "icon": "💻"},
        {"_id": ObjectId(), "name": "Clothing", "slug": "clothing", "description": "Fashion and apparel", "icon": "👕"},
        {"_id": ObjectId(), "name": "Books", "slug": "books", "description": "Books and literature", "icon": "📚"},
        {"_id": ObjectId(), "name": "Home & Garden", "slug": "home-garden", "description": "Home improvement and garden supplies", "icon": "🏡"},
        {"_id": ObjectId(), "name": "Sports", "slug": "sports", "description": "Sports equipment and gear", "icon": "⚽"},
    ]
    
    await db.categories.insert_many(categories_data)
    category_ids = [c["_id"] for c in categories_data]
    print(f"✅ Created {len(categories_data)} categories")
    
    #   PRODUCTS  
    products_data = [
        {
            "_id": ObjectId(),
            "name": "Wireless Headphones Pro",
            "sku": "WH-PRO-001",
            "description": "Premium wireless headphones with active noise cancellation",
            "price": 299.99,
            "cost": 150.00,
            "category_id": category_ids[0],
            "stock": 45,
            "images": ["https://picsum.photos/seed/prod1/400/400", "https://picsum.photos/seed/prod1b/400/400"],
            "tags": ["wireless", "audio", "premium"],
            "specifications": {
                "battery_life": "30 hours",
                "weight": "250g",
                "color": "Black",
                "warranty": "2 years"
            },
            "is_featured": True,
            "is_active": True,
            "rating": 4.5,
            "reviews_count": 128,
            "created_at": datetime.utcnow() - timedelta(days=90)
        },
        {
            "_id": ObjectId(),
            "name": "Smart Watch Series 5",
            "sku": "SW-005",
            "description": "Advanced fitness tracking and notifications",
            "price": 399.99,
            "cost": 200.00,
            "category_id": category_ids[0],
            "stock": 23,
            "images": ["https://picsum.photos/seed/prod2/400/400"],
            "tags": ["wearable", "fitness", "smart"],
            "specifications": {
                "battery_life": "48 hours",
                "display": "AMOLED",
                "water_resistant": "5 ATM"
            },
            "is_featured": True,
            "is_active": True,
            "rating": 4.7,
            "reviews_count": 95,
            "created_at": datetime.utcnow() - timedelta(days=60)
        },
        {
            "_id": ObjectId(),
            "name": "Cotton T-Shirt - Blue",
            "sku": "TS-BLU-M",
            "description": "100% organic cotton t-shirt",
            "price": 29.99,
            "cost": 8.00,
            "category_id": category_ids[1],
            "stock": 150,
            "images": ["https://picsum.photos/seed/prod3/400/400"],
            "tags": ["clothing", "cotton", "casual"],
            "specifications": {
                "size": "Medium",
                "material": "100% Cotton",
                "care": "Machine washable"
            },
            "is_featured": False,
            "is_active": True,
            "rating": 4.2,
            "reviews_count": 34,
            "created_at": datetime.utcnow() - timedelta(days=120)
        },
        {
            "_id": ObjectId(),
            "name": "JavaScript: The Definitive Guide",
            "sku": "BK-JS-001",
            "description": "Comprehensive JavaScript programming guide",
            "price": 59.99,
            "cost": 25.00,
            "category_id": category_ids[2],
            "stock": 67,
            "images": ["https://picsum.photos/seed/prod4/400/400"],
            "tags": ["programming", "javascript", "book"],
            "specifications": {
                "author": "David Flanagan",
                "pages": 706,
                "publisher": "O'Reilly",
                "edition": "7th"
            },
            "is_featured": True,
            "is_active": True,
            "rating": 4.8,
            "reviews_count": 412,
            "created_at": datetime.utcnow() - timedelta(days=200)
        },
        {
            "_id": ObjectId(),
            "name": "Yoga Mat Premium",
            "sku": "YM-PREM-001",
            "description": "Eco-friendly non-slip yoga mat",
            "price": 49.99,
            "cost": 15.00,
            "category_id": category_ids[4],
            "stock": 0,  # Out of stock
            "images": ["https://picsum.photos/seed/prod5/400/400"],
            "tags": ["yoga", "fitness", "eco-friendly"],
            "specifications": {
                "thickness": "6mm",
                "material": "TPE",
                "size": "183cm x 61cm"
            },
            "is_featured": False,
            "is_active": False,  # Inactive
            "rating": 4.6,
            "reviews_count": 78,
            "created_at": datetime.utcnow() - timedelta(days=150)
        }
    ]
    
    await db.products.insert_many(products_data)
    product_ids = [p["_id"] for p in products_data]
    print(f"✅ Created {len(products_data)} products")
    
    #   ORDERS  
    orders_data = [
        {
            "_id": ObjectId(),
            "order_number": "ORD-2024-001",
            "user_id": user_ids[0],
            "status": "delivered",
            "items": [
                {
                    "product_id": product_ids[0],
                    "product_name": "Wireless Headphones Pro",
                    "quantity": 1,
                    "price": 299.99,
                    "subtotal": 299.99
                },
                {
                    "product_id": product_ids[3],
                    "product_name": "JavaScript: The Definitive Guide",
                    "quantity": 2,
                    "price": 59.99,
                    "subtotal": 119.98
                }
            ],
            "subtotal": 419.97,
            "tax": 33.60,
            "shipping": 10.00,
            "total": 463.57,
            "shipping_address": {
                "full_name": "John Doe",
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "payment_method": "credit_card",
            "payment_status": "paid",
            "tracking_number": "TRK123456789",
            "notes": "Please ring doorbell",
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(days=10),
            "delivered_at": datetime.utcnow() - timedelta(days=10)
        },
        {
            "_id": ObjectId(),
            "order_number": "ORD-2024-002",
            "user_id": user_ids[2],
            "status": "processing",
            "items": [
                {
                    "product_id": product_ids[1],
                    "product_name": "Smart Watch Series 5",
                    "quantity": 1,
                    "price": 399.99,
                    "subtotal": 399.99
                }
            ],
            "subtotal": 399.99,
            "tax": 32.00,
            "shipping": 0.00,  # Free shipping
            "total": 431.99,
            "shipping_address": {
                "full_name": "Bob Wilson",
                "street": "456 Oak Ave",
                "city": "Los Angeles",
                "state": "CA",
                "zip": "90001",
                "country": "USA"
            },
            "payment_method": "paypal",
            "payment_status": "paid",
            "tracking_number": None,
            "notes": None,
            "created_at": datetime.utcnow() - timedelta(days=2),
            "updated_at": datetime.utcnow() - timedelta(hours=12),
            "delivered_at": None
        },
        {
            "_id": ObjectId(),
            "order_number": "ORD-2024-003",
            "user_id": user_ids[0],
            "status": "pending",
            "items": [
                {
                    "product_id": product_ids[2],
                    "product_name": "Cotton T-Shirt - Blue",
                    "quantity": 3,
                    "price": 29.99,
                    "subtotal": 89.97
                }
            ],
            "subtotal": 89.97,
            "tax": 7.20,
            "shipping": 5.99,
            "total": 103.16,
            "shipping_address": {
                "full_name": "John Doe",
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "payment_method": "credit_card",
            "payment_status": "pending",
            "tracking_number": None,
            "notes": None,
            "created_at": datetime.utcnow() - timedelta(hours=3),
            "updated_at": datetime.utcnow() - timedelta(hours=3),
            "delivered_at": None
        }
    ]
    
    await db.orders.insert_many(orders_data)
    print(f"✅ Created {len(orders_data)} orders")
    
    #   REVIEWS  
    reviews_data = [
        {
            "_id": ObjectId(),
            "product_id": product_ids[0],
            "user_id": user_ids[0],
            "rating": 5,
            "title": "Amazing sound quality!",
            "comment": "Best headphones I've ever owned. The noise cancellation is phenomenal.",
            "verified_purchase": True,
            "helpful_count": 23,
            "created_at": datetime.utcnow() - timedelta(days=12)
        },
        {
            "_id": ObjectId(),
            "product_id": product_ids[1],
            "user_id": user_ids[2],
            "rating": 4,
            "title": "Great fitness tracker",
            "comment": "Love all the features. Battery life could be better.",
            "verified_purchase": True,
            "helpful_count": 8,
            "created_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "_id": ObjectId(),
            "product_id": product_ids[3],
            "user_id": user_ids[0],
            "rating": 5,
            "title": "Must-read for JS developers",
            "comment": "Comprehensive and well-written. Covers ES2020 features thoroughly.",
            "verified_purchase": True,
            "helpful_count": 45,
            "created_at": datetime.utcnow() - timedelta(days=20)
        }
    ]
    
    await db.reviews.insert_many(reviews_data)
    print(f"✅ Created {len(reviews_data)} reviews")
    
    print("🎉 Database seeding completed!")
    print(f"   - {len(users_data)} users")
    print(f"   - {len(categories_data)} categories")
    print(f"   - {len(products_data)} products")
    print(f"   - {len(orders_data)} orders")
    print(f"   - {len(reviews_data)} reviews")
