from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import random


async def seed_database(db: AsyncIOMotorDatabase):

    await db.users.delete_many({})
    await db.posts.delete_many({})
    await db.comments.delete_many({})
    await db.categories.delete_many({})
    await db.tags.delete_many({})
    await db.products.delete_many({})
    await db.orders.delete_many({})
    
    print("🗑️  Cleared existing data")
    
    # ==================== USERS ====================
    users_data = [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "role": "admin",
            "status": "active",
            "age": 28,
            "bio": "Full-stack developer passionate about Python and MongoDB",
            "joined_at": datetime.utcnow() - timedelta(days=365),
            "settings": {
                "theme": "dark",
                "notifications": True,
                "language": "en"
            },
            "tags": ["developer", "admin", "python"]
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "role": "editor",
            "status": "active",
            "age": 34,
            "bio": "Content creator and technical writer",
            "joined_at": datetime.utcnow() - timedelta(days=200),
            "settings": {
                "theme": "light",
                "notifications": True,
                "language": "en"
            },
            "tags": ["editor", "writer"]
        },
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "role": "user",
            "status": "active",
            "age": 25,
            "bio": "Tech enthusiast and blogger",
            "joined_at": datetime.utcnow() - timedelta(days=150),
            "settings": {
                "theme": "dark",
                "notifications": False,
                "language": "en"
            },
            "tags": ["blogger", "user"]
        },
        {
            "name": "David Brown",
            "email": "david@example.com",
            "role": "user",
            "status": "inactive",
            "age": 42,
            "bio": "Software architect",
            "joined_at": datetime.utcnow() - timedelta(days=500),
            "settings": {
                "theme": "light",
                "notifications": False,
                "language": "en"
            },
            "tags": ["architect", "inactive"]
        },
        {
            "name": "Eve Davis",
            "email": "eve@example.com",
            "role": "moderator",
            "status": "active",
            "age": 31,
            "bio": "Community manager and moderator",
            "joined_at": datetime.utcnow() - timedelta(days=300),
            "settings": {
                "theme": "dark",
                "notifications": True,
                "language": "en"
            },
            "tags": ["moderator", "community"]
        }
    ]
    
    result = await db.users.insert_many(users_data)
    user_ids = result.inserted_ids
    print(f"✅ Created {len(user_ids)} users")
    
    # ==================== CATEGORIES ====================
    categories_data = [
        {"name": "Technology", "slug": "technology", "description": "Tech news and tutorials"},
        {"name": "Programming", "slug": "programming", "description": "Coding tips and tricks"},
        {"name": "Database", "slug": "database", "description": "Database design and optimization"},
        {"name": "Web Development", "slug": "web-dev", "description": "Frontend and backend development"},
        {"name": "DevOps", "slug": "devops", "description": "CI/CD and cloud infrastructure"}
    ]
    
    result = await db.categories.insert_many(categories_data)
    category_ids = result.inserted_ids
    print(f"✅ Created {len(category_ids)} categories")
    
    # ==================== TAGS ====================
    tags_data = [
        {"name": "Python", "slug": "python", "color": "#3776ab"},
        {"name": "MongoDB", "slug": "mongodb", "color": "#47A248"},
        {"name": "FastAPI", "slug": "fastapi", "color": "#009688"},
        {"name": "React", "slug": "react", "color": "#61DAFB"},
        {"name": "Docker", "slug": "docker", "color": "#2496ED"},
        {"name": "Tutorial", "slug": "tutorial", "color": "#FF6B6B"},
        {"name": "Advanced", "slug": "advanced", "color": "#9B59B6"},
        {"name": "Beginner", "slug": "beginner", "color": "#2ECC71"}
    ]
    
    result = await db.tags.insert_many(tags_data)
    tag_ids = result.inserted_ids
    print(f"✅ Created {len(tag_ids)} tags")
    
    # ==================== POSTS ====================
    posts_data = [
        {
            "title": "Getting Started with MongoDB",
            "slug": "getting-started-mongodb",
            "content": "MongoDB is a powerful NoSQL database that stores data in flexible, JSON-like documents...",
            "excerpt": "Learn the basics of MongoDB in this comprehensive guide",
            "author_id": user_ids[0],
            "category_id": category_ids[2],
            "tag_ids": [tag_ids[1], tag_ids[5], tag_ids[7]],
            "status": "published",
            "views": 1250,
            "likes": 89,
            "published_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow() - timedelta(days=25),
            "featured": True,
            "metadata": {
                "reading_time": 8,
                "difficulty": "beginner",
                "series": "MongoDB Basics"
            }
        },
        {
            "title": "Building REST APIs with FastAPI",
            "slug": "building-rest-apis-fastapi",
            "content": "FastAPI is a modern, fast web framework for building APIs with Python...",
            "excerpt": "Create high-performance APIs using FastAPI and Python type hints",
            "author_id": user_ids[1],
            "category_id": category_ids[3],
            "tag_ids": [tag_ids[0], tag_ids[2], tag_ids[5]],
            "status": "published",
            "views": 2340,
            "likes": 156,
            "published_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow() - timedelta(days=18),
            "featured": True,
            "metadata": {
                "reading_time": 12,
                "difficulty": "intermediate",
                "series": "API Development"
            }
        },
        {
            "title": "Docker for Python Developers",
            "slug": "docker-python-developers",
            "content": "Containerization has become essential for modern application deployment...",
            "excerpt": "Learn how to containerize Python applications with Docker",
            "author_id": user_ids[0],
            "category_id": category_ids[4],
            "tag_ids": [tag_ids[0], tag_ids[4], tag_ids[6]],
            "status": "published",
            "views": 1890,
            "likes": 124,
            "published_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(days=14),
            "featured": False,
            "metadata": {
                "reading_time": 15,
                "difficulty": "advanced",
                "series": "DevOps Guide"
            }
        },
        {
            "title": "Advanced MongoDB Aggregations",
            "slug": "advanced-mongodb-aggregations",
            "content": "The aggregation pipeline is one of MongoDB's most powerful features...",
            "excerpt": "Master complex data transformations with MongoDB aggregation",
            "author_id": user_ids[2],
            "category_id": category_ids[2],
            "tag_ids": [tag_ids[1], tag_ids[6]],
            "status": "draft",
            "views": 0,
            "likes": 0,
            "published_at": None,
            "updated_at": datetime.utcnow() - timedelta(days=2),
            "featured": False,
            "metadata": {
                "reading_time": 20,
                "difficulty": "advanced",
                "series": "MongoDB Basics"
            }
        },
        {
            "title": "React Hooks Deep Dive",
            "slug": "react-hooks-deep-dive",
            "content": "React Hooks revolutionized how we write React components...",
            "excerpt": "Understand React Hooks and when to use them",
            "author_id": user_ids[1],
            "category_id": category_ids[3],
            "tag_ids": [tag_ids[3], tag_ids[6]],
            "status": "published",
            "views": 3200,
            "likes": 245,
            "published_at": datetime.utcnow() - timedelta(days=45),
            "updated_at": datetime.utcnow() - timedelta(days=40),
            "featured": True,
            "metadata": {
                "reading_time": 18,
                "difficulty": "advanced",
                "series": "React Mastery"
            }
        }
    ]
    
    result = await db.posts.insert_many(posts_data)
    post_ids = result.inserted_ids
    print(f"✅ Created {len(post_ids)} posts")
    
    # ==================== COMMENTS ====================
    comments_data = [
        {
            "content": "Great tutorial! Very helpful for beginners.",
            "author_id": user_ids[2],
            "post_id": post_ids[0],
            "created_at": datetime.utcnow() - timedelta(days=28),
            "likes": 12,
            "status": "approved"
        },
        {
            "content": "Can you add more examples about indexing?",
            "author_id": user_ids[3],
            "post_id": post_ids[0],
            "created_at": datetime.utcnow() - timedelta(days=27),
            "likes": 5,
            "status": "approved"
        },
        {
            "content": "FastAPI is amazing! Thanks for this guide.",
            "author_id": user_ids[0],
            "post_id": post_ids[1],
            "created_at": datetime.utcnow() - timedelta(days=18),
            "likes": 23,
            "status": "approved"
        },
        {
            "content": "This needs more detail on async/await.",
            "author_id": user_ids[4],
            "post_id": post_ids[1],
            "created_at": datetime.utcnow() - timedelta(days=17),
            "likes": 8,
            "status": "pending"
        },
        {
            "content": "Docker has been a game changer for our team!",
            "author_id": user_ids[2],
            "post_id": post_ids[2],
            "created_at": datetime.utcnow() - timedelta(days=14),
            "likes": 15,
            "status": "approved"
        },
        {
            "content": "React Hooks made my code so much cleaner.",
            "author_id": user_ids[3],
            "post_id": post_ids[4],
            "created_at": datetime.utcnow() - timedelta(days=42),
            "likes": 34,
            "status": "approved"
        },
        {
            "content": "When will part 2 be published?",
            "author_id": user_ids[4],
            "post_id": post_ids[4],
            "created_at": datetime.utcnow() - timedelta(days=39),
            "likes": 7,
            "status": "approved"
        }
    ]
    
    result = await db.comments.insert_many(comments_data)
    comment_ids = result.inserted_ids
    print(f"✅ Created {len(comment_ids)} comments")
    
    # ==================== PRODUCTS ====================
    products_data = [
        {
            "name": "MongoDB Pro License",
            "sku": "MONGO-PRO-001",
            "description": "Professional MongoDB license with advanced features",
            "price": 299.99,
            "stock": 100,
            "category": "Licenses",
            "tags": ["database", "license", "professional"],
            "status": "active",
            "rating": 4.8,
            "reviews_count": 156,
            "created_at": datetime.utcnow() - timedelta(days=180),
            "images": ["/images/mongodb-pro.png"],
            "attributes": {
                "type": "software",
                "duration": "1 year",
                "support": "24/7"
            }
        },
        {
            "name": "Python Course Bundle",
            "sku": "COURSE-PY-001",
            "description": "Complete Python programming course with certificates",
            "price": 149.99,
            "stock": 999,
            "category": "Education",
            "tags": ["python", "course", "education"],
            "status": "active",
            "rating": 4.9,
            "reviews_count": 432,
            "created_at": datetime.utcnow() - timedelta(days=120),
            "images": ["/images/python-course.png"],
            "attributes": {
                "type": "digital",
                "duration": "lifetime",
                "level": "all"
            }
        },
        {
            "name": "FastAPI Masterclass",
            "sku": "COURSE-FA-001",
            "description": "Build production-ready APIs with FastAPI",
            "price": 99.99,
            "stock": 999,
            "category": "Education",
            "tags": ["fastapi", "course", "api"],
            "status": "active",
            "rating": 4.7,
            "reviews_count": 234,
            "created_at": datetime.utcnow() - timedelta(days=90),
            "images": ["/images/fastapi-course.png"],
            "attributes": {
                "type": "digital",
                "duration": "lifetime",
                "level": "intermediate"
            }
        },
        {
            "name": "Developer Toolkit",
            "sku": "TOOLS-DEV-001",
            "description": "Essential tools for modern developers",
            "price": 49.99,
            "stock": 50,
            "category": "Tools",
            "tags": ["tools", "developer", "productivity"],
            "status": "active",
            "rating": 4.5,
            "reviews_count": 89,
            "created_at": datetime.utcnow() - timedelta(days=60),
            "images": ["/images/dev-tools.png"],
            "attributes": {
                "type": "software",
                "duration": "1 year",
                "platforms": ["windows", "mac", "linux"]
            }
        },
        {
            "name": "Cloud Deployment Guide",
            "sku": "BOOK-CD-001",
            "description": "Comprehensive guide to cloud deployments",
            "price": 29.99,
            "stock": 0,
            "category": "Books",
            "tags": ["cloud", "devops", "ebook"],
            "status": "out_of_stock",
            "rating": 4.6,
            "reviews_count": 67,
            "created_at": datetime.utcnow() - timedelta(days=200),
            "images": ["/images/cloud-book.png"],
            "attributes": {
                "type": "ebook",
                "pages": 320,
                "format": "PDF"
            }
        }
    ]
    
    result = await db.products.insert_many(products_data)
    product_ids = result.inserted_ids
    print(f"✅ Created {len(product_ids)} products")
    
    # ==================== ORDERS ====================
    orders_data = [
        {
            "order_number": "ORD-2024-001",
            "user_id": user_ids[0],
            "items": [
                {"product_id": product_ids[0], "quantity": 1, "price": 299.99},
                {"product_id": product_ids[1], "quantity": 1, "price": 149.99}
            ],
            "total": 449.98,
            "status": "completed",
            "payment_status": "paid",
            "payment_method": "credit_card",
            "shipping_address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94102",
                "country": "USA"
            },
            "created_at": datetime.utcnow() - timedelta(days=25),
            "completed_at": datetime.utcnow() - timedelta(days=23)
        },
        {
            "order_number": "ORD-2024-002",
            "user_id": user_ids[2],
            "items": [
                {"product_id": product_ids[2], "quantity": 1, "price": 99.99}
            ],
            "total": 99.99,
            "status": "completed",
            "payment_status": "paid",
            "payment_method": "paypal",
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Seattle",
                "state": "WA",
                "zip": "98101",
                "country": "USA"
            },
            "created_at": datetime.utcnow() - timedelta(days=15),
            "completed_at": datetime.utcnow() - timedelta(days=14)
        },
        {
            "order_number": "ORD-2024-003",
            "user_id": user_ids[1],
            "items": [
                {"product_id": product_ids[1], "quantity": 2, "price": 149.99},
                {"product_id": product_ids[3], "quantity": 1, "price": 49.99}
            ],
            "total": 349.97,
            "status": "processing",
            "payment_status": "paid",
            "payment_method": "credit_card",
            "shipping_address": {
                "street": "789 Pine Rd",
                "city": "Austin",
                "state": "TX",
                "zip": "73301",
                "country": "USA"
            },
            "created_at": datetime.utcnow() - timedelta(days=3),
            "completed_at": None
        },
        {
            "order_number": "ORD-2024-004",
            "user_id": user_ids[4],
            "items": [
                {"product_id": product_ids[3], "quantity": 1, "price": 49.99}
            ],
            "total": 49.99,
            "status": "pending",
            "payment_status": "pending",
            "payment_method": "bank_transfer",
            "shipping_address": {
                "street": "321 Elm St",
                "city": "Boston",
                "state": "MA",
                "zip": "02101",
                "country": "USA"
            },
            "created_at": datetime.utcnow() - timedelta(days=1),
            "completed_at": None
        }
    ]
    
    result = await db.orders.insert_many(orders_data)
    order_ids = result.inserted_ids
    print(f"✅ Created {len(order_ids)} orders")
    
    # Summary
    print("\n" + "="*70)
    print("🎉 Database seeded successfully!")
    print("="*70)
    print(f"📊 Collections created:")
    print(f"   • {len(user_ids)} users (with roles: admin, editor, moderator, user)")
    print(f"   • {len(post_ids)} posts (with categories and tags)")
    print(f"   • {len(comment_ids)} comments (linked to users and posts)")
    print(f"   • {len(category_ids)} categories")
    print(f"   • {len(tag_ids)} tags")
    print(f"   • {len(product_ids)} products (various statuses and prices)")
    print(f"   • {len(order_ids)} orders (with different statuses)")
    print("="*70)
    print("\n✨ Test all admin features:")
    print("   • Table views with sorting/filtering")
    print("   • Document editing with relationships")
    print("   • Search functionality")
    print("   • Pagination with different page sizes")
    print("   • Relationship navigation (posts → author, comments → post)")
    print("="*70 + "\n")
