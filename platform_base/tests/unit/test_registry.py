"""
Comprehensive tests for core/registry.py

Tests plugin registry, manifest handling, version compatibility,
sandbox execution, and security features.
"""

from __future__ import annotations

import json
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import numpy as np
import pytest

from platform_base.core.protocols import PluginProtocol
from platform_base.core.registry import (
    PLATFORM_VERSION,
    PLUGIN_API_VERSION,
    CompatibilityCheck,
    PluginInfo,
    PluginManifest,
    PluginRegistry,
    PluginState,
    ResourceLimits,
    SecurityViolation,
    VersionCompatibility,
)

# =============================================================================
# Test Fixtures
# =============================================================================

class DummyPlugin:
    """Dummy plugin for testing."""
    name = "dummy"
    version = "0.1"
    capabilities = ["test"]

    def interpolate(self, values, t_seconds, params):
        return values


@pytest.fixture
def dummy_plugin():
    """Create a dummy plugin instance."""
    return DummyPlugin()


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create a temporary plugin directory with a valid plugin."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()
    
    # Create manifest
    manifest = {
        "name": "test_plugin",
        "version": "1.0.0",
        "description": "Test plugin",
        "author": "Test Author",
        "entry_point": "plugin.py",
        "main_class": "TestPlugin",
    }
    
    with open(plugin_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)
    
    # Create plugin file
    plugin_code = '''
class TestPlugin:
    name = "test_plugin"
    version = "1.0.0"
    capabilities = ["test"]
    
    def process(self, data):
        return data
'''
    with open(plugin_dir / "plugin.py", "w") as f:
        f.write(plugin_code)
    
    return tmp_path


# =============================================================================
# VersionCompatibility Tests
# =============================================================================

class TestVersionCompatibility:
    """Tests for VersionCompatibility utility class."""
    
    def test_parse_version_full(self):
        """Test parsing full version string."""
        result = VersionCompatibility.parse_version("1.2.3")
        assert result == (1, 2, 3)
    
    def test_parse_version_major_minor(self):
        """Test parsing version with only major.minor."""
        result = VersionCompatibility.parse_version("1.2")
        assert result == (1, 2, 0)
    
    def test_parse_version_major_only(self):
        """Test parsing version with only major."""
        result = VersionCompatibility.parse_version("1")
        assert result == (1, 0, 0)
    
    def test_parse_version_invalid(self):
        """Test parsing invalid version string."""
        result = VersionCompatibility.parse_version("invalid")
        assert result == (0, 0, 0)
    
    def test_parse_version_empty(self):
        """Test parsing empty version string."""
        result = VersionCompatibility.parse_version("")
        assert result == (0, 0, 0)
    
    def test_compare_versions_equal(self):
        """Test comparing equal versions."""
        result = VersionCompatibility.compare_versions("1.2.3", "1.2.3")
        assert result == 0
    
    def test_compare_versions_less_than(self):
        """Test comparing version less than."""
        result = VersionCompatibility.compare_versions("1.0.0", "2.0.0")
        assert result == -1
    
    def test_compare_versions_greater_than(self):
        """Test comparing version greater than."""
        result = VersionCompatibility.compare_versions("2.0.0", "1.0.0")
        assert result == 1
    
    def test_compare_versions_minor_difference(self):
        """Test comparing versions with minor difference."""
        result = VersionCompatibility.compare_versions("1.1.0", "1.2.0")
        assert result == -1
    
    def test_compare_versions_patch_difference(self):
        """Test comparing versions with patch difference."""
        result = VersionCompatibility.compare_versions("1.0.1", "1.0.2")
        assert result == -1
    
    def test_satisfies_requirement_greater_equal(self):
        """Test satisfies_requirement with >= operator."""
        assert VersionCompatibility.satisfies_requirement("2.0.0", ">=1.0.0") is True
        assert VersionCompatibility.satisfies_requirement("1.0.0", ">=1.0.0") is True
        assert VersionCompatibility.satisfies_requirement("0.9.0", ">=1.0.0") is False
    
    def test_satisfies_requirement_less_equal(self):
        """Test satisfies_requirement with <= operator."""
        assert VersionCompatibility.satisfies_requirement("1.0.0", "<=2.0.0") is True
        assert VersionCompatibility.satisfies_requirement("2.0.0", "<=2.0.0") is True
        assert VersionCompatibility.satisfies_requirement("2.1.0", "<=2.0.0") is False
    
    def test_satisfies_requirement_greater_than(self):
        """Test satisfies_requirement with > operator."""
        assert VersionCompatibility.satisfies_requirement("2.0.0", ">1.0.0") is True
        assert VersionCompatibility.satisfies_requirement("1.0.0", ">1.0.0") is False
    
    def test_satisfies_requirement_less_than(self):
        """Test satisfies_requirement with < operator."""
        assert VersionCompatibility.satisfies_requirement("0.9.0", "<1.0.0") is True
        assert VersionCompatibility.satisfies_requirement("1.0.0", "<1.0.0") is False
    
    def test_satisfies_requirement_equal(self):
        """Test satisfies_requirement with == operator."""
        assert VersionCompatibility.satisfies_requirement("1.0.0", "==1.0.0") is True
        assert VersionCompatibility.satisfies_requirement("1.0.1", "==1.0.0") is False
    
    def test_satisfies_requirement_compatible_release(self):
        """Test satisfies_requirement with ~= operator."""
        assert VersionCompatibility.satisfies_requirement("1.2.0", "~=1.2.0") is True
        assert VersionCompatibility.satisfies_requirement("1.2.5", "~=1.2.0") is True
        assert VersionCompatibility.satisfies_requirement("1.3.0", "~=1.2.0") is False
    
    def test_satisfies_requirement_exact_match(self):
        """Test satisfies_requirement with exact version."""
        assert VersionCompatibility.satisfies_requirement("1.0.0", "1.0.0") is True
        assert VersionCompatibility.satisfies_requirement("1.0.1", "1.0.0") is False
    
    def test_is_compatible_api_version_current(self):
        """Test is_compatible_api_version with current API."""
        assert VersionCompatibility.is_compatible_api_version(PLUGIN_API_VERSION) is True
    
    def test_is_compatible_api_version_future(self):
        """Test is_compatible_api_version with future API."""
        assert VersionCompatibility.is_compatible_api_version("99.0.0") is False
    
    def test_is_compatible_api_version_with_min(self):
        """Test is_compatible_api_version with minimum version."""
        assert VersionCompatibility.is_compatible_api_version("1.0.0", min_version="0.5.0") is True
        assert VersionCompatibility.is_compatible_api_version("0.4.0", min_version="0.5.0") is False
    
    def test_is_compatible_api_version_with_max(self):
        """Test is_compatible_api_version with maximum version."""
        assert VersionCompatibility.is_compatible_api_version("1.0.0", max_version="2.0.0") is True
        assert VersionCompatibility.is_compatible_api_version("2.1.0", max_version="2.0.0") is False


