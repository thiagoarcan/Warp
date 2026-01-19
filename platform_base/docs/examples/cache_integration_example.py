#!/usr/bin/env python3
"""
Example: Integration of DiskCache with Platform Base configuration system.

This example shows how DiskCache integrates with the platform.yaml configuration
and how it can be used in real processing pipelines.
"""

import yaml
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from platform_base.caching import create_disk_cache_from_config
from platform_base.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging(level="INFO", json_logs=False)
logger = get_logger(__name__)


def load_platform_config() -> Dict[str, Any]:
    """Load platform configuration from YAML file."""
    config_path = Path(__file__).parent.parent.parent / "configs" / "platform.yaml"
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info("platform_config_loaded", config_path=str(config_path))
        return config
    except Exception as e:
        logger.error("platform_config_load_failed", error=str(e))
        # Fallback configuration
        return {
            "performance": {
                "cache": {
                    "disk": {
                        "enabled": True,
                        "ttl_hours": 24,
                        "max_size_gb": 1,
                        "path": ".cache"
                    }
                }
            }
        }


class CachedDataProcessor:
    """Example data processor with integrated caching."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize processor with configuration."""
        cache_config = config.get("performance", {}).get("cache", {}).get("disk", {})
        self.cache = create_disk_cache_from_config(cache_config)
        
        logger.info(
            "processor_initialized",
            cache_location=str(self.cache.location),
            cache_enabled=cache_config.get("enabled", True)
        )
    
    def load_and_preprocess_data(self, file_path: str) -> pd.DataFrame:
        """Load and preprocess data with caching."""
        cache_key = f"preprocessed_data_{hash(file_path)}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info("data_cache_hit", file_path=file_path)
            return pd.DataFrame(cached_data)
        
        logger.info("data_cache_miss_processing", file_path=file_path)
        
        # Simulate expensive data loading and preprocessing
        # In real implementation, this would load from file_path
        data = self._simulate_data_loading(file_path)
        processed_data = self._simulate_preprocessing(data)
        
        # Cache the result
        self.cache.set(cache_key, processed_data.to_dict())
        logger.info("data_cached", file_path=file_path, shape=processed_data.shape)
        
        return processed_data
    
    @property
    def interpolate_series(self):
        """Cached interpolation method."""
        @self.cache.cache_function
        def _interpolate(series_id: str, data: np.ndarray, method: str) -> np.ndarray:
            """Perform expensive interpolation."""
            logger.info("interpolation_computing", series_id=series_id, method=method)
            
            # Simulate expensive interpolation computation
            import time
            time.sleep(0.1)  # Simulate computation time
            
            if method == "linear":
                # Simple linear interpolation simulation
                return np.interp(
                    np.arange(len(data)),
                    np.arange(len(data))[~np.isnan(data)],
                    data[~np.isnan(data)]
                )
            elif method == "spline":
                # Spline interpolation simulation
                from scipy import interpolate
                valid_indices = ~np.isnan(data)
                if np.sum(valid_indices) > 3:  # Need at least 4 points for spline
                    f = interpolate.interp1d(
                        np.arange(len(data))[valid_indices],
                        data[valid_indices],
                        kind='cubic',
                        fill_value='extrapolate'
                    )
                    return f(np.arange(len(data)))
                else:
                    # Fall back to linear for insufficient data
                    return self._interpolate(series_id, data, "linear")
            else:
                raise ValueError(f"Unknown interpolation method: {method}")
        
        return _interpolate
    
    @property
    def calculate_derivative(self):
        """Cached derivative calculation."""
        @self.cache.cache_function
        def _derivative(series_id: str, data: np.ndarray, order: int = 1) -> np.ndarray:
            """Calculate derivative with caching."""
            logger.info("derivative_computing", series_id=series_id, order=order)
            
            # Simulate expensive derivative calculation
            import time
            time.sleep(0.05)  # Simulate computation time
            
            result = data.copy()
            for i in range(order):
                result = np.gradient(result)
            
            return result
        
        return _derivative
    
    def process_series(self, series_data: pd.Series, series_id: str, operations: list) -> Dict[str, np.ndarray]:
        """Process a series with multiple operations, using cache for each step."""
        results = {"original": series_data.values}
        current_data = series_data.values
        
        for operation in operations:
            op_type = operation.get("type")
            op_params = operation.get("params", {})
            
            if op_type == "interpolate":
                method = op_params.get("method", "linear")
                current_data = self.interpolate_series(
                    f"{series_id}_{op_type}_{method}",
                    current_data,
                    method
                )
                results[f"interpolated_{method}"] = current_data
                
            elif op_type == "derivative":
                order = op_params.get("order", 1)
                current_data = self.calculate_derivative(
                    f"{series_id}_{op_type}_{order}",
                    current_data,
                    order
                )
                results[f"derivative_{order}"] = current_data
                
            else:
                logger.warning("unknown_operation", operation=op_type)
        
        return results
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        stats = self.cache.get_stats()
        
        # Convert bytes to human readable
        size_mb = stats["current_size_bytes"] / (1024 * 1024)
        max_size_mb = stats["max_size_bytes"] / (1024 * 1024) if stats["max_size_bytes"] else None
        
        return {
            "location": stats["location"],
            "size_mb": round(size_mb, 2),
            "max_size_mb": max_size_mb,
            "entry_count": stats["entry_count"],
            "ttl_hours": stats["ttl_seconds"] / 3600 if stats["ttl_seconds"] else None,
            "expired": stats["expired"],
            "time_to_expiry_hours": stats["time_to_expiry"] / 3600 if stats["time_to_expiry"] else None
        }
    
    def _simulate_data_loading(self, file_path: str) -> pd.DataFrame:
        """Simulate loading data from file."""
        # Generate synthetic time series data
        np.random.seed(hash(file_path) % 2**32)
        
        n_points = 1000
        timestamps = pd.date_range('2024-01-01', periods=n_points, freq='1min')
        
        data = {
            'timestamp': timestamps,
            'temperature': 20 + 10 * np.sin(np.arange(n_points) * 0.01) + np.random.normal(0, 1, n_points),
            'pressure': 1000 + 50 * np.cos(np.arange(n_points) * 0.02) + np.random.normal(0, 5, n_points),
            'flow_rate': 100 + 20 * np.sin(np.arange(n_points) * 0.005) + np.random.normal(0, 2, n_points)
        }
        
        df = pd.DataFrame(data)
        
        # Introduce some NaN values to simulate missing data
        missing_indices = np.random.choice(n_points, size=int(n_points * 0.05), replace=False)
        df.loc[missing_indices, ['temperature', 'pressure']] = np.nan
        
        return df
    
    def _simulate_preprocessing(self, data: pd.DataFrame) -> pd.DataFrame:
        """Simulate expensive preprocessing."""
        import time
        time.sleep(0.2)  # Simulate preprocessing time
        
        # Simple preprocessing: outlier removal and smoothing
        for col in ['temperature', 'pressure', 'flow_rate']:
            if col in data.columns:
                # Remove outliers (simple z-score method)
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                data.loc[z_scores > 3, col] = np.nan
                
                # Simple smoothing (moving average)
                data[col] = data[col].rolling(window=5, center=True).mean()
        
        return data


