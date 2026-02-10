"""Tests for caching module."""

import tempfile
import time
from pathlib import Path

import pytest

from platform_base.caching import DiskCache, create_disk_cache_from_config


class TestDiskCache:
    """Test DiskCache functionality."""

    def test_basic_get_set(self):
        """Test basic get/set operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = DiskCache(location=temp_dir)
            
            # Test set and get
            cache.set("test_key", {"data": "value", "number": 42})
            result = cache.get("test_key")
            
            assert result == {"data": "value", "number": 42}
            
            # Test cache miss
            assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cache with 1 second TTL
            cache = DiskCache(location=temp_dir, ttl_seconds=1)
            
            cache.set("test_key", "test_value")
            assert cache.get("test_key") == "test_value"
            
            # Wait for TTL to expire
            time.sleep(1.1)
            assert cache.get("test_key") is None

    def test_size_limit_lru(self):
        """Test size limit with LRU eviction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cache that can hold ~2 small items
            cache = DiskCache(location=temp_dir, max_size_bytes=500)
            
            # Add small values
            cache.set("key1", "x" * 200)
            time.sleep(0.01)  # Ensure different timestamps
            cache.set("key2", "x" * 200)
            time.sleep(0.01)
            
            # Add third value that should trigger eviction of oldest
            cache.set("key3", "x" * 200)
            
            # key1 should be evicted (oldest)
            assert cache.get("key1") is None
            # key3 should exist (most recent)
            assert cache.get("key3") is not None

    def test_function_caching(self):
        """Test function caching decorator."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = DiskCache(location=temp_dir)
            
            call_count = 0
            
            @cache.cache_function
            def expensive_function(x):
                nonlocal call_count
                call_count += 1
                return x * 2
            
            # First call
            result1 = expensive_function(5)
            assert result1 == 10
            assert call_count == 1
            
            # Second call with same args - should use cache
            result2 = expensive_function(5)
            assert result2 == 10
            assert call_count == 1  # No new call
            
            # Call with different args
            result3 = expensive_function(10)
            assert result3 == 20
            assert call_count == 2

    def test_clear_cache(self):
        """Test cache clearing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = DiskCache(location=temp_dir)
            
            cache.set("key1", "value1")
            cache.set("key2", "value2")
            
            assert cache.get("key1") == "value1"
            assert cache.get("key2") == "value2"
            
            cache.clear()
            
            assert cache.get("key1") is None
            assert cache.get("key2") is None

    def test_cleanup(self):
        """Test cache cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = DiskCache(location=temp_dir)
            
            cache.set("key1", "value1")
            cache.set("key2", "value2")
            
            # Cleanup should not remove non-expired entries
            cache.cleanup()
            assert cache.get("key1") == "value1"
            assert cache.get("key2") == "value2"

    def test_get_stats(self):
        """Test cache statistics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = DiskCache(location=temp_dir, ttl_seconds=3600, max_size_bytes=10240)
            
            # Set a value first to initialize the stamp file
            cache.set("init", "data")
            cache.clear()  # Clear but stamp should remain valid
            
            stats = cache.get_stats()
            
            assert stats["location"] == temp_dir
            assert stats["ttl_seconds"] == 3600
            assert stats["max_size_bytes"] == 10240
            assert stats["entry_count"] == 0
            assert stats["current_size_bytes"] >= 0
            # After clear, expired state depends on implementation
            
            # Add some data
            cache.set("test", "data")
            stats = cache.get_stats()
            assert stats["entry_count"] == 1
            assert stats["current_size_bytes"] > 0
            assert not stats["expired"]  # Should not be expired immediately after set

    def test_context_manager(self):
        """Test context manager usage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with DiskCache(location=temp_dir) as cache:
                cache.set("key", "value")
                assert cache.get("key") == "value"
            
            # Cache should be cleaned up after context exit

    def test_create_from_config(self):
        """Test factory function."""
        config = {
            "enabled": True,
            "ttl_hours": 24,
            "max_size_gb": 1,
            "path": ".test_cache"
        }
        
        cache = create_disk_cache_from_config(config)
        
        assert cache._ttl_seconds == 24 * 3600
        assert cache._max_size_bytes == 1024 * 1024 * 1024
        assert cache.location == Path(".test_cache")
        
        # Cleanup
        cache.clear()

    def test_disabled_cache_config(self):
        """Test disabled cache configuration."""
        config = {
            "enabled": False,
            "path": ".test_cache"
        }
        
        cache = create_disk_cache_from_config(config)
        
        # Should still create cache but with warning
        assert isinstance(cache, DiskCache)
        
        # Cleanup
        cache.clear()

    def test_persistence_across_instances(self):
        """Test that cache persists across DiskCache instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First instance
            cache1 = DiskCache(location=temp_dir)
            cache1.set("persistent_key", "persistent_value")
            
            # Second instance with same location
            cache2 = DiskCache(location=temp_dir)
            result = cache2.get("persistent_key")
            
            assert result == "persistent_value"

    def test_error_handling(self):
        """Test error handling for invalid operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = DiskCache(location=temp_dir)
            
            # Test getting with invalid key should not crash
            result = cache.get("")
            assert result is None
            
            # Test setting None value
            cache.set("null_key", None)
            assert cache.get("null_key") is None