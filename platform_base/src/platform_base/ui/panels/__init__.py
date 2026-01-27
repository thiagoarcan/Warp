"""UI Panels package

Exports:
- VizPanel: Painel de visualização com suporte a drag-and-drop
- OperationsPanel: Painel de operações em séries temporais  
- FileUploadDialog: Diálogo de upload de arquivos
- Performance: Otimização para grandes volumes de dados
- ResultsPanel: Painel de estatísticas e resultados
- StreamingPanel: Controle de playback/streaming
- ConfigPanel: Configurações da aplicação
"""

from platform_base.ui.panels.config_panel import ColorButton, ConfigPanel
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
    # Performance module
    "DecimationMethod",
    "PerformanceConfig",
    "DataDecimator",
    "LODManager",
    "StreamingDataManager",
    "PerformanceRenderer",
    "get_performance_renderer",
    "decimate_for_plot",
    # Results panel
    "ResultsPanel",
    "StatisticsResult",
    "StatCard",
    "StatisticsTable",
    # Streaming panel
    "StreamingPanel",
    "PlaybackState",
    "PlaybackMode",
    "TimelineSlider",
    "MinimapWidget",
    # Config panel
    "ConfigPanel",
    "ColorButton",
]