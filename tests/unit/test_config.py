"""
Unit tests for the configuration system.

Tests all configuration models including validation, defaults, and serialization.
"""

import pytest
from pydantic import ValidationError

from monglo.core.config import (
    CollectionConfig,
    TableViewConfig,
    DocumentViewConfig,
    FilterConfig,
)


class TestTableViewConfig:
    """Test TableViewConfig model."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = TableViewConfig()
        
        assert config.columns == []
        assert config.default_sort == []
        assert config.per_page == 20
        assert config.enable_bulk_actions is True
        assert config.enable_export is True
        assert config.row_actions == ["view", "edit", "delete"]
    
    def test_custom_values(self):
        """Test setting custom values."""
        config = TableViewConfig(
            columns=[{"field": "name", "width": 200}],
            default_sort=[("created_at", -1)],
            per_page=50,
            enable_bulk_actions=False
        )
        
        assert len(config.columns) == 1
        assert config.columns[0]["field"] == "name"
        assert config.default_sort == [("created_at", -1)]
        assert config.per_page == 50
        assert config.enable_bulk_actions is False
    
    def test_per_page_validation(self):
        """Test per_page validation constraints."""
        # Valid range
        config = TableViewConfig(per_page=50)
        assert config.per_page == 50
        
        # Below minimum
        with pytest.raises(ValidationError) as exc_info:
            TableViewConfig(per_page=0)
        assert "greater than or equal to 1" in str(exc_info.value)
        
        # Above maximum
        with pytest.raises(ValidationError) as exc_info:
            TableViewConfig(per_page=101)
        assert "less than or equal to 100" in str(exc_info.value)


class TestDocumentViewConfig:
    """Test DocumentViewConfig model."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = DocumentViewConfig()
        
        assert config.layout == "tree"
        assert config.fields == []
        assert config.readonly_fields == []
        assert config.enable_relationships is True
        assert config.relationship_depth == 1
    
    def test_layout_values(self):
        """Test layout literal type validation."""
        # Valid values
        config1 = DocumentViewConfig(layout="tree")
        assert config1.layout == "tree"
        
        config2 = DocumentViewConfig(layout="form")
        assert config2.layout == "form"
        
        # Invalid value
        with pytest.raises(ValidationError):
            DocumentViewConfig(layout="invalid")
    
    def test_relationship_depth_validation(self):
        """Test relationship_depth constraints."""
        # Valid range
        config = DocumentViewConfig(relationship_depth=2)
        assert config.relationship_depth == 2
        
        # Below minimum
        with pytest.raises(ValidationError):
            DocumentViewConfig(relationship_depth=0)
        
        # Above maximum
        with pytest.raises(ValidationError):
            DocumentViewConfig(relationship_depth=4)


class TestFilterConfig:
    """Test FilterConfig model."""
    
    def test_required_fields(self):
        """Test that required fields are enforced."""
        # Missing required fields
        with pytest.raises(ValidationError):
            FilterConfig()
        
        # Valid config with required fields
        config = FilterConfig(field="status", type="eq")
        assert config.field == "status"
        assert config.type == "eq"
        assert config.label is None
        assert config.options is None
    
    def test_filter_types(self):
        """Test all filter type literals."""
        valid_types = [
            "eq", "ne", "gt", "lt", "gte", "lte",
            "in", "regex", "range", "date_range"
        ]
        
        for filter_type in valid_types:
            config = FilterConfig(field="test", type=filter_type)
            assert config.type == filter_type
    
    def test_invalid_filter_type(self):
        """Test that invalid filter types are rejected."""
        with pytest.raises(ValidationError):
            FilterConfig(field="test", type="invalid")
    
    def test_optional_fields(self):
        """Test optional label and options fields."""
        config = FilterConfig(
            field="category",
            type="in",
            label="Product Category",
            options=["Electronics", "Books", "Clothing"]
        )
        
        assert config.label == "Product Category"
        assert len(config.options) == 3


