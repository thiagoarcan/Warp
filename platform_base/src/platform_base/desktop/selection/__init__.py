"""
Advanced Selection System for Platform Base v2.0

Provides temporal, graphical and conditional selection capabilities
for time series data visualization and analysis.
"""

from .selection_manager import (
    ConditionalSelection,
    GraphicalSelection,
    SelectionCriteria,
    SelectionManager,
    SelectionMode,
    SelectionState,
    SelectionType,
    TemporalSelection,
)
from .selection_widgets import (
    ConditionalSelectionDialog,
    SelectionStatisticsPanel,
    SelectionToolbar,
)


__all__ = [
    "ConditionalSelection",
    "ConditionalSelectionDialog",
    "GraphicalSelection",
    "SelectionCriteria",
    "SelectionManager",
    "SelectionMode",
    "SelectionState",
    "SelectionStatisticsPanel",
    "SelectionToolbar",
    "SelectionType",
    "TemporalSelection",
]
