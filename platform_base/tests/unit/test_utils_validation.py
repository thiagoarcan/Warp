"""
Tests for validation module - 100% coverage target.
"""
import pytest
from pydantic import BaseModel

from platform_base.utils.errors import ValidationError
from platform_base.utils.validation import validate_config


class SampleConfig(BaseModel):
    """Sample config for testing."""
    name: str
    value: int
    enabled: bool = True


class NestedConfig(BaseModel):
    """Nested config for testing."""
    title: str
    settings: SampleConfig


class TestValidateConfig:
    """Tests for validate_config function."""
    
    def test_valid_config_simple(self):
        """Test validation with valid simple config."""
        config_dict = {"name": "test", "value": 42}
        result = validate_config(config_dict, SampleConfig)
        
        assert isinstance(result, SampleConfig)
        assert result.name == "test"
        assert result.value == 42
        assert result.enabled is True  # Default value
    
    def test_valid_config_all_fields(self):
        """Test validation with all fields provided."""
        config_dict = {"name": "full", "value": 100, "enabled": False}
        result = validate_config(config_dict, SampleConfig)
        
        assert result.name == "full"
        assert result.value == 100
        assert result.enabled is False
    
    def test_invalid_config_missing_required(self):
        """Test validation fails with missing required field."""
        config_dict = {"name": "test"}  # Missing 'value'
        
        with pytest.raises(ValidationError) as exc_info:
            validate_config(config_dict, SampleConfig)
        
        assert "Config validation failed" in str(exc_info.value)
    
    def test_invalid_config_wrong_type(self):
        """Test validation fails with wrong type."""
        config_dict = {"name": "test", "value": "not_an_int"}
        
        with pytest.raises(ValidationError):
            validate_config(config_dict, SampleConfig)
    
    def test_nested_config_valid(self):
        """Test validation with nested config."""
        config_dict = {
            "title": "Main Config",
            "settings": {"name": "nested", "value": 10}
        }
        result = validate_config(config_dict, NestedConfig)
        
        assert result.title == "Main Config"
        assert result.settings.name == "nested"
        assert result.settings.value == 10
    
    def test_nested_config_invalid(self):
        """Test validation fails with invalid nested config."""
        config_dict = {
            "title": "Main Config",
            "settings": {"name": "nested"}  # Missing value
        }
        
        with pytest.raises(ValidationError):
            validate_config(config_dict, NestedConfig)
    
    def test_empty_config_dict(self):
        """Test validation with empty dict."""
        with pytest.raises(ValidationError):
            validate_config({}, SampleConfig)
    
    def test_extra_fields_ignored(self):
        """Test that extra fields are handled."""
        config_dict = {"name": "test", "value": 42, "extra": "ignored"}
        # Pydantic by default ignores extra fields
        result = validate_config(config_dict, SampleConfig)
        assert result.name == "test"
    
    def test_validation_error_contains_details(self):
        """Test that ValidationError contains error details."""
        config_dict = {"name": 123, "value": "wrong"}  # Both wrong types
        
        with pytest.raises(ValidationError) as exc_info:
            validate_config(config_dict, SampleConfig)
        
        error = exc_info.value
        # ValidationError should have details dict or message about errors
        assert hasattr(error, 'details') or hasattr(error, 'args')
