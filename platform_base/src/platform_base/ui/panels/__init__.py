"""UI Panels package.

Exports:
- VizPanel: visualization panel with drag-and-drop support
- OperationsPanel: time-series operations panel
- Performance: optimization for large data volumes
- ResultsPanel: statistics/results panel
- StreamingPanel: playback/streaming controls
- ConfigPanel: application settings panel
"""

from platform_base.ui.panels.config_panel import ColorButton, ConfigPanel
from platform_base.ui.panels.data_panel import DataPanel
from platform_base.ui.panels.viz_panel import VizPanel
from platform_base.ui.panels.performance import (
    DataDecimator,
    DecimationMethod,
    LODManager,
    PerformanceConfig,
    PerformanceRenderer,
    StreamingDataManager,
    decimate_for_plot,
    get_performance_renderer,
)
from platform_base.ui.panels.results_panel import (
    ResultsPanel,
    StatCard,
    StatisticsResult,
    StatisticsTable,
)
from platform_base.ui.panels.streaming_panel import (
    MinimapWidget,
    PlaybackMode,
    PlaybackState,
    StreamingPanel,
    TimelineSlider,
)


__all__ = [
    "ColorButton",
    "ConfigPanel",
    "DataPanel",
    "DataDecimator",
    "DecimationMethod",
    "LODManager",
    "MinimapWidget",
    "PerformanceConfig",
    "PerformanceRenderer",
    "PlaybackMode",
    "PlaybackState",
    "ResultsPanel",
    "StatCard",
    "StatisticsResult",
    "StatisticsTable",
    "StreamingDataManager",
    "StreamingPanel",
    "TimelineSlider",
    "VizPanel",
    "decimate_for_plot",
    "get_performance_renderer",
]
