"""
Custom admin setup - registers collections
"""

async def setup_admin(engine):
    """Register collections - Monglo will auto-configure them"""
    
    # Register all collections
    # Monglo will automatically introspect schemas and detect relationships
    await engine.register_collection("users")
    await engine.register_collection("products")
    await engine.register_collection("orders")
    await engine.register_collection("categories")