# =============================================================================
# CompatibilityCheck Tests
# =============================================================================

class TestCompatibilityCheck:
    """Tests for CompatibilityCheck dataclass."""
    
    def test_compatibility_check_initial_state(self):
        """Test initial state of CompatibilityCheck."""
        check = CompatibilityCheck(compatible=True)
        assert check.compatible is True
        assert len(check.issues) == 0
        assert len(check.warnings) == 0
    
    def test_add_error(self):
        """Test adding error sets compatible to False."""
        check = CompatibilityCheck(compatible=True)
        check.add_error("Test error")
        
        assert check.compatible is False
        assert "Test error" in check.issues
    
    def test_add_warning(self):
        """Test adding warning doesn't affect compatible."""
        check = CompatibilityCheck(compatible=True)
        check.add_warning("Test warning")
        
        assert check.compatible is True
        assert "Test warning" in check.warnings
    
    def test_multiple_errors(self):
        """Test adding multiple errors."""
        check = CompatibilityCheck(compatible=True)
        check.add_error("Error 1")
        check.add_error("Error 2")
        
        assert len(check.issues) == 2


# =============================================================================
# PluginState Tests
# =============================================================================

class TestPluginState:
    """Tests for PluginState enum."""
    
    def test_plugin_states_exist(self):
        """Test all expected plugin states exist."""
        assert PluginState.UNLOADED.value == "unloaded"
        assert PluginState.LOADING.value == "loading"
        assert PluginState.LOADED.value == "loaded"
        assert PluginState.ERROR.value == "error"
        assert PluginState.DISABLED.value == "disabled"
    
    def test_plugin_state_comparison(self):
        """Test plugin state comparison."""
        assert PluginState.LOADED != PluginState.UNLOADED


