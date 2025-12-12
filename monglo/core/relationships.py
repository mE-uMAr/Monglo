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


class RelationshipDetector:
    """Intelligently detect relationships between MongoDB collections.
    
    This class uses multiple detection strategies to automatically discover
    relationships without requiring manual configuration:
    
    1. **Naming Convention**: Fields ending in `_id` or `_ids` are checked
       against existing collections (e.g., `user_id` → `users` collection)
    
    2. **ObjectId Detection**: Fields containing ObjectId values are matched
       against collections where those IDs exist
    
    3. **DBRef Detection**: Standard MongoDB references are automatically recognized
    
    Attributes:
        db: MongoDB database instance
        _collection_cache: Set of collection names for quick lookup
    
    Example:
        >>> detector = RelationshipDetector(db)
       >>> relationships = await detector.detect("orders", config)
        >>> # Returns detected relationships for the orders collection
    """
    
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        """Initialize the relationship detector.
        
        Args:
            database: Motor database instance
        """
        self.db = database
        self._collection_cache: set[str] = set()
    
    async def detect(
        self,
        collection_name: str,
        config: Any,  # Will be CollectionConfig, avoiding circular import
        sample_size: int = 100
    ) -> list[Relationship]:
        """Detect all relationships for a collection.
        
        Args:
            collection_name: Name of the collection to analyze
            config: Collection configuration (may include manual relationships)
            sample_size: Number of documents to sample for detection
            
        Returns:
            List of detected Relationship objects
            
        Example:
            >>> relationships = await detector.detect("orders", config)
            >>> user_rel = next(r for r in relationships if r.source_field == "user_id")
            >>> assert user_rel.target_collection == "users"
        """
        # Populate collection cache
        if not self._collection_cache:
            self._collection_cache = set(await self.db.list_collection_names())
        
        relationships: list[Relationship] = []
        
        # Start with manual relationships from config
        if config.relationships:
           relationships.extend(config.relationships)
        
        # Sample documents for automatic detection
        sample = await self.db[collection_name].find().limit(sample_size).to_list(sample_size)
        
        if not sample:
            return relationships
        
        # Track detected relationships to avoid duplicates
        detected_fields: set[str] = set()
        
        for doc in sample:
            new_rels = self._detect_in_document(collection_name, doc)
            for rel in new_rels:
                if rel.source_field not in detected_fields:
                    relationships.append(rel)
                    detected_fields.add(rel.source_field)
        
        return relationships
    
    def _detect_in_document(
        self,
        collection_name: str,
        document: dict[str, Any]
    ) -> list[Relationship]:
        """Detect relationships within a single document.
        
        Args:
            collection_name: Name of the source collection
            document: Document to analyze
            
        Returns:
            List of detected relationships
        """
        relationships: list[Relationship] = []
        
        for field, value in document.items():
            # Skip _id field
            if field == "_id":
                continue
            
            # Strategy 1: Naming convention (user_id → users)
            if field.endswith("_id") or field.endswith("_ids"):
                target = self._guess_collection_from_field(field)
                if target in self._collection_cache:
                    rel_type = (
                        RelationshipType.ONE_TO_MANY
                        if field.endswith("_ids")
                        else RelationshipType.ONE_TO_ONE
                    )
                    relationships.append(Relationship(
                        source_collection=collection_name,
                        source_field=field,
                        target_collection=target,
                        target_field="_id",
                        type=rel_type
                    ))
                    continue
            
            # Strategy 2: ObjectId type detection
            if isinstance(value, ObjectId):
                # Try to find which collection this ID might belong to
                # For now, use naming convention as fallback
                if not field.endswith("_id"):
                    # Could be author, creator, etc.
                    target = self._pluralize(field)
                    if target in self._collection_cache:
                        relationships.append(Relationship(
                            source_collection=collection_name,
                            source_field=field,
                            target_collection=target,
                            target_field="_id",
                            type=RelationshipType.ONE_TO_ONE
                        ))
            
            # Strategy 3: Array of ObjectIds
            elif isinstance(value, list) and value and isinstance(value[0], ObjectId):
                target = self._guess_collection_from_field(field)
                if target in self._collection_cache:
                    relationships.append(Relationship(
                        source_collection=collection_name,
                        source_field=field,
                        target_collection=target,
                        target_field="_id",
                        type=RelationshipType.ONE_TO_MANY
                    ))
            
            # Strategy 4: DBRef detection
            elif isinstance(value, DBRef):
                relationships.append(Relationship(
                    source_collection=collection_name,
                    source_field=field,
                    target_collection=value.collection,
                    target_field="_id",
                    type=RelationshipType.ONE_TO_ONE
                ))
        
        return relationships
    
    def _guess_collection_from_field(self, field: str) -> str:
        """Guess collection name from field name.
        
        Converts field names to pluralized collection names:
        - user_id → users
        - author_id → authors
        - category_ids → categories
        
        Args:
            field: Field name to convert
            
        Returns:
            Guessed collection name
            
        Example:
            >>> detector._guess_collection_from_field("user_id")
            'users'
            >>> detector._guess_collection_from_field("category_ids")
            'categories'
        """
        # Remove _id or _ids suffix
        base = field.replace("_id", "").replace("_ids", "")
        return self._pluralize(base)
    
    def _pluralize(self, word: str) -> str:
        """Simple pluralization for collection name guessing.
        
        Args:
            word: Singular word
            
        Returns:
            Pluralized word
            
        Example:
            >>> detector._pluralize("user")
            'users'
            >>> detector._pluralize("category")
            'categories'
        """
        if word.endswith("y"):
            return f"{word[:-1]}ies"  # category → categories
        elif word.endswith("s"):
            return f"{word}es"  # class → classes
        else:
            return f"{word}s"  # user → users


