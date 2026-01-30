#!/usr/bin/env python3
"""
Test script to verify legend and color bugs
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set QT platform for headless execution
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_colors_and_legend():
    """Test that series have different colors and legend appears"""
    print("=== Testing Bug 1: Series Colors & Bug 2: Legend ===\n")
    
    try:
        from platform_base.viz.figures_2d import Plot2DWidget, TimeseriesPlot
        from platform_base.viz.config import get_default_config
        from platform_base.core.models import Dataset, Series, SeriesID, SeriesMetadata, SourceInfo, DatasetMetadata
        import numpy as np
        from pint import Unit
        from datetime import datetime
        from PyQt6.QtWidgets import QApplication
        
        # Create app
        app = QApplication([])
        
        # Create config
        config = get_default_config()
        print(f"Default color palette: {config.colors.primary_colors}\n")
        
        # Create Plot2DWidget
        widget = Plot2DWidget(config)
        print(f"✓ Plot2DWidget created")
        
        # Check if legend exists initially
        plot_item = widget.plot_widget.getPlotItem()
        initial_legend = plot_item.legend
        print(f"  Initial legend: {initial_legend}")
        
        # Add multiple series with different colors
        t = np.linspace(0, 10, 100)
        series_data = [
            ("Series 1", np.sin(t)),
            ("Series 2", np.cos(t)),
            ("Series 3", np.sin(t * 2)),
        ]
        
        print("\nAdding series:")
        for i, (name, values) in enumerate(series_data):
            widget.add_series(
                series_id=name,
                x_data=t,
                y_data=values,
                series_index=i
            )
            
            # Check color assignment
            stored_color = widget._series_data[name]['color']
            expected_color = config.get_color_for_series(i)
            
            if stored_color == expected_color:
                print(f"  ✓ {name}: color={stored_color} (correct)")
            else:
                print(f"  ✗ {name}: color={stored_color}, expected={expected_color} (WRONG)")
        
        # Check legend after adding series
        final_legend = plot_item.legend
        print(f"\nFinal legend: {final_legend}")
        
        if final_legend is None:
            print("✗ BUG CONFIRMED: Legend is None (not visible)")
            return False
        else:
            print(f"✓ Legend exists")
            if hasattr(final_legend, 'items'):
                print(f"  Legend has {len(final_legend.items)} items")
                if len(final_legend.items) == len(series_data):
                    print("  ✓ All series in legend")
                else:
                    print(f"  ✗ Expected {len(series_data)} items, got {len(final_legend.items)}")
        
        # Check that colors are different
        colors_used = [widget._series_data[name]['color'] for name, _ in series_data]
        unique_colors = set(colors_used)
        
        print(f"\nColor uniqueness check:")
        print(f"  Colors used: {colors_used}")
        print(f"  Unique colors: {len(unique_colors)}/{len(colors_used)}")
        
        if len(unique_colors) == len(colors_used):
            print("  ✓ All series have different colors")
        else:
            print("  ✗ BUG CONFIRMED: Some series have the same color")
            return False
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_colors_and_legend()
    sys.exit(0 if success else 1)
