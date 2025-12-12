"""
Collection registry and administration for Monglo.

This module provides the registry system for managing MongoDB collections
and their administrative interfaces.
"""

from dataclasses import dataclass, field
from typing import Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from .config import CollectionConfig
from .relationships import Relationship


@dataclass
class CollectionAdmin:
    """Administrative interface for a single MongoDB collection.
    
    This class provides the operations and metadata for managing a specific
    collection, including its configuration, relationships, and access to
    the underlying MongoDB collection.
    
    Attributes:
        name: Collection name
        database: Motor database instance
        config: Collection configuration
        relationships: Detected/configured relationships
    
    Example:
        >>> admin = CollectionAdmin(
        ...     name="users",
        ...     database=db,
        ...     config=CollectionConfig(),
        ...     relationships=[]
        ... )
        >>> collection = admin.collection  # Access MongoDB collection
    """
    
    name: str
    database: AsyncIOMotorDatabase
    config: CollectionConfig
    relationships: list[Relationship] = field(default_factory=list)
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection instance.
        
        Returns:
            Motor collection object for direct database access
            
        Example:
            >>> count = await admin.collection.count_documents({})
        """
        return self.database[self.name]
    
    @property
    def display_name(self) -> str:
        """Get human-readable collection name.
        
        Returns:
            Configured display name or titlecased collection name
            
        Example:
            >>> admin.display_name
            'Users'
        """
        return self.config.display_name or self.name.replace("_", " ").title()
    
    def get_relationship(self, field: str) -> Relationship | None:
        """Get relationship for a specific field.
        
        Args:
            field: Source field name
            
        Returns:
            Relationship object if found, None otherwise
            
        Example:
            >>> rel = admin.get_relationship("user_id")
            >>> if rel:
            ...     print(f"Points to {rel.target_collection}")
        """
        for rel in self.relationships:
            if rel.source_field == field:
                return rel
        return None


class CollectionRegistry:
    """Central registry for all managed MongoDB collections.
    
    The registry maintains a mapping of collection names to their
    administrative interfaces, enabling easy lookup and iteration.
    
    Attributes:
        _collections: Internal mapping of collection name to CollectionAdmin
    
    Example:
        >>> registry = CollectionRegistry()
        >>> registry.register(admin)
        >>> admin = registry.get("users")
        >>> assert "users" in registry
    """
    
    def __init__(self) -> None:
        """Initialize an empty collection registry."""
        self._collections: dict[str, CollectionAdmin] = {}
    
    def register(self, admin: CollectionAdmin) -> None:
        """Register a collection admin instance.
        
        Args:
            admin: CollectionAdmin to register
            
        Raises:
            ValueError: If collection is already registered
            
        Example:
            >>> registry.register(CollectionAdmin(...))
        """
        if admin.name in self._collections:
            raise ValueError(f"Collection '{admin.name}' is already registered")
        self._collections[admin.name] = admin
    
    def unregister(self, name: str) -> None:
        """Remove a collection from the registry.
        
        Args:
            name: Collection name to unregister
            
        Example:
            >>> registry.unregister("temp_collection")
        """
        self._collections.pop(name, None)
    
    def get(self, name: str) -> CollectionAdmin:
        """Get collection admin by name.
        
        Args:
            name: Collection name
            
        Returns:
            CollectionAdmin instance
            
        Raises:
            KeyError: If collection not found
            
        Example:
            >>> admin = registry.get("users")
        """
        if name not in self._collections:
            raise KeyError(f"Collection '{name}' is not registered")
        return self._collections[name]
    
    def get_all(self) -> list[CollectionAdmin]:
        """Get all registered collection admins.
        
        Returns:
            List of all CollectionAdmin instances
            
        Example:
            >>> for admin in registry.get_all():
            ...     print(admin.name)
        """
        return list(self._collections.values())
    
    def __contains__(self, name: str) -> bool:
        """Check if a collection is registered.
        
        Args:
            name: Collection name
            
        Returns:
            True if registered, False otherwise
            
        Example:
            >>> if "users" in registry:
            ...     print("Users collection is registered")
        """
        return name in self._collections
    
    def __iter__(self):
        """Iterate over collection names.
        
        Returns:
            Iterator over collection names
            
        Example:
            >>> for name in registry:
            ...     print(name)
        """
        return iter(self._collections)
    
    def __len__(self) -> int:
        """Get number of registered collections.
        
        Returns:
            Count of registered collections
            
        Example:
            >>> total = len(registry)
        """
        return len(self._collections)
    
    def items(self):
        """Iterate over (name, admin) pairs.
        
        Returns:
            Iterator over (collection_name, CollectionAdmin) tuples
            
        Example:
            >>> for name, admin in registry.items():
            ...     print(f"{name}: {admin.display_name}")
        """
        return self._collections.items()