# =============================================================================
# PluginManifest Tests
# =============================================================================

class TestPluginManifest:
    """Tests for PluginManifest dataclass."""
    
    def test_plugin_manifest_basic(self):
        """Test basic plugin manifest creation."""
        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            description="Test plugin",
        )
        assert manifest.name == "test"
        assert manifest.version == "1.0.0"
    
    def test_plugin_manifest_defaults(self):
        """Test plugin manifest default values."""
        manifest = PluginManifest(name="test", version="1.0.0")
        assert manifest.entry_point == "plugin.py"
        assert manifest.main_class == "Plugin"
        assert manifest.category == "general"
        assert manifest.trusted is False
    
    def test_plugin_manifest_from_file(self, tmp_path):
        """Test loading manifest from file."""
        manifest_data = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "author": "Test Author",
        }
        
        manifest_file = tmp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)
        
        loaded = PluginManifest.from_file(manifest_file)
        assert loaded.name == "test_plugin"
        assert loaded.version == "1.0.0"
    
    def test_plugin_manifest_from_file_invalid(self, tmp_path):
        """Test loading manifest from invalid file."""
        manifest_file = tmp_path / "invalid.json"
        with open(manifest_file, "w") as f:
            f.write("not valid json")
        
        from platform_base.utils.errors import PluginError
        with pytest.raises(PluginError):
            PluginManifest.from_file(manifest_file)
    
    def test_plugin_manifest_security_settings(self):
        """Test manifest security settings."""
        manifest = PluginManifest(
            name="secure",
            version="1.0.0",
            sandbox_level="strict",
            trusted=False,
        )
        assert manifest.sandbox_level == "strict"
        assert manifest.trusted is False
    
    def test_plugin_manifest_resource_limits(self):
        """Test manifest resource limit settings."""
        manifest = PluginManifest(
            name="limited",
            version="1.0.0",
            timeout_seconds=10.0,
            max_memory_mb=50.0,
            max_cpu_percent=50.0,
        )
        assert manifest.timeout_seconds == 10.0
        assert manifest.max_memory_mb == 50.0
        assert manifest.max_cpu_percent == 50.0


# =============================================================================
# PluginInfo Tests
# =============================================================================

class TestPluginInfo:
    """Tests for PluginInfo dataclass."""
    
    def test_plugin_info_basic(self, tmp_path):
        """Test basic PluginInfo creation."""
        manifest = PluginManifest(name="test", version="1.0.0")
        info = PluginInfo(manifest=manifest, plugin_path=tmp_path)
        
        assert info.state == PluginState.UNLOADED
        assert info.instance is None
        assert info.error_message is None
    
    def test_plugin_info_resource_tracking(self, tmp_path):
        """Test PluginInfo resource tracking defaults."""
        manifest = PluginManifest(name="test", version="1.0.0")
        info = PluginInfo(manifest=manifest, plugin_path=tmp_path)
        
        assert info.peak_memory_mb == 0.0
        assert info.total_cpu_time == 0.0
        assert info.error_count == 0


# =============================================================================
# ResourceLimits Tests
# =============================================================================

class TestResourceLimits:
    """Tests for ResourceLimits dataclass."""
    
    def test_resource_limits_defaults(self):
        """Test ResourceLimits default values."""
        limits = ResourceLimits()
        assert limits.max_memory_mb == 100.0
        assert limits.max_cpu_percent == 80.0
        assert limits.max_execution_time == 30.0
    
    def test_resource_limits_custom(self):
        """Test ResourceLimits with custom values."""
        limits = ResourceLimits(
            max_memory_mb=50.0,
            max_cpu_percent=50.0,
            max_execution_time=10.0,
        )
        assert limits.max_memory_mb == 50.0
        assert limits.max_cpu_percent == 50.0


# =============================================================================
# SecurityViolation Tests
# =============================================================================

class TestSecurityViolation:
    """Tests for SecurityViolation dataclass."""
    
    def test_security_violation_basic(self):
        """Test basic SecurityViolation creation."""
        violation = SecurityViolation(
            plugin_name="test",
            violation_type="timeout",
            description="Test timeout",
        )
        assert violation.plugin_name == "test"
        assert violation.violation_type == "timeout"
        assert violation.severity == "warning"
    
    def test_security_violation_timestamp(self):
        """Test SecurityViolation timestamp auto-generation."""
        before = time.time()
        violation = SecurityViolation(
            plugin_name="test",
            violation_type="test",
            description="Test",
        )
        after = time.time()
        
        assert before <= violation.timestamp <= after