def main():
    """Demonstrate cache integration with platform configuration."""
    
    print("=== Platform Base Cache Integration Example ===\n")
    
    # 1. Load platform configuration
    print("1. Loading platform configuration...")
    config = load_platform_config()
    cache_config = config.get("performance", {}).get("cache", {}).get("disk", {})
    print(f"   Cache enabled: {cache_config.get('enabled', False)}")
    print(f"   TTL hours: {cache_config.get('ttl_hours', 'None')}")
    print(f"   Max size GB: {cache_config.get('max_size_gb', 'None')}")
    print(f"   Cache path: {cache_config.get('path', 'None')}")
    
    # 2. Initialize processor with cache
    print("\n2. Initializing data processor...")
    processor = CachedDataProcessor(config)
    
    # 3. Process data with caching
    print("\n3. Processing data (first time - should compute)...")
    
    # Simulate processing multiple files
    files = ["sensor_data_A.csv", "sensor_data_B.csv", "sensor_data_A.csv"]  # Note: A appears twice
    
    for i, file_path in enumerate(files):
        print(f"\n   Processing {file_path}...")
        
        # Load and preprocess (cached)
        start_time = pd.Timestamp.now()
        data = processor.load_and_preprocess_data(file_path)
        load_time = (pd.Timestamp.now() - start_time).total_seconds()
        print(f"     Load time: {load_time:.3f}s")
        
        # Process series with multiple operations
        operations = [
            {"type": "interpolate", "params": {"method": "linear"}},
            {"type": "derivative", "params": {"order": 1}},
            {"type": "interpolate", "params": {"method": "spline"}},
        ]
        
        # Process temperature series
        temp_series = data['temperature']
        start_time = pd.Timestamp.now()
        results = processor.process_series(temp_series, f"temp_{i}", operations)
        process_time = (pd.Timestamp.now() - start_time).total_seconds()
        print(f"     Process time: {process_time:.3f}s")
        print(f"     Results: {list(results.keys())}")
    
    # 4. Show cache statistics
    print("\n4. Cache statistics:")
    cache_info = processor.get_cache_info()
    for key, value in cache_info.items():
        print(f"   {key}: {value}")
    
    # 5. Demonstrate cache persistence
    print("\n5. Testing cache persistence...")
    
    # Create new processor instance (same config)
    processor2 = CachedDataProcessor(config)
    
    # Try to load same data (should hit cache)
    start_time = pd.Timestamp.now()
    data_cached = processor2.load_and_preprocess_data("sensor_data_A.csv")
    cached_load_time = (pd.Timestamp.now() - start_time).total_seconds()
    print(f"   Cached load time: {cached_load_time:.3f}s")
    
    # 6. Cache maintenance
    print("\n6. Cache maintenance...")
    print("   Before cleanup:")
    before_stats = processor.cache.get_stats()
    print(f"     Entries: {before_stats['entry_count']}")
    print(f"     Size: {before_stats['current_size_bytes']} bytes")
    
    processor.cache.cleanup()
    
    print("   After cleanup:")
    after_stats = processor.cache.get_stats()
    print(f"     Entries: {after_stats['entry_count']}")
    print(f"     Size: {after_stats['current_size_bytes']} bytes")
    
    # 7. Clear cache for cleanup
    print("\n7. Cleaning up...")
    processor.cache.clear()
    print("   Cache cleared")
    
    print("\n=== Integration example completed ===")


if __name__ == "__main__":
    main()