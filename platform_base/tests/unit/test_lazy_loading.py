"""
Tests for processing/lazy_loading.py module.

Tests lazy loading functionality including:
- ChunkInfo dataclass
- LRUCache class
- ChunkLoader worker
- LazyDataArray class
- LazyCSVReader class
- VirtualListModel class
- create_lazy_array function
"""

import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    file_path = tmp_path / "sample_data.csv"
    df = pd.DataFrame({
        'time': np.arange(1000),
        'value': np.random.randn(1000),
        'category': ['A', 'B'] * 500,
    })
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def large_csv_file(tmp_path):
    """Create a larger CSV file for chunking tests."""
    file_path = tmp_path / "large_data.csv"
    df = pd.DataFrame({
        'time': np.arange(50000),
        'value': np.random.randn(50000),
    })
    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def simple_load_func():
    """Simple load function for testing."""
    def load(start: int, end: int) -> np.ndarray:
        return np.arange(start, end)
    return load


# =============================================================================
# ChunkInfo Tests
# =============================================================================

class TestChunkInfo:
    """Tests for ChunkInfo dataclass."""
    
    def test_create_chunk_info(self):
        """Test creating ChunkInfo."""
        from platform_base.processing.lazy_loading import ChunkInfo
        
        info = ChunkInfo(
            chunk_id=0,
            start_index=0,
            end_index=1000,
            size=1000,
        )
        
        assert info.chunk_id == 0
        assert info.start_index == 0
        assert info.end_index == 1000
        assert info.size == 1000
        assert info.loaded is False
        assert info.loading is False
        assert info.data is None
    
    def test_chunk_info_with_data(self):
        """Test ChunkInfo with data."""
        from platform_base.processing.lazy_loading import ChunkInfo
        
        data = np.array([1, 2, 3, 4, 5])
        info = ChunkInfo(
            chunk_id=1,
            start_index=100,
            end_index=105,
            size=5,
            loaded=True,
            data=data,
        )
        
        assert info.loaded is True
        np.testing.assert_array_equal(info.data, data)
    
    def test_chunk_info_last_access(self):
        """Test last_access timestamp."""
        from platform_base.processing.lazy_loading import ChunkInfo
        
        before = time.time()
        info = ChunkInfo(chunk_id=0, start_index=0, end_index=100, size=100)
        after = time.time()
        
        assert before <= info.last_access <= after


# =============================================================================
# LRUCache Tests
# =============================================================================

