# E-Commerce Admin - Advanced Example

A comprehensive example demonstrating Monglo's advanced features with a modular, production-ready architecture.

## 🏗️ Architecture

```
advanced_example/
├── app.py           # Main FastAPI application
├── admin_setup.py   # Custom admin configurations
├── db.py           # Database seeding
└── README.md       # This file
```

## ✨ Features Demonstrated

### 1. **Modular Structure**
- Separated concerns: app, admin config, database
- Easy to maintain and extend
- Production-ready organization

### 2. **Custom Admin Classes**
Each collection has a custom `ModelAdmin` class with:
- 🎨 **Custom display names** with emojis
- 📋 **List display** - which columns to show
- 🔍 **Search fields** - searchable columns
- 🔄 **Default sorting** - newest first, alphabetical, etc.
- 📄 **Pagination** - items per page
- 📝 **Field schemas** - proper types for forms

### 3. **Realistic E-Commerce Data**
- **Users** with roles, preferences, avatars
- **Categories** with slugs and icons
- **Products** with nested specs, images, tags
- **Orders** with embedded items and addresses
- **Reviews** with ratings and verification

### 4. **Advanced Relationships**
- `Orders.user_id` → `Users`
- `Orders.items[].product_id` → `Products` (embedded)
- `Products.category_id` → `Categories`
- `Reviews.user_id` → `Users`
- `Reviews.product_id` → `Products`

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi motor monglo uvicorn
```

### 2. Start MongoDB
```bash
# Using Docker
docker run -d -p 27017:27017 mongo:latest

# Or use your local MongoDB
mongod
```

### 3. Run the App
```bash
cd examples/advanced_example
python app.py
```

### 4. Access Admin Panel
Open your browser to:
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000

## 📚 Code Highlights

### Custom Admin Class Example
```python
class ProductAdmin(ModelAdmin):
    display_name = "🛍️ Products"
    list_display = ["sku", "name", "price", "stock", "is_active"]
    search_fields = ["name", "sku", "description"]
    default_sort = [("created_at", -1)]
    per_page = 25
    
    fields = {
        "name": StringField(required=True),
        "price": FloatField(required=True),
        "stock": IntField(default=0),
        # ... more fields
    }
```

### Registration
```python
async def setup_admin(engine):
    registry = engine.registry
    registry.register("products", ProductAdmin)
    registry.register("users", UserAdmin)
    # ... more registrations
```

### Main App
```python
@app.on_event("startup")
async def startup():
    await seed_database(db)
    await engine.initialize()
    await setup_admin(engine)
    setup_ui(app, engine=engine, title="E-Commerce Admin")
```

## 🎯 What You'll Learn

1. **Modular Architecture** - Separate files for different concerns
2. **Custom Configurations** - Tailor admin for your needs
3. **Field Definitions** - Proper typing for forms
4. **Relationship Handling** - Both direct and embedded
5. **Search & Filter** - Make data discoverable
6. **Branding** - Custom colors and titles

## 💡 Customization

### Add New Collection
1. Add data in `db.py`
2. Create admin class in `admin_setup.py`
3. Register in `setup_admin()`

### Modify Display
Edit the `list_display` in your admin class:
```python
list_display = ["field1", "field2", "field3"]
```

### Change Search
Edit the `search_fields`:
```python
search_fields = ["name", "email", "description"]
```

### Adjust Branding
In `app.py`:
```python
setup_ui(
    app,
    engine=engine,
    title="My App",
    brand_color="#FF5722"
)
```

## 📖 Next Steps

- Add custom filters
- Implement bulk actions
- Add export functionality
- Create custom views
- Add authentication

## 🔗 Resources

- [Monglo Documentation](../../README.md)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [MongoDB Motor](https://motor.readthedocs.io)
