from monglo import MongloEngine, ModelAdmin

#CUSTOM ADMIN CLASSES

class UserAdmin(ModelAdmin):
    """Custom admin for Users collection"""
    
    # Display name in sidebar
    display_name = "Users"
    
    # Fields to display in list view
    list_display = ["email", "full_name", "role", "is_active", "created_at"]
    
    # Fields to search
    search_fields = ["email", "username", "full_name"]
    
    # Default sort
    default_sort = [("created_at", -1)]  # Newest first
    
    # Items per page
    per_page = 20


class CategoryAdmin(ModelAdmin):
    """Custom admin for Categories"""
    
    display_name = "Categories"
    list_display = ["name", "slug", "icon"]
    search_fields = ["name", "slug"]
    default_sort = [("name", 1)]
    per_page = 50


class ProductAdmin(ModelAdmin):
    """Custom admin for Products with advanced config"""
    
    display_name = "Products"
    list_display = ["sku", "name", "price", "stock", "is_active", "is_featured"]
    search_fields = ["name", "sku", "description"]
    default_sort = [("created_at", -1)]
    per_page = 25
    

class OrderAdmin(ModelAdmin):
    """Custom admin for Orders"""
    
    display_name = "Orders"
    list_display = ["order_number", "user_id", "status", "total", "created_at"]
    search_fields = ["order_number", "tracking_number"]
    default_sort = [("created_at", -1)]
    per_page = 20
    

class ReviewAdmin(ModelAdmin):
    """Custom admin for Product Reviews"""
    
    display_name = "Reviews"
    list_display = ["title", "rating", "user_id", "product_id", "verified_purchase"]
    search_fields = ["title", "comment"]
    default_sort = [("created_at", -1)]
    per_page = 30
    

# SETUP FUNCTION

async def setup_admin(engine: MongloEngine):
    """
    Configure custom admin classes for collections
    
    This function registers custom ModelAdmin classes that define:
    - Display names and icons
    - List view columns
    - Search fields
    - Default sorting
    - Pagination settings
    - Field schemas
    """
    
    # Register custom admin classes
    registry = engine.registry
    
    # Users
    registry.register("users", UserAdmin)
    
    # Categories  
    registry.register("categories", CategoryAdmin)
    
    # Products
    registry.register("products", ProductAdmin)
    
    # Orders
    registry.register("orders", OrderAdmin)
    
    # Reviews
    registry.register("reviews", ReviewAdmin)
    
    print("✅ Custom admin configurations registered")
    print(f"   - {len(registry._collections)} collections with custom admin")
