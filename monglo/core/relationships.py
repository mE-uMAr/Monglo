
from dataclasses import dataclass
from enum import Enum
from typing import Any

from bson import DBRef, ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

class RelationshipType(Enum):

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"
    EMBEDDED = "embedded"

@dataclass
class Relationship:

    source_collection: str
    source_field: str
    target_collection: str
    target_field: str = "_id"
    type: RelationshipType = RelationshipType.ONE_TO_ONE
    reverse_name: str | None = None

    def __hash__(self) -> int:
        return hash(
            (self.source_collection, self.source_field, self.target_collection, self.target_field)
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Relationship):
            return NotImplemented
        return (
            self.source_collection == other.source_collection
            and self.source_field == other.source_field
            and self.target_collection == other.target_collection
            and self.target_field == other.target_field
        )

class RelationshipDetector:

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.db = database
        self._collection_cache: set[str] = set()

    async def detect(
        self,
        collection_name: str,
        config: Any,  # Will be CollectionConfig, avoiding circular import
        sample_size: int = 100,
    ) -> list[Relationship]:
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

        detected_fields: set[str] = set()

        for doc in sample:
            new_rels = self._detect_in_document(collection_name, doc)
            for rel in new_rels:
                if rel.source_field not in detected_fields:
                    relationships.append(rel)
                    detected_fields.add(rel.source_field)

        return relationships

    def _detect_in_document(
        self, collection_name: str, document: dict[str, Any]
    ) -> list[Relationship]:
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
                    relationships.append(
                        Relationship(
                            source_collection=collection_name,
                            source_field=field,
                            target_collection=target,
                            target_field="_id",
                            type=rel_type,
                        )
                    )
                    continue

            # Strategy 2: ObjectId type detection
            if isinstance(value, ObjectId):
                # Try to find which collection this ID might belong to
                # For now, use naming convention as fallback
                if not field.endswith("_id"):
                    # Could be author, creator, etc.
                    target = self._pluralize(field)
                    if target in self._collection_cache:
                        relationships.append(
                            Relationship(
                                source_collection=collection_name,
                                source_field=field,
                                target_collection=target,
                                target_field="_id",
                                type=RelationshipType.ONE_TO_ONE,
                            )
                        )

            # Strategy 3: Array of ObjectIds
            elif isinstance(value, list) and value and isinstance(value[0], ObjectId):
                target = self._guess_collection_from_field(field)
                if target in self._collection_cache:
                    relationships.append(
                        Relationship(
                            source_collection=collection_name,
                            source_field=field,
                            target_collection=target,
                            target_field="_id",
                            type=RelationshipType.ONE_TO_MANY,
                        )
                    )

            # Strategy 4: DBRef detection
            elif isinstance(value, DBRef):
                relationships.append(
                    Relationship(
                        source_collection=collection_name,
                        source_field=field,
                        target_collection=value.collection,
                        target_field="_id",
                        type=RelationshipType.ONE_TO_ONE,
                    )
                )

        return relationships

    def _guess_collection_from_field(self, field: str) -> str:
        # Handle _ids (plural) - BUT don't use the _ids suffix as already plural
        # Extract the base word and pluralize it properly
        if field.endswith("_ids"):
            base = field[:-4]  # Remove "_ids": category_ids → category
            return self._pluralize(base)  # category → categories
        # Handle _id (singular) - need to pluralize
        elif field.endswith("_id"):
            base = field[:-3]  # Remove "_id": user_id → user
            return self._pluralize(base)  # user → users
        else:
            return self._pluralize(field)

    def _pluralize(self, word: str) -> str:
        if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
            return f"{word[:-1]}ies"  # category → categories
        elif word.endswith(("s", "ss", "x", "z", "ch", "sh")):
            return f"{word}es"  # class → classes, box → boxes
        else:
            return f"{word}s"  # user → users

class RelationshipResolver:

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.db = database

    async def resolve(
        self, document: dict[str, Any], relationships: list[Relationship], depth: int = 1
    ) -> dict[str, Any]:
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
                    related_docs = (
                        await self.db[rel.target_collection]
                        .find({rel.target_field: {"$in": ref_value}})
                        .to_list(100)
                    )  # Limit to 100 related docs
                    resolved["_relationships"][rel.source_field] = related_docs
                else:
                    # One-to-one: fetch single document
                    related_doc = await self.db[rel.target_collection].find_one(
                        {rel.target_field: ref_value}
                    )
                    resolved["_relationships"][rel.source_field] = related_doc

            elif rel.type == RelationshipType.EMBEDDED:
                # Embedded documents are already in the document
                resolved["_relationships"][rel.source_field] = ref_value

        return resolved

    async def resolve_batch(
        self, documents: list[dict[str, Any]], relationships: list[Relationship], depth: int = 1
    ) -> list[dict[str, Any]]:
        if depth <= 0 or not documents:
            return documents

        resolved_docs = [doc.copy() for doc in documents]

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

            related_docs = (
                await self.db[rel.target_collection]
                .find({rel.target_field: {"$in": ref_values}})
                .to_list(1000)
            )  # Limit to prevent memory issues

            related_map = {doc[rel.target_field]: doc for doc in related_docs}

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
                        resolved_docs[idx]["_relationships"][rel.source_field] = related_map[
                            ref_val
                        ]

        return resolved_docs