class RelationshipResolver:
    """Resolve and populate relationships in MongoDB documents.
    
    This class enriches documents with related data by following relationship
    definitions. It uses batch queries to efficiently load related documents
    and avoid N+1 query problems.
    
    Attributes:
        db: MongoDB database instance
    
    Example:
        >>> resolver = RelationshipResolver(db)
        >>> order = {"_id": ObjectId(), "user_id": ObjectId(...)}
        >>> enriched = await resolver.resolve(order, relationships, depth=1)
        >>> # enriched["_relationships"]["user"] contains the user document
    """
    
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        """Initialize the relationship resolver.
        
        Args:
            database: Motor database instance
        """
        self.db = database
    
    async def resolve(
        self,
        document: dict[str, Any],
        relationships: list[Relationship],
        depth: int = 1
    ) -> dict[str, Any]:
        """Resolve relationships in a document.
        
        Enriches the document with a `_relationships` field containing
        related documents. Supports configurable depth for nested resolution.
        
        Args:
            document: Document to enrich
            relationships: List of relationships to resolve
            depth: How many levels deep to resolve (1-3)
            
        Returns:
            Document with `_relationships` field added
            
        Example:
            >>> order = {"_id": ObjectId(), "user_id": user_id}
            >>> resolved = await resolver.resolve(order, [user_rel], depth=1)
            >>> assert "_relationships" in resolved
            >>> assert "user_id" in resolved["_relationships"]
        """
        if depth <= 0:
            return document
        
        resolved = document.copy()
        resolved["_relationships"] = {}
        
        for rel in relationships:
            if rel.source_field not in document:
                continue
            
            ref_value = document[rel.source_field]
            
            # Handle one-to-one and one-to-many relationships
            if rel.type in [RelationshipType.ONE_TO_ONE, RelationshipType.ONE_TO_MANY]:
                if isinstance(ref_value, list):
                    # One-to-many: fetch multiple documents
                    related_docs = await self.db[rel.target_collection].find({
                        rel.target_field: {"$in": ref_value}
                    }).to_list(100)  # Limit to 100 related docs
                    resolved["_relationships"][rel.source_field] = related_docs
                else:
                    # One-to-one: fetch single document
                    related_doc = await self.db[rel.target_collection].find_one({
                        rel.target_field: ref_value
                    })
                    resolved["_relationships"][rel.source_field] = related_doc
            
            elif rel.type == RelationshipType.EMBEDDED:
                # Embedded documents are already in the document
                resolved["_relationships"][rel.source_field] = ref_value
        
        return resolved
    
    async def resolve_batch(
        self,
        documents: list[dict[str, Any]],
        relationships: list[Relationship],
        depth: int = 1
    ) -> list[dict[str, Any]]:
        """Resolve relationships for multiple documents efficiently.
        
        Uses batch queries to load all related documents at once,
        avoiding the N+1 query problem.
        
        Args:
            documents: List of documents to enrich
            relationships: List of relationships to resolve
            depth: How many levels deep to resolve
            
        Returns:
            List of enriched documents
            
        Example:
            >>> orders = [{"user_id": id1}, {"user_id": id2}]
            >>> resolved = await resolver.resolve_batch(orders, [user_rel])
            >>> # Only 1 query to fetch all users, not N queries
        """
        if depth <= 0 or not documents:
            return documents
        
        resolved_docs = [doc.copy() for doc in documents]
        
        # Initialize _relationships for all documents
        for doc in resolved_docs:
            doc["_relationships"] = {}
        
        # Group relationships by target collection for batch loading
        for rel in relationships:
            # Collect all reference values from all documents
            ref_values: list[Any] = []
            doc_indices: list[int] = []
            
            for idx, doc in enumerate(documents):
                if rel.source_field in doc:
                    ref_val = doc[rel.source_field]
                    if isinstance(ref_val, list):
                        ref_values.extend(ref_val)
                    else:
                        ref_values.append(ref_val)
                    doc_indices.append(idx)
            
            if not ref_values:
                continue
            
            # Fetch all related documents in one query
            related_docs = await self.db[rel.target_collection].find({
                rel.target_field: {"$in": ref_values}
            }).to_list(1000)  # Limit to prevent memory issues
            
            # Create a lookup map for O(1) access
            related_map = {
                doc[rel.target_field]: doc
                for doc in related_docs
            }
            
            # Assign related documents back to original documents
            for idx in doc_indices:
                source_doc = documents[idx]
                if rel.source_field not in source_doc:
                    continue
                
                ref_val = source_doc[rel.source_field]
                
                if isinstance(ref_val, list):
                    # One-to-many
                    resolved_docs[idx]["_relationships"][rel.source_field] = [
                        related_map[val] for val in ref_val if val in related_map
                    ]
                else:
                    # One-to-one
                    if ref_val in related_map:
                        resolved_docs[idx]["_relationships"][rel.source_field] = related_map[ref_val]
        
        return resolved_docs


