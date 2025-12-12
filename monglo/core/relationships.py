"""
Relationship detection and resolution for MongoDB collections.

This module provides intelligent relationship detection between MongoDB collections
using multiple strategies: naming conventions, ObjectId fields, and DBRef.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any
from bson import ObjectId, DBRef
from motor.motor_asyncio import AsyncIOMotorDatabase


class RelationshipType(Enum):
    """Types of relationships between collections.
    
    Attributes:
        ONE_TO_ONE: Single reference to another document
        ONE_TO_MANY: Array of references to multiple documents
        MANY_TO_MANY: Many-to-many relationship (via junction collection)
        EMBEDDED: Embedded document (not a reference)
    
    Example:
        >>> rel_type = RelationshipType.ONE_TO_ONE
        >>> assert rel_type.value == "one_to_one"
    """
    
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"
    EMBEDDED = "embedded"


@dataclass
class Relationship:
    """Represents a relationship between MongoDB collections.
    
    A relationship connects a field in the source collection to documents
    in the target collection, enabling navigation and data enrichment.
    
    Attributes:
        source_collection: Name of the collection containing the reference
        source_field: Field name in source collection (e.g., "user_id")
        target_collection: Name of the referenced collection (e.g., "users")
        target_field: Field name in target collection (usually "_id")
        type: Type of relationship (ONE_TO_ONE, ONE_TO_MANY, etc.)
        reverse_name: Optional name for reverse navigation (bidirectional)
    
    Example:
        >>> rel = Relationship(
        ...     source_collection="orders",
        ...     source_field="user_id",
        ...     target_collection="users",
        ...     target_field="_id",
        ...     type=RelationshipType.ONE_TO_ONE,
        ...     reverse_name="orders"
        ... )
        >>> # This allows: order.user_id -> User document
        >>> # And reverse: user -> [Order documents]
    """
    
    source_collection: str
    source_field: str
    target_collection: str
    target_field: str = "_id"
    type: RelationshipType = RelationshipType.ONE_TO_ONE
    reverse_name: str | None = None
    
    def __hash__(self) -> int:
        """Make Relationship hashable for use in sets and dicts."""
        return hash((
            self.source_collection,
            self.source_field,
            self.target_collection,
            self.target_field
        ))
    
    def __eq__(self, other: object) -> bool:
        """Compare relationships by their core attributes."""
        if not isinstance(other, Relationship):
            return NotImplemented
        return (
            self.source_collection == other.source_collection
            and self.source_field == other.source_field
            and self.target_collection == other.target_collection
            and self.target_field == other.target_field
        )