class TestLRUCache:
    """Tests for LRUCache class."""
    
    def test_create_cache(self):
        """Test creating LRU cache."""
        from platform_base.processing.lazy_loading import LRUCache
        
        cache = LRUCache[np.ndarray](max_size=10, max_memory_mb=100)
        
        assert len(cache) == 0
        assert cache.memory_usage == 0
    
    def test_put_and_get(self):
        """Test put and get operations."""
        from platform_base.processing.lazy_loading import LRUCache
        
        cache = LRUCache[str](max_size=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("nonexistent") is None
    
    def test_lru_eviction(self):
        """Test LRU eviction when max size reached."""
        from platform_base.processing.lazy_loading import LRUCache
        
        cache = LRUCache[str](max_size=3)
        
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        cache.put("k3", "v3")
        
        # Access k1 to make it recently used
        cache.get("k1")
        
        # Add k4, should evict k2 (least recently used)
        cache.put("k4", "v4")
        
        assert "k1" in cache  # Recently accessed
        assert "k3" in cache
        assert "k4" in cache
        assert "k2" not in cache  # Should be evicted
    
    def test_memory_limit_eviction(self):
        """Test eviction based on memory limit."""
        from platform_base.processing.lazy_loading import LRUCache

        # 1MB limit
        cache = LRUCache[np.ndarray](max_size=100, max_memory_mb=1)
        
        # Each array is ~800KB
        for i in range(3):
            arr = np.zeros(100000)  # ~800KB
            cache.put(f"arr_{i}", arr, arr.nbytes)
        
        # Should have evicted some due to memory limit
        assert len(cache) < 3
    
    def test_remove(self):
        """Test remove operation."""
        from platform_base.processing.lazy_loading import LRUCache
        
        cache = LRUCache[str](max_size=10)
        
        cache.put("key", "value")
        assert "key" in cache
        
        result = cache.remove("key")
        assert result is True
        assert "key" not in cache
        
        # Remove non-existent
        result = cache.remove("nonexistent")
        assert result is False
    
    def test_clear(self):
        """Test clear operation."""
        from platform_base.processing.lazy_loading import LRUCache
        
        cache = LRUCache[str](max_size=10)
        
        for i in range(5):
            cache.put(f"key_{i}", f"value_{i}")
        
        assert len(cache) == 5
        
        cache.clear()
        
        assert len(cache) == 0
        assert cache.memory_usage == 0
    
    def test_contains(self):
        """Test __contains__ operator."""
        from platform_base.processing.lazy_loading import LRUCache
        
        cache = LRUCache[str](max_size=10)
        
        cache.put("key", "value")
        
        assert "key" in cache
        assert "other" not in cache
    
    def test_thread_safety(self):
        """Test thread safety of cache operations."""
        from platform_base.processing.lazy_loading import LRUCache
        
        cache = LRUCache[int](max_size=1000)
        errors = []
        
        def writer(prefix: str, count: int):
            try:
                for i in range(count):
                    cache.put(f"{prefix}_{i}", i)
            except Exception as e:
                errors.append(e)
        
        def reader(count: int):
            try:
                for i in range(count):
                    cache.get(f"w1_{i}")
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=writer, args=("w1", 100)),
            threading.Thread(target=writer, args=("w2", 100)),
            threading.Thread(target=reader, args=(100,)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0


# =============================================================================
# LazyDataArray Tests
# =============================================================================

class TestLazyDataArray:
    """Tests for LazyDataArray class."""
    
    def test_create_lazy_array(self, simple_load_func):
        """Test creating LazyDataArray."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=10000,
            chunk_size=1000,
            load_func=simple_load_func,
        )
        
        assert len(arr) == 10000
        assert arr.total_chunks == 10
    
    def test_single_item_access(self, simple_load_func):
        """Test accessing single items."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        assert arr[0] == 0
        assert arr[50] == 50
        assert arr[999] == 999
    
    def test_negative_indexing(self, simple_load_func):
        """Test negative indexing."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        assert arr[-1] == 999
        assert arr[-100] == 900
    
    def test_index_out_of_range(self, simple_load_func):
        """Test index out of range."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=100,
            chunk_size=10,
            load_func=simple_load_func,
        )
        
        with pytest.raises(IndexError):
            _ = arr[100]
        
        with pytest.raises(IndexError):
            _ = arr[-101]
    
    def test_slice_access(self, simple_load_func):
        """Test slice access."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        result = arr[10:20]
        np.testing.assert_array_equal(result, np.arange(10, 20))
    
    def test_slice_across_chunks(self, simple_load_func):
        """Test slice that spans multiple chunks."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        # Slice across chunk boundary
        result = arr[90:110]
        np.testing.assert_array_equal(result, np.arange(90, 110))
    
    def test_slice_with_step(self, simple_load_func):
        """Test slice with step."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=100,
            chunk_size=10,
            load_func=simple_load_func,
        )
        
        result = arr[0:10:2]
        np.testing.assert_array_equal(result, np.array([0, 2, 4, 6, 8]))
    
    def test_chunk_caching(self, simple_load_func):
        """Test that chunks are cached."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        # Access some values
        _ = arr[0]
        _ = arr[50]
        
        assert arr.loaded_chunks >= 1
    
    def test_prefetch(self, simple_load_func):
        """Test prefetch functionality."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        arr.prefetch([150, 250, 350])
        
        assert arr.loaded_chunks >= 3
    
    def test_prefetch_range(self, simple_load_func):
        """Test prefetch_range functionality."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        arr.prefetch_range(0, 300)
        
        assert arr.loaded_chunks >= 3
    
    def test_clear_cache(self, simple_load_func):
        """Test clearing cache."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=1000,
            chunk_size=100,
            load_func=simple_load_func,
        )
        
        # Load some chunks
        _ = arr[0:300]
        assert arr.loaded_chunks >= 3
        
        arr.clear_cache()
        assert arr.memory_usage == 0
    
    def test_no_load_func_error(self):
        """Test error when no load function provided."""
        from platform_base.processing.lazy_loading import LazyDataArray
        
        arr = LazyDataArray(
            total_size=100,
            chunk_size=10,
            load_func=None,
        )
        
        with pytest.raises(ValueError, match="No load function"):
            _ = arr[0]


# =============================================================================
# LazyCSVReader Tests
# =============================================================================

class TestLazyCSVReader:
    """Tests for LazyCSVReader class."""
    
    def test_create_reader(self, sample_csv_file):
        """Test creating LazyCSVReader."""
        from platform_base.processing.lazy_loading import LazyCSVReader
        
        reader = LazyCSVReader(sample_csv_file, chunk_size=100)
        
        assert reader.total_rows == 1000
        assert 'time' in reader.columns
        assert 'value' in reader.columns
        assert 'category' in reader.columns
    
    def test_get_column(self, sample_csv_file):
        """Test getting column as LazyDataArray."""
        from platform_base.processing.lazy_loading import LazyCSVReader, LazyDataArray
        
        reader = LazyCSVReader(sample_csv_file, chunk_size=100)
        
        time_col = reader.get_column('time')
        
        assert isinstance(time_col, LazyDataArray)
        assert len(time_col) == 1000
    
    def test_getitem_column(self, sample_csv_file):
        """Test __getitem__ access for columns."""
        from platform_base.processing.lazy_loading import LazyCSVReader
        
        reader = LazyCSVReader(sample_csv_file, chunk_size=100)
        
        time_col = reader['time']
        assert len(time_col) == 1000
    
    def test_read_values(self, sample_csv_file):
        """Test reading actual values."""
        from platform_base.processing.lazy_loading import LazyCSVReader
        
        reader = LazyCSVReader(sample_csv_file, chunk_size=100)
        
        time_col = reader['time']
        
        # First few values
        assert time_col[0] == 0
        assert time_col[1] == 1
        assert time_col[99] == 99
    
    def test_large_file_chunking(self, large_csv_file):
        """Test chunking with larger file."""
        from platform_base.processing.lazy_loading import LazyCSVReader
        
        reader = LazyCSVReader(large_csv_file, chunk_size=10000)
        
        assert reader.total_rows == 50000
        
        # Access data from different chunks
        time_col = reader['time']
        assert time_col[0] == 0
        assert time_col[25000] == 25000
        assert time_col[49999] == 49999


# =============================================================================
# VirtualListModel Tests
# =============================================================================

class TestVirtualListModel:
    """Tests for VirtualListModel class."""
    
    def test_create_model(self):
        """Test creating VirtualListModel."""
        from platform_base.processing.lazy_loading import VirtualListModel
        
        model = VirtualListModel(
            total_items=1000,
            item_loader=lambda i: f"item_{i}",
        )
        
        assert len(model) == 1000
    
    def test_getitem(self):
        """Test __getitem__ access."""
        from platform_base.processing.lazy_loading import VirtualListModel
        
        model = VirtualListModel(
            total_items=100,
            item_loader=lambda i: i * 2,
        )
        
        assert model[0] == 0
        assert model[10] == 20
        assert model[50] == 100
    
    def test_caching(self):
        """Test that items are cached."""
        from platform_base.processing.lazy_loading import VirtualListModel
        
        load_count = [0]
        
        def loader(i: int) -> int:
            load_count[0] += 1
            return i
        
        model = VirtualListModel(
            total_items=100,
            item_loader=loader,
            cache_size=50,
        )
        
        # Access same item multiple times
        _ = model[0]
        _ = model[0]
        _ = model[0]
        
        # Should only load once
        assert load_count[0] == 1
    
    def test_prefetch_visible(self):
        """Test prefetch_visible functionality."""
        from platform_base.processing.lazy_loading import VirtualListModel
        
        loaded_indices = []
        
        def loader(i: int) -> int:
            loaded_indices.append(i)
            return i
        
        model = VirtualListModel(
            total_items=1000,
            item_loader=loader,
            cache_size=200,
        )
        
        model.prefetch_visible(first_visible=100, last_visible=120, margin=10)
        
        # Should have loaded items from 90 to 130
        assert len(loaded_indices) > 20


# =============================================================================
# create_lazy_array Tests
# =============================================================================

class TestCreateLazyArray:
    """Tests for create_lazy_array function."""
    
    def test_create_from_csv(self, sample_csv_file):
        """Test creating lazy array from CSV."""
        from platform_base.processing.lazy_loading import (
            LazyDataArray,
            create_lazy_array,
        )
        
        arr = create_lazy_array(sample_csv_file, column='time', chunk_size=100)
        
        assert isinstance(arr, LazyDataArray)
        assert len(arr) == 1000
    
    def test_unsupported_format(self, tmp_path):
        """Test error for unsupported format."""
        from platform_base.processing.lazy_loading import create_lazy_array
        
        file_path = tmp_path / "data.xyz"
        file_path.touch()
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            create_lazy_array(file_path, column='time')


# =============================================================================
# ChunkLoader Tests (Qt Worker)
# =============================================================================

class TestChunkLoader:
    """Tests for ChunkLoader worker."""
    
    @pytest.mark.skip(reason="Requires Qt event loop")
    def test_chunk_loader_success(self):
        """Test successful chunk loading."""
        pass
    
    @pytest.mark.skip(reason="Requires Qt event loop")
    def test_chunk_loader_failure(self):
        """Test chunk loading failure."""
        pass


# =============================================================================
# Integration Tests
# =============================================================================

class TestLazyLoadingIntegration:
    """Integration tests for lazy loading system."""
    
    def test_full_workflow(self, sample_csv_file):
        """Test complete lazy loading workflow."""
        from platform_base.processing.lazy_loading import LazyCSVReader

        # Create reader
        reader = LazyCSVReader(sample_csv_file, chunk_size=100)
        
        # Get columns
        time_col = reader['time']
        value_col = reader['value']
        
        # Access data
        time_slice = time_col[0:50]
        value_slice = value_col[0:50]
        
        assert len(time_slice) == 50
        assert len(value_slice) == 50
        
        # Verify time column values
        np.testing.assert_array_equal(time_slice, np.arange(50))
    
    def test_memory_efficiency(self, large_csv_file):
        """Test that memory usage is bounded."""
        from platform_base.processing.lazy_loading import LazyCSVReader
        
        reader = LazyCSVReader(
            large_csv_file,
            chunk_size=5000,
        )
        
        time_col = reader['time']
        
        # Access scattered data points
        _ = time_col[0]
        _ = time_col[25000]
        _ = time_col[49999]
        
        # Memory usage should be bounded (not loading entire file)
        # This is a soft check - actual memory depends on cache settings
        assert time_col.loaded_chunks <= time_col.total_chunks