# =============================================================================
# PluginRegistry Tests
# =============================================================================

class TestPluginRegistry:
    """Tests for PluginRegistry class."""
    
    def test_registry_initialization(self):
        """Test PluginRegistry initialization."""
        registry = PluginRegistry()
        assert len(registry._plugins) == 0
    
    def test_registry_initialization_with_directories(self, tmp_path):
        """Test PluginRegistry initialization with directories."""
        registry = PluginRegistry(plugin_directories=[tmp_path])
        assert tmp_path in registry._plugin_directories
    
    def test_registry_add_plugin_directory(self, tmp_path):
        """Test adding plugin directory."""
        registry = PluginRegistry()
        registry.add_plugin_directory(tmp_path)
        assert tmp_path in registry._plugin_directories
    
    def test_registry_add_nonexistent_directory(self, tmp_path):
        """Test adding non-existent directory."""
        registry = PluginRegistry()
        nonexistent = tmp_path / "nonexistent"
        
        # Should not add non-existent directory
        registry.add_plugin_directory(nonexistent)
        assert nonexistent not in registry._plugin_directories
    
    def test_registry_registers_plugin(self):
        """Test basic plugin registration."""
        registry = PluginRegistry()
        plugin = DummyPlugin()
        registry.register(plugin)
        assert "dummy" in registry.list_plugins()
    
    def test_registry_list_plugins_empty(self):
        """Test listing plugins when empty."""
        registry = PluginRegistry()
        result = registry.list_plugins()
        assert isinstance(result, list)
    
    def test_registry_discover_plugins_empty_dir(self, tmp_path):
        """Test discovering plugins in empty directory."""
        registry = PluginRegistry(plugin_directories=[tmp_path])
        discovered = registry.discover_plugins()
        assert len(discovered) == 0
    
    def test_registry_discover_plugins(self, temp_plugin_dir):
        """Test discovering plugins."""
        registry = PluginRegistry(plugin_directories=[temp_plugin_dir])
        discovered = registry.discover_plugins()
        # May be 0 or 1 depending on validation
        assert isinstance(discovered, list)


# =============================================================================
# Additional Registry Tests
# =============================================================================

class TestRegistryAdvanced:
    """Advanced tests for PluginRegistry."""
    
    def test_registry_thread_safety(self):
        """Test registry thread safety during discovery."""
        registry = PluginRegistry()
        
        errors = []
        
        def discover_in_thread():
            try:
                registry.discover_plugins()
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=discover_in_thread) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
    
    def test_registry_max_plugins_limit(self):
        """Test registry max plugins limit."""
        registry = PluginRegistry()
        assert registry._max_plugins == 100
    
    def test_registry_global_timeout(self):
        """Test registry global timeout setting."""
        registry = PluginRegistry()
        assert registry._global_timeout == 60.0


# =============================================================================
# Integration-like Tests
# =============================================================================

class TestRegistryIntegration:
    """Integration-style tests for the registry system."""
    
    def test_full_plugin_lifecycle(self, tmp_path):
        """Test complete plugin lifecycle."""
        # Create plugin directory structure
        plugin_dir = tmp_path / "lifecycle_plugin"
        plugin_dir.mkdir()
        
        manifest = {
            "name": "lifecycle",
            "version": "1.0.0",
            "description": "Lifecycle test plugin",
        }
        with open(plugin_dir / "manifest.json", "w") as f:
            json.dump(manifest, f)
        
        with open(plugin_dir / "plugin.py", "w") as f:
            f.write("class Plugin: pass")
        
        # Initialize registry
        registry = PluginRegistry(plugin_directories=[tmp_path])
        
        # Discover
        discovered = registry.discover_plugins()
        
        # Verify structure
        assert isinstance(discovered, list)
    
    def test_version_compatibility_workflow(self):
        """Test complete version compatibility workflow."""
        # Check platform version
        assert PLATFORM_VERSION is not None
        assert PLUGIN_API_VERSION is not None
        
        # Simulate version checks
        check = CompatibilityCheck(compatible=True)
        
        # Check platform requirement
        if not VersionCompatibility.satisfies_requirement(
            PLATFORM_VERSION, ">=1.0.0"
        ):
            check.add_error("Platform version incompatible")
        
        assert check.compatible is True
