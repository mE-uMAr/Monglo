
__version__ = "0.1.0"
__author__ = "Mehar Umar"
__email__ = "contact@meharumar.codes"
__license__ = "MIT"

# Core exports
from .core.config import (
    CollectionConfig,
    DocumentViewConfig,
    FilterConfig,
    TableViewConfig,
)
from .core.engine import MongloEngine
from .core.introspection import SchemaIntrospector
from .core.query_builder import QueryBuilder
from .core.registry import CollectionAdmin, CollectionRegistry
from .core.relationships import (
    Relationship,
    RelationshipDetector,
    RelationshipResolver,
    RelationshipType,
)

# Fields exports
from .fields import (
    BaseField,
    BooleanField,
    DateField,
    DateTimeField,
    DBRefField,
    NumberField,
    ObjectIdField,
    StringField,
)
from .operations.aggregations import AggregationOperations

# Operations exports
from .operations.crud import CRUDOperations
from .operations.export import ExportFormat, ExportOperations, export_collection
from .operations.pagination import PaginationHandler, PaginationStrategy

# Serializers exports
from .serializers import DocumentSerializer, JSONSerializer, TableSerializer

# Views exports
from .views import BaseView, DocumentView, TableView, ViewType

# Adapters (optional - require framework dependencies)
# from .adapters.fastapi import FastAPIAdapter, create_fastapi_router
# from .adapters.flask import FlaskAdapter, create_flask_blueprint
# from .adapters.django import CollectionView, create_django_urls

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Main engine
    "MongloEngine",
    # Configuration
    "CollectionConfig",
    "TableViewConfig",
    "DocumentViewConfig",
    "FilterConfig",
    # Relationships
    "Relationship",
    "RelationshipType",
    "RelationshipDetector",
    "RelationshipResolver",
    # Registry
    "CollectionAdmin",
    "CollectionRegistry",
    # Utilities
    "SchemaIntrospector",
    "QueryBuilder",
    # Operations
    "CRUDOperations",
    "PaginationHandler",
    "PaginationStrategy",
    "ExportOperations",
    "ExportFormat",
    "export_collection",
    "AggregationOperations",
    # Views
    "BaseView",
    "ViewType",
    "TableView",
    "DocumentView",
    # Serializers
    "JSONSerializer",
    "TableSerializer",
    "DocumentSerializer",
    # Fields
    "BaseField",
    "StringField",
    "NumberField",
    "BooleanField",
    "DateField",
    "DateTimeField",
    "ObjectIdField",
    "DBRefField",
]
