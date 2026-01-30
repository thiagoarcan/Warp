#!/usr/bin/env python3
"""
Demo app to visually demonstrate Bug #1 and Bug #2 fixes
Shows multiple series with different colors and a visible legend
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Create a demo visualization showing the fixes"""
    from platform_base.viz.figures_2d import Plot2DWidget
    from platform_base.viz.config import get_default_config
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
    from PyQt6.QtCore import Qt
    import numpy as np
    
    print("=" * 60)
    print("Demo: Bug Fixes for Series Colors and Legend")
    print("=" * 60)
    print("\nBug #1 Fix: Series now have unique colors")
    print("Bug #2 Fix: Legend is now visible and shows all series")
    print()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Platform Base - Bug Fixes Demo")
    window.resize(1200, 800)
    
    # Create central widget with layout
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Add title label
    title = QLabel("✓ Bug #1 & #2 Fixed: Unique Series Colors + Visible Legend")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 10px;")
    layout.addWidget(title)
    
    # Create config and widget
    config = get_default_config()
    viz_widget = Plot2DWidget(config)
    layout.addWidget(viz_widget)
    
    # Add info label
    info_text = (
        "Legend shows all series (upper-left corner) • "
        "Each series has a unique color from the palette • "
        "Colors cycle through the 10-color palette"
    )
    info = QLabel(info_text)
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info.setStyleSheet("font-size: 10pt; padding: 5px; color: #666;")
    layout.addWidget(info)
    
    window.setCentralWidget(central_widget)
    
    # Generate test data with multiple series
    t = np.linspace(0, 10, 500)
    
    test_series = [
        ("Temperature Sensor A", np.sin(t) + 20, 0),
        ("Pressure Sensor B", 100 * np.cos(t * 1.5) + 1000, 1),
        ("Flow Rate C", 50 * np.sin(t * 0.8) + 200, 2),
        ("Voltage D", 5 * np.cos(t * 2) + 12, 3),
        ("Current E", 2 * np.sin(t * 1.2) + 10, 4),
    ]
    
    print("Adding series to plot:")
    for name, values, idx in test_series:
        viz_widget.add_series(
            series_id=name,
            x_data=t,
            y_data=values,
            series_index=idx
        )
        color = config.get_color_for_series(idx)
        print(f"  • {name}: color={color}")
    
    print(f"\n✓ Added {len(test_series)} series with unique colors")
    print("✓ Legend is visible in the plot")
    print("\nShowing window... Close to exit.")
    
    # Auto-range to show all data
    viz_widget.auto_range()
    
    # Show window
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
