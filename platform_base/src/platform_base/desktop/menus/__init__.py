"""
Context Menu System for Platform Base v2.0

Provides rich context menus for various UI components
with analysis tools and data manipulation options.
"""

from .plot_context_menu import (
    PlotContextMenu,
    MathAnalysisDialog,
    create_plot_context_menu,
)

__all__ = [
    "PlotContextMenu",
    "MathAnalysisDialog", 
    "create_plot_context_menu",
]