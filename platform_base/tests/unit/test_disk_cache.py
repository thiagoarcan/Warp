"""
Testes unitários para sistema de cache disk conforme PRD.
"""
import pytest
import tempfile
import time
from pathlib import Path

from platform_base.caching.disk import DiskCache, create_disk_cache_from_config


class TestDiskCache:
    """Testa sistema de cache disk com TTL e LRU"""
    
    def test_basic_cache_operations(self):
        """Testa operações básicas de get/set"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(tmpdir, ttl_seconds=None, max_size_bytes=None)
            
            # Test set/get
            cache.set("key1", "value1")
            assert cache.get("key1") == "value1"
            
            # Test cache miss
            assert cache.get("nonexistent") is None
            
    def test_ttl_expiration(self):
        """Testa expiração TTL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(tmpdir, ttl_seconds=1, max_size_bytes=None)
            
            cache.set("key1", "value1")
            assert cache.get("key1") == "value1"
            
            # Wait for expiration
            time.sleep(1.1)
            
            assert cache.get("key1") is None  # Should be expired
            
    def test_size_limit_enforcement(self):
        """Testa limite de tamanho com LRU eviction"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Small cache size for testing
            cache = DiskCache(tmpdir, ttl_seconds=None, max_size_bytes=1000)
            
            # Add items that exceed size limit
            large_value = "x" * 500
            cache.set("key1", large_value)
            cache.set("key2", large_value)
            cache.set("key3", large_value)  # Should trigger eviction
            
            # key1 should be evicted (LRU)
            assert cache.get("key1") is None
            assert cache.get("key2") == large_value
            assert cache.get("key3") == large_value
            
    def test_cache_from_config(self):
        """Testa criação de cache a partir de configuração"""
        config = {
            "enabled": True,
            "ttl_hours": 1,
            "max_size_gb": 0.001,  # 1MB
            "path": ".test_cache"
        }
        
        cache = create_disk_cache_from_config(config)
        
        # Test configuration was applied
        assert cache._ttl_seconds == 3600  # 1 hour
        assert cache._max_size_bytes == 1024 * 1024  # 1MB
        
        # Cleanup
        cache.clear()
        
    def test_function_caching(self):
        """Testa caching de funções com joblib"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(tmpdir, ttl_seconds=None, max_size_bytes=None)
            
            call_count = 0
            
            @cache.cache_function
            def expensive_function(x):
                nonlocal call_count
                call_count += 1
                return x * 2
            
            # First call - should execute function
            result1 = expensive_function(5)
            assert result1 == 10
            assert call_count == 1
            
            # Second call - should use cache
            result2 = expensive_function(5)
            assert result2 == 10
            assert call_count == 1  # Function not called again
            
    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(tmpdir, ttl_seconds=3600, max_size_bytes=1000000)
            
            cache.set("key1", "value1")
            cache.set("key2", "value2")
            
            stats = cache.get_stats()
            
            assert stats["entry_count"] == 2
            assert stats["ttl_seconds"] == 3600
            assert stats["max_size_bytes"] == 1000000
            assert stats["expired"] is False
            assert "current_size_bytes" in stats
            
    def test_cache_cleanup(self):
        """Testa limpeza automática do cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = DiskCache(tmpdir, ttl_seconds=None, max_size_bytes=None)
            
            cache.set("key1", "value1")
            cache.set("key2", "value2")
            
            # Verify items exist
            assert cache.get("key1") == "value1"
            assert cache.get("key2") == "value2"
            
            # Clear cache
            cache.clear()
            
            # Verify items are gone
            assert cache.get("key1") is None
            assert cache.get("key2") is None
            
    def test_context_manager(self):
        """Testa uso como context manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with DiskCache(tmpdir) as cache:
                cache.set("key1", "value1")
                assert cache.get("key1") == "value1"
            
            # Cache should have been cleaned up
            # (Can't easily test this without implementation details)