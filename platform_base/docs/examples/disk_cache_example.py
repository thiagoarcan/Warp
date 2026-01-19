#!/usr/bin/env python3
"""
Example: Using DiskCache for caching expensive operations in Platform Base.

This example demonstrates how to use DiskCache to cache expensive computational
operations like interpolation, calculus, and data processing.
"""

import time
from pathlib import Path

import numpy as np

from platform_base.caching import DiskCache, create_disk_cache_from_config


def expensive_interpolation(data: np.ndarray, method: str = "spline") -> np.ndarray:
    """Simulate an expensive interpolation operation."""
    print(f"Computing expensive {method} interpolation...")
    time.sleep(1)  # Simulate expensive computation
    
    # Simple mock interpolation
    if method == "spline":
        return data * 1.1 + np.random.normal(0, 0.01, len(data))
    else:
        return np.interp(np.linspace(0, 1, len(data)), np.linspace(0, 1, len(data)), data)


def expensive_derivative(data: np.ndarray, order: int = 1) -> np.ndarray:
    """Simulate an expensive derivative calculation."""
    print(f"Computing expensive {order}-order derivative...")
    time.sleep(0.5)  # Simulate computation
    
    # Simple finite difference
    result = data.copy()
    for _ in range(order):
        result = np.diff(result, prepend=result[0])
    return result


def main():
    """Demonstrate DiskCache usage patterns."""
    
    print("=== Platform Base DiskCache Example ===\n")
    
    # 1. Create cache from platform configuration
    print("1. Creating cache from configuration...")
    config = {
        "enabled": True,
        "ttl_hours": 1,  # 1 hour TTL
        "max_size_gb": 0.1,  # 100MB limit
        "path": ".example_cache"
    }
    
    cache = create_disk_cache_from_config(config)
    print(f"   Cache created at: {cache.location}")
    print(f"   TTL: {cache._ttl_seconds} seconds")
    print(f"   Max size: {cache._max_size_bytes} bytes")
    
    # 2. Manual caching with get/set
    print("\n2. Manual caching example...")
    
    # Generate test data
    test_data = np.random.randn(1000)
    cache_key = f"interpolation_spline_{hash(test_data.tobytes())}"
    
    # Check cache first
    start_time = time.time()
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        print(f"   Cache HIT! Retrieved in {time.time() - start_time:.3f}s")
        interpolated = cached_result
    else:
        print("   Cache MISS. Computing...")
        interpolated = expensive_interpolation(test_data, "spline")
        cache.set(cache_key, interpolated)
        print(f"   Computed and cached in {time.time() - start_time:.3f}s")
    
    # 3. Function decorator caching
    print("\n3. Function decorator caching...")
    
    @cache.cache_function
    def cached_derivative(data_hash: str, data: np.ndarray, order: int = 1) -> np.ndarray:
        """Cached version of expensive_derivative."""
        return expensive_derivative(data, order)
    
    # First call - should compute
    print("   First call (computing)...")
    start_time = time.time()
    deriv1 = cached_derivative("test_data_1", test_data, 1)
    print(f"   Time: {time.time() - start_time:.3f}s")
    
    # Second call - should use cache
    print("   Second call (cached)...")
    start_time = time.time()
    deriv2 = cached_derivative("test_data_1", test_data, 1)
    print(f"   Time: {time.time() - start_time:.3f}s")
    
    assert np.array_equal(deriv1, deriv2), "Results should be identical!"
    
    # 4. Cache statistics and monitoring
    print("\n4. Cache statistics...")
    stats = cache.get_stats()
    
    print(f"   Location: {stats['location']}")
    print(f"   Entries: {stats['entry_count']}")
    print(f"   Size: {stats['current_size_bytes']} bytes")
    print(f"   LRU entries: {stats['lru_entries']}")
    print(f"   Expired: {stats['expired']}")
    if stats['time_to_expiry'] is not None:
        print(f"   Time to expiry: {stats['time_to_expiry']:.1f} seconds")
    
    # 5. Demonstrate cache persistence
    print("\n5. Cache persistence...")
    cache.set("persistent_data", {"computation_id": "test_123", "result": [1, 2, 3]})
    
    # Create new cache instance with same location
    cache2 = DiskCache(location=cache.location)
    persistent_data = cache2.get("persistent_data")
    
    if persistent_data:
        print(f"   Persistent data retrieved: {persistent_data}")
    else:
        print("   No persistent data found")
    
    # 6. Demonstrate size-based eviction
    print("\n6. Size-based LRU eviction...")
    
    # Create small cache
    small_cache = DiskCache(location=".small_cache", max_size_bytes=1024)  # 1KB
    
    print("   Adding data to small cache...")
    small_cache.set("small1", "a" * 200)  # ~200 bytes
    small_cache.set("small2", "b" * 200)  # ~200 bytes
    small_cache.set("small3", "c" * 200)  # ~200 bytes
    
    print(f"   Cache size: {small_cache.get_stats()['current_size_bytes']} bytes")
    
    # Add large item that should trigger eviction
    small_cache.set("large", "x" * 800)  # ~800 bytes - should evict earlier items
    
    print("   After adding large item:")
    print(f"     small1 exists: {small_cache.get('small1') is not None}")
    print(f"     small2 exists: {small_cache.get('small2') is not None}")
    print(f"     small3 exists: {small_cache.get('small3') is not None}")
    print(f"     large exists: {small_cache.get('large') is not None}")
    print(f"     Cache size: {small_cache.get_stats()['current_size_bytes']} bytes")
    
    # 7. Context manager usage
    print("\n7. Context manager usage...")
    
    with DiskCache(location=".context_cache") as ctx_cache:
        ctx_cache.set("context_data", "This will be cleaned up")
        print(f"   Data in context: {ctx_cache.get('context_data')}")
    
    print("   Context manager exited (cache cleaned up)")
    
    # 8. Cleanup
    print("\n8. Cleanup...")
    cache.clear()
    small_cache.clear()
    
    # Remove cache directories
    import shutil
    for cache_dir in [".example_cache", ".small_cache", ".context_cache"]:
        cache_path = Path(cache_dir)
        if cache_path.exists():
            shutil.rmtree(cache_path)
            print(f"   Removed {cache_dir}")
    
    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()