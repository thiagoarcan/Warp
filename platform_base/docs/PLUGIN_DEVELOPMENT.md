# Platform Base v2.0 - Plugin Development Guide

**Complete guide for developing custom plugins**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Plugin Architecture](#plugin-architecture)
3. [Quick Start](#quick-start)
4. [Plugin Types](#plugin-types)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Testing Plugins](#testing-plugins)
8. [Distribution](#distribution)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

Platform Base supports a plugin system that allows you to extend functionality without modifying core code. Plugins can:

- Add custom data processing operations
- Create new visualization types
- Implement custom file format loaders
- Add UI panels and dialogs
- Integrate external tools and services

### Plugin System Features

- ✅ **Hot reloading** - Load plugins without restart
- ✅ **Isolation** - Plugins run in separate process (optional)
- ✅ **Type safety** - Full type hints and validation
- ✅ **Auto-discovery** - Automatic plugin detection
- ✅ **Error handling** - Graceful failure without crashing app
- ✅ **Metadata** - Version info, dependencies, descriptions

---

## Plugin Architecture

### Plugin Structure

```
my_plugin/
├── __init__.py           # Plugin entry point
├── plugin.yaml           # Plugin metadata
├── operations.py         # Custom operations
├── ui.py                 # UI components (optional)
├── tests/               # Unit tests (optional)
│   └── test_operations.py
└── README.md            # Documentation
```

### Plugin Lifecycle

```
1. Discovery → 2. Validation → 3. Loading → 4. Registration → 5. Execution
```

### Plugin Registry

Plugins register with the central `PluginRegistry`:

```python
from platform_base.plugins.registry import PluginRegistry

registry = PluginRegistry()
registry.register_plugin(MyPlugin)
```

---

## Quick Start

### Create Your First Plugin (5 minutes)

#### Step 1: Create Plugin Directory

```bash
mkdir my_first_plugin
cd my_first_plugin
```

#### Step 2: Create plugin.yaml

```yaml
name: my_first_plugin
version: 1.0.0
author: Your Name
description: My first Platform Base plugin
type: operation
entry_point: my_first_plugin:MyPlugin

dependencies:
  - numpy>=1.24.0
  - scipy>=1.10.0

platform_base_version: ">=2.0.0"
```

#### Step 3: Create __init__.py

```python
"""My First Plugin - Simple data smoothing."""

from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series
import numpy as np


class MyPlugin(OperationPlugin):
    """Simple data smoothing plugin."""
    
    name = "Simple Smooth"
    description = "Smooth data using moving average"
    category = "Filters"
    
    def get_parameters(self):
        """Define plugin parameters."""
        return {
            "window_size": {
                "type": "int",
                "default": 5,
                "min": 3,
                "max": 100,
                "description": "Moving average window size"
            }
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        """Execute plugin operation."""
        window = params["window_size"]
        
        # Calculate moving average
        smoothed = np.convolve(
            series.values,
            np.ones(window) / window,
            mode='same'
        )
        
        # Return new series
        return Series(
            series_id=f"{series.series_id}_smoothed",
            name=f"{series.name} (Smoothed)",
            values=smoothed,
            unit=series.unit
        )


# Export plugin class
__plugin__ = MyPlugin
```

#### Step 4: Install Plugin

```bash
# From Platform Base root
python -m platform_base.plugins install /path/to/my_first_plugin
```

#### Step 5: Use Plugin

1. Launch Platform Base
2. Load data
3. Select series
4. Operations → Filters → Simple Smooth
5. Set window size → Apply

**Congratulations!** You've created your first plugin!

---

## Plugin Types

### 1. Operation Plugins

Process data and return results.

**Base Class**: `OperationPlugin`

**Example**: Derivative, Integral, Custom Filter

```python
from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series

class DerivativePlugin(OperationPlugin):
    name = "Custom Derivative"
    category = "Calculus"
    
    def get_parameters(self):
        return {
            "order": {"type": "int", "default": 1}
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        # Implementation
        pass
```

### 2. Visualization Plugins

Create custom plot types.

**Base Class**: `VisualizationPlugin`

**Example**: Custom 3D plot, Heatmap, Waterfall

```python
from platform_base.plugins.base import VisualizationPlugin

class HeatmapPlugin(VisualizationPlugin):
    name = "Custom Heatmap"
    category = "2D Plots"
    
    def create_plot(self, data, params):
        # Create matplotlib/plotly figure
        pass
```

### 3. Loader Plugins

Support custom file formats.

**Base Class**: `LoaderPlugin`

**Example**: Custom binary format, Database connection

```python
from platform_base.plugins.base import LoaderPlugin
from platform_base.core.models import Dataset

class CustomFormatLoader(LoaderPlugin):
    name = "Custom Format"
    extensions = [".myformat"]
    
    def load(self, filepath: str) -> Dataset:
        # Parse file and return Dataset
        pass
```

### 4. Export Plugins

Export data in custom formats.

**Base Class**: `ExportPlugin`

**Example**: Custom report format, API upload

```python
from platform_base.plugins.base import ExportPlugin

class CustomExporter(ExportPlugin):
    name = "Custom Export"
    extensions = [".custom"]
    
    def export(self, dataset, filepath: str):
        # Write data to file
        pass
```

### 5. UI Plugins

Add custom panels and dialogs.

**Base Class**: `UIPlugin`

**Example**: Statistics panel, Data quality dashboard

```python
from platform_base.plugins.base import UIPlugin
from PyQt6.QtWidgets import QWidget

class StatsPanelPlugin(UIPlugin):
    name = "Statistics Panel"
    location = "right"
    
    def create_widget(self) -> QWidget:
        # Create and return Qt widget
        pass
```

---

## API Reference

### Plugin Base Classes

#### OperationPlugin

```python
class OperationPlugin:
    """Base class for data operations."""
    
    name: str                    # Display name
    description: str             # Short description
    category: str                # Category for menu
    
    def get_parameters(self) -> dict:
        """Return parameter definitions."""
        pass
    
    def validate_input(self, series: Series) -> bool:
        """Validate input data (optional)."""
        return True
    
    def execute(self, series: Series, params: dict) -> Series:
        """Execute operation and return result."""
        pass
    
    def get_preview(self, series: Series, params: dict) -> Series:
        """Return preview result (optional)."""
        return self.execute(series, params)
```

#### Parameter Types

```python
# Integer parameter
{
    "param_name": {
        "type": "int",
        "default": 10,
        "min": 1,
        "max": 100,
        "description": "Parameter description"
    }
}

# Float parameter
{
    "frequency": {
        "type": "float",
        "default": 1.0,
        "min": 0.1,
        "max": 100.0,
        "step": 0.1,
        "description": "Cutoff frequency (Hz)"
    }
}

# Choice parameter
{
    "method": {
        "type": "choice",
        "options": ["linear", "cubic", "quintic"],
        "default": "cubic",
        "description": "Interpolation method"
    }
}

# Boolean parameter
{
    "normalize": {
        "type": "bool",
        "default": False,
        "description": "Normalize output"
    }
}
```

### Core Models

#### Series

```python
from platform_base.core.models import Series

series = Series(
    series_id="unique_id",
    name="Display Name",
    values=np.array([1, 2, 3]),
    unit="m/s",
    metadata={"sensor": "IMU-001"}
)

# Properties
series.values       # numpy array
series.name         # str
series.unit         # str
series.metadata     # dict
```

#### Dataset

```python
from platform_base.core.models import Dataset, Series

dataset = Dataset(
    dataset_id="ds_001",
    name="Dataset Name",
    series={"s1": series1, "s2": series2},
    t_seconds=np.array([0, 0.1, 0.2]),
    metadata={"source": "file.csv"}
)

# Properties
dataset.series      # dict[str, Series]
dataset.t_seconds   # numpy array
dataset.metadata    # dict
```

---

## Examples

### Example 1: FFT Plugin

```python
"""FFT Analysis Plugin."""

from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series
import numpy as np
from scipy import fft


class FFTPlugin(OperationPlugin):
    """Compute Fast Fourier Transform."""
    
    name = "FFT Analysis"
    description = "Compute frequency spectrum"
    category = "Signal Processing"
    
    def get_parameters(self):
        return {
            "window": {
                "type": "choice",
                "options": ["hann", "hamming", "blackman", "none"],
                "default": "hann",
                "description": "Window function"
            },
            "normalize": {
                "type": "bool",
                "default": True,
                "description": "Normalize amplitudes"
            }
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        """Compute FFT."""
        # Get parameters
        window_type = params["window"]
        normalize = params["normalize"]
        
        # Apply window
        if window_type != "none":
            window = getattr(np, window_type)(len(series.values))
            windowed = series.values * window
        else:
            windowed = series.values
        
        # Compute FFT
        spectrum = fft.rfft(windowed)
        amplitudes = np.abs(spectrum)
        
        # Normalize if requested
        if normalize:
            amplitudes = amplitudes / np.max(amplitudes)
        
        # Create result series
        return Series(
            series_id=f"{series.series_id}_fft",
            name=f"{series.name} (FFT)",
            values=amplitudes,
            unit="normalized" if normalize else series.unit
        )
```

### Example 2: Peak Detection Plugin

```python
"""Peak Detection Plugin."""

from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series
from scipy.signal import find_peaks
import numpy as np


class PeakDetectionPlugin(OperationPlugin):
    """Detect peaks in signal."""
    
    name = "Peak Detection"
    category = "Analysis"
    
    def get_parameters(self):
        return {
            "height": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "description": "Minimum peak height"
            },
            "distance": {
                "type": "int",
                "default": 10,
                "min": 1,
                "description": "Minimum distance between peaks"
            },
            "prominence": {
                "type": "float",
                "default": 0.1,
                "min": 0.0,
                "description": "Minimum peak prominence"
            }
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        """Find peaks."""
        # Find peaks
        peaks, properties = find_peaks(
            series.values,
            height=params["height"],
            distance=params["distance"],
            prominence=params["prominence"]
        )
        
        # Create boolean array marking peaks
        peak_markers = np.zeros_like(series.values)
        peak_markers[peaks] = 1.0
        
        return Series(
            series_id=f"{series.series_id}_peaks",
            name=f"{series.name} (Peaks)",
            values=peak_markers,
            metadata={
                "peak_count": len(peaks),
                "peak_indices": peaks.tolist(),
                "peak_heights": properties["peak_heights"].tolist()
            }
        )
```

### Example 3: Custom Loader Plugin

```python
"""Custom Binary Format Loader."""

from platform_base.plugins.base import LoaderPlugin
from platform_base.core.models import Dataset, Series
import struct
import numpy as np


class BinaryLoader(LoaderPlugin):
    """Load custom binary format."""
    
    name = "Custom Binary"
    extensions = [".bin", ".dat"]
    
    def load(self, filepath: str) -> Dataset:
        """Load binary file."""
        with open(filepath, "rb") as f:
            # Read header
            version = struct.unpack("I", f.read(4))[0]
            n_points = struct.unpack("I", f.read(4))[0]
            n_series = struct.unpack("I", f.read(4))[0]
            
            # Read time array
            time_data = f.read(n_points * 8)  # 8 bytes per double
            t_seconds = np.frombuffer(time_data, dtype=np.float64)
            
            # Read series
            series_dict = {}
            for i in range(n_series):
                # Read series name
                name_len = struct.unpack("H", f.read(2))[0]
                name = f.read(name_len).decode("utf-8")
                
                # Read values
                values_data = f.read(n_points * 8)
                values = np.frombuffer(values_data, dtype=np.float64)
                
                # Create series
                series_dict[f"series_{i}"] = Series(
                    series_id=f"series_{i}",
                    name=name,
                    values=values
                )
            
            # Create dataset
            return Dataset(
                dataset_id=filepath,
                name=filepath,
                series=series_dict,
                t_seconds=t_seconds,
                metadata={"version": version}
            )
```

---

## Testing Plugins

### Unit Tests

Create `tests/test_myplugin.py`:

```python
"""Tests for MyPlugin."""

import pytest
import numpy as np
from platform_base.core.models import Series
from my_plugin import MyPlugin


@pytest.fixture
def sample_series():
    """Create test series."""
    t = np.linspace(0, 10, 100)
    y = np.sin(t)
    return Series(
        series_id="test",
        name="Test",
        values=y
    )


def test_plugin_creation():
    """Test plugin can be instantiated."""
    plugin = MyPlugin()
    assert plugin.name == "My Plugin"


def test_plugin_parameters():
    """Test parameter definition."""
    plugin = MyPlugin()
    params = plugin.get_parameters()
    
    assert "window_size" in params
    assert params["window_size"]["type"] == "int"


def test_plugin_execution(sample_series):
    """Test plugin execution."""
    plugin = MyPlugin()
    params = {"window_size": 5}
    
    result = plugin.execute(sample_series, params)
    
    assert result is not None
    assert len(result.values) == len(sample_series.values)
    assert result.series_id != sample_series.series_id


def test_plugin_validation(sample_series):
    """Test input validation."""
    plugin = MyPlugin()
    
    # Valid input
    assert plugin.validate_input(sample_series)
    
    # Invalid input (empty series)
    empty_series = Series("empty", "Empty", np.array([]))
    assert not plugin.validate_input(empty_series)
```

### Run Tests

```bash
pytest tests/
```

---

## Distribution

### Package Plugin

```bash
# Create distribution package
python setup.py sdist bdist_wheel
```

### setup.py Example

```python
from setuptools import setup, find_packages

setup(
    name="platform-base-myplugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "platform-base>=2.0.0",
        "numpy>=1.24.0"
    ],
    entry_points={
        "platform_base.plugins": [
            "myplugin=my_plugin:MyPlugin"
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="My Platform Base plugin",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/myplugin",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)
```

### Publish to PyPI

```bash
twine upload dist/*
```

### Install from PyPI

```bash
pip install platform-base-myplugin
```

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def execute(self, series: Series, params: dict) -> Series:
    try:
        # Your code
        result = process_data(series.values)
        return Series(...)
    except ValueError as e:
        raise PluginExecutionError(f"Invalid input: {e}")
    except Exception as e:
        raise PluginExecutionError(f"Unexpected error: {e}")
```

### 2. Input Validation

Validate inputs before processing:

```python
def validate_input(self, series: Series) -> bool:
    if len(series.values) < 10:
        raise ValidationError("Series too short (min 10 points)")
    
    if np.any(np.isnan(series.values)):
        raise ValidationError("Series contains NaN values")
    
    return True
```

### 3. Documentation

Provide clear docstrings:

```python
class MyPlugin(OperationPlugin):
    """
    One-line summary.
    
    Longer description explaining what the plugin does,
    algorithm used, and any important notes.
    
    Parameters:
        window_size: Size of moving average window
        
    Returns:
        Smoothed series with same length as input
        
    Example:
        >>> plugin = MyPlugin()
        >>> result = plugin.execute(series, {"window_size": 5})
    """
```

### 4. Performance

Optimize for large datasets:

```python
# Use NumPy operations (fast)
result = np.mean(data)

# Avoid Python loops (slow)
result = sum(data) / len(data)

# Use numba for custom loops
from numba import jit

@jit(nopython=True)
def custom_operation(data):
    # Fast loop
    pass
```

### 5. Type Hints

Use type hints for better IDE support:

```python
from typing import Dict, Any
from platform_base.core.models import Series

def execute(self, series: Series, params: Dict[str, Any]) -> Series:
    pass
```

---

## Troubleshooting

### Plugin Not Loading

**Problem**: Plugin not appearing in menu

**Solutions**:
1. Check `plugin.yaml` syntax
2. Verify entry point is correct
3. Check logs: `~/.platform_base/logs/plugins.log`
4. Ensure dependencies installed
5. Check Platform Base version compatibility

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solutions**:
1. Install plugin dependencies
2. Check Python path
3. Reinstall plugin

### Runtime Errors

**Problem**: Plugin crashes during execution

**Solutions**:
1. Add try/except blocks
2. Validate inputs
3. Check for NaN/Inf values
4. Test with sample data first
5. Enable debug logging

### Performance Issues

**Problem**: Plugin is slow

**Solutions**:
1. Profile code: `python -m cProfile`
2. Use NumPy operations
3. Consider numba JIT compilation
4. Reduce data copying
5. Process in chunks for large data

---

## Resources

### Documentation
- [API Reference](API_REFERENCE.md)
- [User Guide](USER_GUIDE.md)
- [Core Models](../src/platform_base/core/models.py)

### Examples
- [Example Plugins](../plugins/examples/)
- [Community Plugins](https://github.com/platform-base/plugins)

### Support
- [GitHub Issues](https://github.com/thiagoarcan/Warp/issues)
- [Discussions](https://github.com/thiagoarcan/Warp/discussions)

---

*Platform Base v2.0 - Plugin Development Guide*  
*Last Updated: 2026-02-02*
