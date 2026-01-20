#!/usr/bin/env python3
"""
Teste simples do sistema de visualização 2D
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set environment for Windows console encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_viz_config():
    """Testa sistema de configuração VizConfig"""
    print("=== Testing VizConfig ===")
    
    try:
        from platform_base.viz.config import VizConfig, get_default_config, get_dark_config
        
        # Test default config
        config = get_default_config()
        print(f"[OK] Default config created: {config.theme}")
        print(f"  Colors: {len(config.colors.primary_colors)} primary colors")
        print(f"  Performance: max_points_2d={config.performance.max_points_2d}")
        
        # Test dark theme
        dark_config = get_dark_config()
        print(f"[OK] Dark config created: {dark_config.theme}")
        print(f"  Background: {dark_config.colors.background_color}")
        
        # Test color cycle
        colors = config.colors.get_color_cycle(5)
        print(f"[OK] Color cycle for 5 series: {colors}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] VizConfig test failed: {e}")
        return False

def test_plot2d_import():
    """Testa importação do sistema Plot2D"""
    print("\n=== Testing Plot2D Import ===")
    
    try:
        from platform_base.viz.figures_2d import Plot2DWidget, TimeseriesPlot, ScatterPlot
        print("[OK] Plot2D classes imported successfully")
        
        # Test if pyqtgraph is available
        try:
            import pyqtgraph as pg
            print("[OK] PyQtGraph is available")
            return True
        except ImportError:
            print("! PyQtGraph not available - Plot2D will have limited functionality")
            return False
            
    except Exception as e:
        print(f"[ERROR] Plot2D import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_figure():
    """Testa classe base BaseFigure"""
    print("\n=== Testing BaseFigure ===")
    
    try:
        from platform_base.viz.base import BaseFigure, _downsample_lttb
        from platform_base.viz.config import VizConfig
        
        # Test LTTB downsampling
        import numpy as np
        
        # Generate test data
        t = np.linspace(0, 100, 10000)
        values = np.sin(t) + 0.1 * np.random.randn(len(t))
        
        # Test downsampling
        t_down, v_down = _downsample_lttb(t, values, 1000)
        print(f"[OK] LTTB downsampling: {len(t)} -> {len(t_down)} points")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] BaseFigure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dataset_integration():
    """Testa integração com Dataset"""
    print("\n=== Testing Dataset Integration ===")
    
    try:
        from platform_base.core.models import Dataset, Series, SeriesID, SeriesMetadata, SourceInfo, DatasetMetadata
        from platform_base.viz.figures_2d import TimeseriesPlot
        from platform_base.viz.config import get_default_config
        import numpy as np
        from pint import Unit
        from datetime import datetime
        
        # Create test dataset
        n_points = 1000
        t_seconds = np.linspace(0, 100, n_points)
        t_datetime = np.arange('2023-01-01T00:00:00', '2023-01-01T01:40:00', dtype='datetime64[s]')[:n_points]
        
        # Create proper metadata
        series1_metadata = SeriesMetadata(
            original_name="Temperature",
            source_column="temp_col",
            description="Temperature sensor data"
        )
        
        series2_metadata = SeriesMetadata(
            original_name="Pressure", 
            source_column="press_col",
            description="Pressure sensor data"
        )
        
        # Create test series with proper units
        series1 = Series(
            series_id=SeriesID("test_series_1"),
            name="Temperature",
            unit=Unit("celsius"),
            values=20 + 5 * np.sin(t_seconds * 0.1) + np.random.randn(n_points) * 0.5,
            metadata=series1_metadata
        )
        
        series2 = Series(
            series_id=SeriesID("test_series_2"), 
            name="Pressure",
            unit=Unit("bar"),
            values=1000 + 100 * np.cos(t_seconds * 0.15) + np.random.randn(n_points) * 10,
            metadata=series2_metadata
        )
        
        # Create required metadata and source info
        source_info = SourceInfo(
            filepath="/tmp/test_data.csv",
            filename="test_data.csv", 
            format="csv",
            size_bytes=1024,
            checksum="test_checksum"
        )
        
        dataset_metadata = DatasetMetadata(
            description="Test dataset for visualization testing"
        )
        
        # Create dataset
        dataset = Dataset(
            dataset_id="test_dataset",
            version=1,
            parent_id=None,
            source=source_info,
            t_seconds=t_seconds,
            t_datetime=t_datetime,
            series={
                "temp": series1,
                "press": series2
            },
            metadata=dataset_metadata,
            created_at=datetime.now()
        )
        
        print(f"[OK] Test dataset created: {len(dataset.series)} series, {len(dataset.t_seconds)} points")
        
        # Create plot (without actually showing UI)
        config = get_default_config()
        plot = TimeseriesPlot(config)
        
        print("[OK] TimeseriesPlot instance created")
        print("[OK] Dataset integration test passed")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Dataset integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all visualization tests"""
    print("Testing Platform Base v2.0 - Visualization System")
    print("=" * 60)
    
    tests = [
        test_viz_config,
        test_plot2d_import, 
        test_base_figure,
        test_dataset_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[CRASH] Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] All visualization tests PASSED!")
    else:
        print("[WARNING] Some tests failed - check output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)