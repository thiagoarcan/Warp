# DTW (Dynamic Time Warping) Plugin

A comprehensive Dynamic Time Warping plugin for Platform Base v2.0, providing advanced temporal signal alignment and similarity measurement capabilities.

## Overview

Dynamic Time Warping (DTW) is a powerful algorithm for measuring similarity between temporal sequences that may vary in speed or timing. This plugin implements DTW with various optimizations and constraints, making it suitable for a wide range of applications in signal processing, time series analysis, and pattern recognition.

## Features

### Core DTW Functionality
- **Standard DTW**: Unconstrained dynamic time warping
- **Constrained DTW**: Sakoe-Chiba band constraints for improved performance
- **Multiple Distance Metrics**: Euclidean, Manhattan, and Cosine distance
- **Step Patterns**: Symmetric and asymmetric warping patterns
- **Batch Processing**: Efficient pairwise distance computation for multiple series

### Advanced Features  
- **Caching System**: Intelligent caching for repeated computations
- **Visualization**: Interactive DTW alignment and cost matrix plots
- **Performance Monitoring**: Detailed execution statistics and timing
- **Memory Optimization**: Configurable memory limits and efficient algorithms
- **Error Handling**: Robust error handling and validation

### Security & Sandboxing
- **Moderate Sandbox Level**: Balanced security and functionality
- **Resource Limits**: Configurable CPU and memory constraints
- **Module Restrictions**: Controlled access to system modules
- **Execution Monitoring**: Real-time resource usage tracking

## Installation

The plugin is automatically discovered by Platform Base when placed in the `plugins/` directory. Dependencies will be checked during plugin loading.

### Required Dependencies
- numpy >= 1.20.0
- scipy >= 1.7.0 (optional, for optimized distance calculations)
- matplotlib >= 3.5.0 (optional, for visualization)

### Platform Requirements
- Platform Base >= 2.0.0
- Python >= 3.8
- Plugin API version 1.0.0

## Usage

### Basic DTW Computation

```python
from platform_base.core.registry import PluginRegistry

# Load plugin through registry
registry = PluginRegistry()
dtw_plugin = registry.get("dtw_plugin")

# Configure DTW parameters
from dtw_plugin.plugin import DTWConfig
config = DTWConfig(
    window_size=50,  # Sakoe-Chiba band constraint
    distance_metric='euclidean',
    normalize_distance=True,
    return_path=True
)

# Compute DTW distance
result = dtw_plugin.compute_dtw_distance(series1, series2, config)
print(f"DTW Distance: {result.distance}")
print(f"Normalized Distance: {result.normalized_distance}")
```

### Batch Processing

```python
# Compute pairwise distances for multiple series
series_list = [series1, series2, series3, series4]
distance_matrix = dtw_plugin.compute_dtw_batch(series_list, config)
```

### Visualization

```python
# Visualize DTW alignment
fig = dtw_plugin.visualize_dtw_alignment(series1, series2, result)
plt.show()
```

### Configuration Options

The `DTWConfig` class provides comprehensive configuration:

```python
config = DTWConfig(
    window_size=None,           # Constraint window (None = unconstrained)
    distance_metric='euclidean', # 'euclidean', 'manhattan', 'cosine'
    normalize_distance=True,     # Normalize by path length
    return_path=True,           # Return optimal warping path
    return_cost_matrix=False,   # Return full cost matrix
    step_pattern='symmetric'    # 'symmetric' or 'asymmetric'
)
```

## Performance Considerations

### Computational Complexity
- **Unconstrained DTW**: O(nm) time and space complexity
- **Constrained DTW**: O(nw) where w is the window size
- **Batch Processing**: Optimized for multiple series comparisons

### Memory Usage
- Configurable memory limits (default: 500MB)
- Efficient cost matrix computation
- Intelligent caching with LRU eviction
- Optional cost matrix return for memory savings

### Optimization Features
- **Caching**: Results cached for identical inputs
- **Early Termination**: Distance threshold stopping
- **Window Constraints**: Sakoe-Chiba band for large series
- **Vectorized Operations**: NumPy/SciPy optimizations

## Applications

### Time Series Analysis
- Signal alignment and synchronization
- Pattern matching and recognition
- Anomaly detection in temporal data
- Clustering of time series data

### Signal Processing
- Audio signal alignment
- Speech recognition preprocessing  
- Biomedical signal analysis
- Sensor data correlation

### Machine Learning
- Feature extraction for temporal data
- Similarity-based classification
- Prototype-based clustering
- Temporal data augmentation

## Algorithm Details

### DTW Recurrence Relation

The DTW distance is computed using dynamic programming with the recurrence:

```
DTW(i,j) = d(xi, yj) + min(
    DTW(i-1, j),     # insertion
    DTW(i, j-1),     # deletion  
    DTW(i-1, j-1)    # match
)
```

### Constraints and Optimizations

1. **Sakoe-Chiba Band**: Limits warping to diagonal band of width 2w+1
2. **Step Patterns**: Control allowed transitions in warping path
3. **Distance Metrics**: Multiple point-to-point distance functions
4. **Normalization**: Path length normalization for fair comparison

## Error Handling

The plugin includes comprehensive error handling:

- **Input Validation**: Series length and format checking
- **Memory Limits**: Graceful handling of memory constraints
- **Timeout Protection**: Execution time limits
- **Resource Monitoring**: CPU and memory usage tracking

## Security Features

- **Sandbox Isolation**: Moderate security level with controlled access
- **Module Restrictions**: Limited import capabilities
- **Resource Limits**: CPU and memory constraints
- **Execution Monitoring**: Real-time performance tracking

## Development

### Plugin Structure
```
dtw_plugin/
├── manifest.json       # Plugin metadata and configuration
├── plugin.py          # Main plugin implementation
└── README.md          # Documentation (this file)
```

### Testing
```python
python plugin.py  # Run example usage and tests
```

### Extending the Plugin
The plugin can be extended with additional features:
- Custom distance metrics
- Advanced constraint patterns  
- Multi-dimensional DTW
- Approximate DTW algorithms

## Troubleshooting

### Common Issues

**Import Errors**: Ensure all dependencies are installed
```bash
pip install numpy scipy matplotlib
```

**Memory Issues**: Reduce window size or disable cost matrix return
```python
config = DTWConfig(window_size=20, return_cost_matrix=False)
```

**Performance Issues**: Enable constraints for large series
```python
config = DTWConfig(window_size=50)  # Limit warping flexibility
```

### Debug Information

Enable debug logging to monitor plugin behavior:
```python
stats = dtw_plugin.get_statistics()
print(f"Execution count: {stats['execution_count']}")
print(f"Average time: {stats['average_execution_time']:.4f}s")
```

## License

This plugin is distributed under the MIT License. See the manifest.json file for complete license information.

## Contributing

Contributions are welcome! Please ensure all changes maintain compatibility with the Platform Base plugin API v1.0.0.

## Support

For issues and questions:
1. Check this documentation
2. Review plugin logs for error messages  
3. Verify dependency installations
4. Test with smaller datasets to isolate issues

## Version History

- **v1.0.0**: Initial release with core DTW functionality
  - Standard and constrained DTW
  - Multiple distance metrics
  - Batch processing capabilities
  - Visualization support
  - Comprehensive caching system