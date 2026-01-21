#!/usr/bin/env python3
"""
Test script for DTW plugin

This script validates the DTW plugin functionality and demonstrates
its integration with the Platform Base plugin system.
"""

import sys
import numpy as np
from pathlib import Path

# Add plugin directory to path for testing
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

from plugin import DTWPlugin, DTWConfig, DTWResult


def test_basic_functionality():
    """Test basic DTW functionality"""
    print("=== Testing Basic DTW Functionality ===")
    
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        # Create simple test series
        series1 = np.array([1, 2, 3, 4, 5])
        series2 = np.array([1, 3, 2, 4, 5])  # Different order should give non-zero distance
        
        # Test basic DTW
        config = DTWConfig(normalize_distance=True, return_path=True)
        result = plugin.compute_dtw_distance(series1, series2, config)
        
        print(f"DEBUG: result.distance = {result.distance}")
        print(f"DEBUG: result.normalized_distance = {result.normalized_distance}")
        
        assert isinstance(result, DTWResult)
        assert result.distance > 0  # Should be > 0 for different series
        assert result.normalized_distance is not None
        assert len(result.path) > 0
        
        print(f"[OK] Basic DTW distance: {result.distance:.4f}")
        print(f"[OK] Normalized distance: {result.normalized_distance:.4f}")
        print(f"[OK] Path length: {len(result.path)}")
        
    finally:
        plugin.cleanup()


def test_constrained_dtw():
    """Test constrained DTW with Sakoe-Chiba band"""
    print("\n=== Testing Constrained DTW ===")
    
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        # Create longer series
        t1 = np.linspace(0, 2*np.pi, 50)
        t2 = np.linspace(0, 2*np.pi, 55)
        
        series1 = np.sin(t1)
        series2 = np.sin(t2 + 0.1)  # Phase shifted
        
        # Test with different window sizes
        for window in [5, 10, 20]:
            config = DTWConfig(window_size=window, normalize_distance=True)
            result = plugin.compute_dtw_distance(series1, series2, config)
            
            print(f"[OK] Window size {window}: distance = {result.distance:.4f}")
            
    finally:
        plugin.cleanup()


def test_distance_metrics():
    """Test different distance metrics"""
    print("\n=== Testing Distance Metrics ===")
    
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        # Create test series
        series1 = np.random.randn(30)
        series2 = series1 + 0.1 * np.random.randn(30)  # Noisy version
        
        metrics = ['euclidean', 'manhattan', 'cosine']
        
        for metric in metrics:
            config = DTWConfig(distance_metric=metric, normalize_distance=True)
            result = plugin.compute_dtw_distance(series1, series2, config)
            
            print(f"[OK] {metric} distance: {result.normalized_distance:.4f}")
            
    finally:
        plugin.cleanup()


def test_batch_processing():
    """Test batch DTW processing"""
    print("\n=== Testing Batch Processing ===")
    
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        # Create multiple series
        np.random.seed(42)  # For reproducible results
        series_list = [
            np.sin(np.linspace(0, 2*np.pi, 30)),
            np.cos(np.linspace(0, 2*np.pi, 30)),
            np.sin(np.linspace(0, 4*np.pi, 30)),
            np.random.randn(30)
        ]
        
        config = DTWConfig(normalize_distance=True)
        distance_matrix = plugin.compute_dtw_batch(series_list, config)
        
        assert distance_matrix.shape == (4, 4)
        assert np.allclose(distance_matrix, distance_matrix.T)  # Should be symmetric
        assert np.allclose(np.diag(distance_matrix), 0)  # Diagonal should be zero
        
        print(f"[OK] Batch processing: {distance_matrix.shape} distance matrix")
        print(f"[OK] Distance matrix symmetric: {np.allclose(distance_matrix, distance_matrix.T)}")
        
    finally:
        plugin.cleanup()


def test_caching():
    """Test caching functionality"""
    print("\n=== Testing Caching ===")
    
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        series1 = np.array([1, 2, 3, 4, 5])
        series2 = np.array([1, 3, 2, 4, 5])
        config = DTWConfig()
        
        # First computation
        result1 = plugin.compute_dtw_distance(series1, series2, config)
        time1 = result1.execution_time
        
        # Second computation (should be cached)
        result2 = plugin.compute_dtw_distance(series1, series2, config)
        time2 = result2.execution_time
        
        assert result1.distance == result2.distance
        print(f"[OK] Caching works: same distance {result1.distance:.4f}")
        print(f"[OK] First computation: {time1:.6f}s")
        print(f"[OK] Cached computation: {time2:.6f}s")
        
    finally:
        plugin.cleanup()


def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        # Test empty series
        try:
            plugin.compute_dtw_distance(np.array([]), np.array([1, 2, 3]))
            assert False, "Should have raised ValueError"
        except ValueError:
            print("[OK] Empty series error handling works")
        
        # Test invalid distance metric
        try:
            config = DTWConfig(distance_metric='invalid_metric')
            plugin.compute_dtw_distance(np.array([1, 2]), np.array([1, 2]), config)
            assert False, "Should have raised ValueError"
        except ValueError:
            print("[OK] Invalid metric error handling works")
        
    finally:
        plugin.cleanup()


def test_plugin_protocol():
    """Test plugin protocol compliance"""
    print("\n=== Testing Plugin Protocol ===")
    
    plugin = DTWPlugin()
    
    # Test required properties
    assert hasattr(plugin, 'name')
    assert hasattr(plugin, 'version')
    assert hasattr(plugin, 'description')
    
    assert plugin.name == "dtw_plugin"
    assert plugin.version == "1.0.0"
    assert isinstance(plugin.description, str)
    
    # Test required methods
    assert hasattr(plugin, 'initialize')
    assert hasattr(plugin, 'cleanup')
    
    print("[OK] Plugin protocol compliance verified")
    print(f"[OK] Plugin name: {plugin.name}")
    print(f"[OK] Plugin version: {plugin.version}")


def test_statistics():
    """Test plugin statistics"""
    print("\n=== Testing Statistics ===")
    
    plugin = DTWPlugin()
    plugin.initialize()
    
    try:
        # Perform some computations with different inputs to avoid caching
        series1 = np.array([1, 2, 3, 4])
        series2 = np.array([1, 3, 2, 4])
        series3 = np.array([2, 1, 4, 3])
        series4 = np.array([4, 3, 2, 1])
        
        # Disable cache for this test
        plugin._distance_cache.clear()
        
        plugin.compute_dtw_distance(series1, series2)
        plugin.compute_dtw_distance(series2, series3)  
        plugin.compute_dtw_distance(series3, series4)
        
        stats = plugin.get_statistics()
        
        assert stats['execution_count'] >= 3
        assert stats['total_execution_time'] > 0
        assert stats['average_execution_time'] > 0
        assert 'plugin_name' in stats
        assert 'version' in stats
        
        print(f"[OK] Execution count: {stats['execution_count']}")
        print(f"[OK] Total time: {stats['total_execution_time']:.6f}s")
        print(f"[OK] Average time: {stats['average_execution_time']:.6f}s")
        
    finally:
        plugin.cleanup()


def run_all_tests():
    """Run all tests"""
    print("Running DTW Plugin Tests\n")
    
    try:
        test_plugin_protocol()
        test_basic_functionality()
        test_constrained_dtw()
        test_distance_metrics()
        test_batch_processing()
        test_caching()
        test_error_handling()
        test_statistics()
        
        print("\n" + "="*50)
        print("All tests passed! [OK]")
        print("DTW Plugin is working correctly.")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)