class TestCollectionConfig:
    """Test CollectionConfig model."""
    
    def test_default_values(self):
        """Test default values initialization."""
        config = CollectionConfig()
        
        assert config.name is None
        assert config.display_name is None
        assert config.icon is None
        assert config.list_fields is None
        assert config.search_fields is None
        assert isinstance(config.table_view, TableViewConfig)
        assert isinstance(config.document_view, DocumentViewConfig)
        assert config.filters == []
        assert config.relationships == []
        assert config.actions == ["create", "edit", "delete"]
        assert config.bulk_actions == ["delete", "export"]
        assert config.pagination_config["style"] == "offset"
        assert config.pagination_config["per_page"] == 20
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = CollectionConfig(
            name="users",
            display_name="User Accounts",
            icon="user",
            list_fields=["name", "email", "created_at"],
            search_fields=["name", "email"],
            table_view=TableViewConfig(per_page=50),
            filters=[
                FilterConfig(field="status", type="eq", label="Status")
            ]
        )
        
        assert config.name == "users"
        assert config.display_name == "User Accounts"
        assert config.icon == "user"
        assert len(config.list_fields) == 3
        assert len(config.search_fields) == 2
        assert config.table_view.per_page == 50
        assert len(config.filters) == 1
    
    def test_nested_config_validation(self):
        """Test that nested configs are validated."""
        # Invalid table_view
        with pytest.raises(ValidationError):
            CollectionConfig(
                table_view=TableViewConfig(per_page=1000)  # Exceeds max
            )
        
        # Invalid document_view
        with pytest.raises(ValidationError):
            CollectionConfig(
                document_view=DocumentViewConfig(relationship_depth=10)  # Exceeds max
            )
    
    def test_from_schema_factory(self):
        """Test creating config from introspected schema."""
        schema = {
            "name": {"type": "string", "frequency": 1.0},
            "email": {"type": "string", "frequency": 1.0},
            "age": {"type": "number", "frequency": 0.95},
            "bio": {"type": "string", "frequency": 0.5},
            "created_at": {"type": "datetime", "frequency": 1.0},
            "updated_at": {"type": "datetime", "frequency": 1.0},
            "is_active": {"type": "boolean", "frequency": 1.0},
            "metadata": {"type": "embedded", "frequency": 0.8},
            "tags": {"type": "array", "frequency": 0.7},
            "user_id": {"type": "objectid", "frequency": 1.0},
            "extra1": {"type": "string", "frequency": 0.1},
            "extra2": {"type": "string", "frequency": 0.1},
        }
        
        config = CollectionConfig.from_schema(schema)
        
        # Should have first 10 fields for list
        assert config.list_fields is not None
        assert len(config.list_fields) == 10
        
        # Should have up to 5 string fields for search
        assert config.search_fields is not None
        assert len(config.search_fields) <= 5
        assert all(
            schema[field]["type"] == "string" 
            for field in config.search_fields
        )
        
        # Should have sortable fields
        assert config.sortable_fields is not None
        sortable_types = {"string", "number", "datetime", "date"}
        assert all(
            schema[field]["type"] in sortable_types
            for field in config.sortable_fields
        )
    
    def test_from_schema_empty(self):
        """Test from_schema with empty schema."""
        config = CollectionConfig.from_schema({})
        
        assert config.list_fields == []
        assert config.search_fields == []
        assert config.sortable_fields == []
    
    def test_from_schema_no_strings(self):
        """Test from_schema with no string fields."""
        schema = {
            "count": {"type": "number"},
            "is_active": {"type": "boolean"},
            "created_at": {"type": "datetime"}
        }
        
        config = CollectionConfig.from_schema(schema)
        
        # Should have empty search_fields
        assert config.search_fields == []
        # But should have sortable fields
        assert len(config.sortable_fields) > 0
    
    def test_permissions_config(self):
        """Test permissions configuration."""
        config = CollectionConfig(
            permissions={
                "admin": ["create", "read", "update", "delete"],
                "user": ["read"],
                "editor": ["read", "update"]
            }
        )
        
        assert "admin" in config.permissions
        assert len(config.permissions["admin"]) == 4
        assert config.permissions["user"] == ["read"]
    
    def test_pagination_config(self):
        """Test pagination configuration."""
        config = CollectionConfig(
            pagination_config={
                "style": "cursor",
                "per_page": 30,
                "max_per_page": 200
            }
        )
        
        assert config.pagination_config["style"] == "cursor"
        assert config.pagination_config["per_page"] == 30
        assert config.pagination_config["max_per_page"] == 200
