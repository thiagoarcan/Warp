"""
Figures 2D - Sistema de visualização 2D com pyqtgraph conforme seção 10.3

Features:
- Gráficos de linha e scatter com pyqtgraph
- Brush selection interativa
- Performance otimizada para milhões de pontos
- Suporte a múltiplas séries
- Downsampling LTTB inteligente
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np


try:
    import pyqtgraph as pg
    from PyQt6.QtCore import QObject, Qt, pyqtSignal
    from PyQt6.QtGui import QBrush, QColor, QPen
    from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False

from platform_base.utils.logging import get_logger
from platform_base.viz.base import BaseFigure, _downsample_lttb


if TYPE_CHECKING:
    from platform_base.core.models import Dataset, Series
    from platform_base.viz.config import VizConfig


logger = get_logger(__name__)


if not PYQTGRAPH_AVAILABLE:
    logger.error("pyqtgraph_not_available", message="PyQtGraph not available for 2D visualization")


def _hex_to_qcolor(hex_color: str) -> QColor:
    """Converte cor hex para QColor"""
    hex_color = hex_color.lstrip("#")
    return QColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def _prepare_data_for_plotting(t: np.ndarray, values: np.ndarray, max_points: int = 100000) -> tuple[np.ndarray, np.ndarray]:
    """Prepara dados para plotagem com downsampling inteligente"""
    if len(t) <= max_points:
        return t, values

    # Usa LTTB para preservar features importantes
    try:
        t_down, values_down = _downsample_lttb(t, values, max_points)
        logger.debug("lttb_downsampling_applied",
                    original_points=len(t),
                    downsampled_points=len(t_down))
        return t_down, values_down
    except Exception as e:
        # Fallback para downsampling uniforme
        logger.warning("lttb_failed_fallback_uniform", error=str(e))
        idx = np.linspace(0, len(t) - 1, max_points).astype(int)
        return t[idx], values[idx]


class Plot2DWidget(QWidget):
    """
    Widget PyQtGraph para visualização 2D conforme seção 10.3

    Features:
    - Performance otimizada para milhões de pontos
    - Brush selection interativa
    - Múltiplas séries com cores configuráveis
    - Zoom e pan responsivos
    - Downsampling LTTB automático
    """

    # Signals
    selection_changed = pyqtSignal(np.ndarray)  # indices selecionados
    range_changed = pyqtSignal(tuple, tuple)    # x_range, y_range
    series_clicked = pyqtSignal(str)            # series_id

    def __init__(self, config: VizConfig, parent: QWidget | None = None):
        super().__init__(parent)

        if not PYQTGRAPH_AVAILABLE:
            raise ImportError("PyQtGraph not available")

        self.config = config
        self._series_data = {}  # {series_id: (x, y, plot_item)}
        self._selection_enabled = True
        self._brush_selection = None

        self._setup_ui()
        self._setup_connections()

        logger.debug("plot2d_widget_initialized")

    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create plot widget with configuration
        self.plot_widget = pg.PlotWidget(
            title="Time Series Plot",
            labels={"left": "Value", "bottom": "Time (s)"},
        )

        # Apply theme configuration
        self._apply_theme()

        # Enable OpenGL acceleration if configured
        if self.config.performance.use_opengl:
            self.plot_widget.useOpenGL(True)
            logger.debug("opengl_acceleration_enabled")

        # Configure plot widget
        self.plot_widget.setLabel("left", "Value")
        self.plot_widget.setLabel("bottom", "Time (s)")
        self.plot_widget.showGrid(
            x=self.config.style.grid_enabled,
            y=self.config.style.grid_enabled,
            alpha=self.config.style.grid_alpha,
        )

        # Enable anti-aliasing if configured
        if self.config.performance.antialias:
            self.plot_widget.setAntialiasing(True)

        # Add legend to plot (Bug Fix #2: Legend not appearing)
        plot_item = self.plot_widget.getPlotItem()
        plot_item.addLegend()
        logger.debug("legend_added_to_plot")

        layout.addWidget(self.plot_widget)

        # Selection region for brush selection
        if self.config.interaction.brush_selection:
            self._setup_brush_selection()

    def _setup_brush_selection(self):
        """Configura seleção por brush"""
        # Linear region for X-axis selection
        self._brush_selection = pg.LinearRegionItem()
        self._brush_selection.setZValue(10)
        self.plot_widget.addItem(self._brush_selection)

        # Initially hide selection
        self._brush_selection.setVisible(False)

        # Connect selection signals
        self._brush_selection.sigRegionChanged.connect(self._on_selection_changed)

        logger.debug("brush_selection_configured")

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Range change signals
        view_box = self.plot_widget.getViewBox()
        view_box.sigRangeChanged.connect(self._on_range_changed)

    def _apply_theme(self):
        """Aplica tema à visualização"""
        # Background color
        bg_color = _hex_to_qcolor(self.config.colors.background_color)
        self.plot_widget.setBackground(bg_color)

        # Grid color is handled in showGrid call

    def add_series(self, series_id: str, x_data: np.ndarray, y_data: np.ndarray,
                   series_index: int = 0, **plot_kwargs):
        """
        Adiciona série ao gráfico

        Args:
            series_id: Identificador da série
            x_data: Dados do eixo X (timestamps)
            y_data: Dados do eixo Y (valores)
            series_index: Índice para seleção de cor
            **plot_kwargs: Argumentos adicionais para plotagem
        """
        start_time = time.perf_counter()

        # Apply downsampling if needed
        x_plot, y_plot = self._apply_downsampling(x_data, y_data)

        # Get color for series
        color = self.config.get_color_for_series(series_index)
        qcolor = _hex_to_qcolor(color)

        # Configure pen and brush
        pen = QPen(qcolor)
        # Bug Fix #1: setWidth expects int, not float
        pen.setWidth(int(self.config.style.line_width))

        # Plot configuration
        plot_config = {
            "pen": pen,
            "symbol": "o",
            "symbolSize": self.config.style.marker_size,
            "symbolBrush": QBrush(qcolor),
            "name": series_id,
            "connect": "finite",  # Don't connect NaN gaps
            **plot_kwargs,
        }

        # Add plot item
        plot_item = self.plot_widget.plot(x_plot, y_plot, **plot_config)

        # Store series data
        self._series_data[series_id] = {
            "x_original": x_data,
            "y_original": y_data,
            "x_plot": x_plot,
            "y_plot": y_plot,
            "plot_item": plot_item,
            "color": color,
        }

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("series_added_to_plot",
                   series_id=series_id,
                   original_points=len(x_data),
                   plotted_points=len(x_plot),
                   duration_ms=duration_ms)

    def remove_series(self, series_id: str):
        """Remove série do gráfico"""
        if series_id in self._series_data:
            plot_item = self._series_data[series_id]["plot_item"]
            self.plot_widget.removeItem(plot_item)
            del self._series_data[series_id]

            logger.debug("series_removed_from_plot", series_id=series_id)

    def clear_series(self):
        """Remove todas as séries"""
        for series_id in list(self._series_data.keys()):
            self.remove_series(series_id)

    def update_series(self, series_id: str, x_data: np.ndarray, y_data: np.ndarray):
        """Atualiza dados de uma série existente"""
        if series_id in self._series_data:
            # Apply downsampling
            x_plot, y_plot = self._apply_downsampling(x_data, y_data)

            # Update plot data
            plot_item = self._series_data[series_id]["plot_item"]
            plot_item.setData(x_plot, y_plot)

            # Update stored data
            series_data = self._series_data[series_id]
            series_data["x_original"] = x_data
            series_data["y_original"] = y_data
            series_data["x_plot"] = x_plot
            series_data["y_plot"] = y_plot

            logger.debug("series_updated", series_id=series_id, points=len(x_plot))

    def enable_selection(self, enabled: bool = True):
        """Habilita/desabilita seleção por brush"""
        self._selection_enabled = enabled
        if self._brush_selection:
            self._brush_selection.setVisible(enabled)

    def get_selection_range(self) -> tuple[float, float] | None:
        """Retorna range selecionado (min, max) ou None"""
        if self._brush_selection and self._brush_selection.isVisible():
            return self._brush_selection.getRegion()
        return None

    def set_selection_range(self, x_min: float, x_max: float):
        """Define range de seleção"""
        if self._brush_selection:
            self._brush_selection.setRegion([x_min, x_max])
            self._brush_selection.setVisible(True)

    def clear_selection(self):
        """Limpa seleção atual"""
        if self._brush_selection:
            self._brush_selection.setVisible(False)

    def auto_range(self):
        """Auto-ajusta range para mostrar todos os dados"""
        self.plot_widget.autoRange()

    def set_range(self, x_range: tuple[float, float], y_range: tuple[float, float]):
        """Define ranges dos eixos"""
        self.plot_widget.setRange(xRange=x_range, yRange=y_range)

    def export_image(self, file_path: str, width: int = 1920, height: int = 1080):
        """Exporta gráfico como imagem"""
        try:
            # Set size temporarily
            original_size = self.plot_widget.size()
            self.plot_widget.resize(width, height)

            # Export image
            exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.parameters()["width"] = width
            exporter.parameters()["height"] = height
            exporter.export(file_path)

            # Restore original size
            self.plot_widget.resize(original_size)

            logger.info("plot_exported", file_path=file_path, width=width, height=height)

        except Exception as e:
            logger.exception("plot_export_failed", file_path=file_path, error=str(e))
            raise

    def _apply_downsampling(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Aplica downsampling baseado na configuração"""
        max_points = self.config.performance.max_points_2d

        if len(x) <= max_points:
            return x, y

        method = self.config.performance.downsample_method

        if method == "lttb":
            return _downsample_lttb(x, y, max_points, ["peaks", "valleys", "edges"])
        if method == "uniform":
            indices = np.linspace(0, len(x)-1, max_points, dtype=int)
            return x[indices], y[indices]
        # Default to uniform sampling
        indices = np.linspace(0, len(x)-1, max_points, dtype=int)
        return x[indices], y[indices]

    def _on_selection_changed(self):
        """Handler para mudança de seleção"""
        if not self._selection_enabled or not self._brush_selection:
            return

        # Get selection range
        x_min, x_max = self._brush_selection.getRegion()

        # Find indices in selection for all series
        selected_indices = set()

        for series_data in self._series_data.values():
            x_data = series_data["x_original"]
            mask = (x_data >= x_min) & (x_data <= x_max)
            series_indices = np.where(mask)[0]
            selected_indices.update(series_indices)

        # Convert to sorted array
        selected_indices = np.array(sorted(selected_indices))

        # Emit signal with both indices and range for sync
        self.selection_changed.emit(selected_indices)

        logger.debug("selection_changed",
                    x_range=(x_min, x_max),
                    n_selected=len(selected_indices))

    def _update_selection_from_sync(self, xmin: float, xmax: float) -> None:
        """Update selection region from external synchronization.
        
        Args:
            xmin: Minimum X value for selection
            xmax: Maximum X value for selection
        """
        if not self._brush_selection:
            return

        # Temporarily block signals to avoid circular updates
        self._brush_selection.blockSignals(True)
        try:
            self._brush_selection.setRegion((xmin, xmax))
            self._brush_selection.setVisible(True)
        finally:
            self._brush_selection.blockSignals(False)

        logger.debug("selection_synced", xmin=xmin, xmax=xmax)

    def _on_range_changed(self):
        """Handler para mudança de range"""
        view_box = self.plot_widget.getViewBox()
        x_range, y_range = view_box.viewRange()
        self.range_changed.emit(tuple(x_range), tuple(y_range))


class TimeseriesPlot(BaseFigure):
    """Wrapper para Plot2DWidget com interface BaseFigure"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Plot2DWidget | None = None

    def render(self, dataset: Dataset) -> Plot2DWidget:
        """
        Renderiza séries temporais do dataset

        Args:
            dataset: Dataset com séries temporais

        Returns:
            Widget PyQtGraph configurado
        """
        # Create widget if not exists
        if self._widget is None:
            self._widget = Plot2DWidget(self.config)

        # Clear existing series
        self._widget.clear_series()

        # Add all series from dataset
        for i, (series_id, series) in enumerate(dataset.series.items()):
            self._widget.add_series(
                series_id=series.name or series_id,
                x_data=dataset.t_seconds,
                y_data=series.values,
                series_index=i,
            )

        # Auto-range to show all data
        self._widget.auto_range()

        logger.info("timeseries_plot_rendered",
                   dataset_id=dataset.dataset_id,
                   n_series=len(dataset.series),
                   n_points=len(dataset.t_seconds))

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual no gráfico.
        
        Args:
            selection_indices: Array of indices to highlight in the plot.
        """
        if self._widget and len(selection_indices) > 0:
            # Highlight the selected region in the plot
            try:
                # Get data range from selection indices
                if hasattr(self, "_current_x_data") and self._current_x_data is not None:
                    x_data = self._current_x_data
                    x_min = x_data[selection_indices.min()]
                    x_max = x_data[selection_indices.max()]
                    self._widget.set_selection_region(x_min, x_max)
                else:
                    # Use indices directly if no x data available
                    self._widget.set_selection_region(
                        float(selection_indices.min()),
                        float(selection_indices.max()),
                    )
            except (IndexError, AttributeError):
                # Widget may not support selection region
                logger.debug("selection_update_skipped",
                           reason="widget_does_not_support_selection_region")

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta gráfico para arquivo"""
        if self._widget:
            width = kwargs.get("width", self.config.export_2d.default_width)
            height = kwargs.get("height", self.config.export_2d.default_height)
            self._widget.export_image(file_path, width, height)


class ScatterPlot(BaseFigure):
    """Scatter plot para análise de correlação"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: Plot2DWidget | None = None

    def render(self, x_series: Series, y_series: Series) -> Plot2DWidget:
        """
        Cria scatter plot entre duas séries

        Args:
            x_series: Série para eixo X
            y_series: Série para eixo Y

        Returns:
            Widget PyQtGraph configurado
        """
        # Create widget if not exists
        if self._widget is None:
            self._widget = Plot2DWidget(self.config)

        # Clear existing plots
        self._widget.clear_series()

        # Ensure same length (simple truncation for now)
        min_len = min(len(x_series.values), len(y_series.values))
        x_data = x_series.values[:min_len]
        y_data = y_series.values[:min_len]

        # Add scatter plot
        self._widget.add_series(
            series_id=f"{x_series.name} vs {y_series.name}",
            x_data=x_data,
            y_data=y_data,
            series_index=0,
            symbol="o",
            pen=None,  # No lines, only symbols
        )

        # Update axis labels
        self._widget.plot_widget.setLabel("left", y_series.name or "Y")
        self._widget.plot_widget.setLabel("bottom", x_series.name or "X")

        # Auto-range
        self._widget.auto_range()

        # Calculate correlation
        correlation = np.corrcoef(x_data, y_data)[0, 1]
        logger.info("scatter_plot_rendered",
                   x_series=x_series.name,
                   y_series=y_series.name,
                   correlation=correlation,
                   n_points=min_len)

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual"""
        # Placeholder implementation

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta scatter plot"""
        if self._widget:
            width = kwargs.get("width", self.config.export_2d.default_width)
            height = kwargs.get("height", self.config.export_2d.default_height)
            self._widget.export_image(file_path, width, height)


class MultipanelPlot:
    """
    Multipanel plot layout for visualizing multiple datasets.
    
    Provides a grid layout of Plot2DWidget instances with synchronized
    zooming and selection across panels.
    """

    def __init__(self, rows: int = 2, cols: int = 2, config: VizConfig | None = None):
        """Initialize multipanel plot.
        
        Args:
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            config: Visualization configuration
        """
        self.rows = rows
        self.cols = cols
        self.config = config
        self._panels: list[Plot2DWidget | None] = [None] * (rows * cols)

    def get_panel(self, row: int, col: int) -> Plot2DWidget | None:
        """Get panel at specified position.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            
        Returns:
            Panel widget or None if not set
        """
        idx = row * self.cols + col
        if 0 <= idx < len(self._panels):
            return self._panels[idx]
        return None

    def set_panel(self, row: int, col: int, panel: Plot2DWidget) -> None:
        """Set panel at specified position.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            panel: Plot2DWidget to place
        """
        idx = row * self.cols + col
        if 0 <= idx < len(self._panels):
            self._panels[idx] = panel

    def sync_x_axes(self) -> None:
        """Synchronize X axes across all panels.
        
        Links X-axis ranges so that zooming/panning in one panel
        affects all panels simultaneously.
        """
        # Get all valid panels
        valid_panels = [p for p in self._panels if p is not None]

        if len(valid_panels) < 2:
            logger.debug("sync_x_axes_skipped", reason="Less than 2 panels")
            return

        # Use first panel as reference
        reference_panel = valid_panels[0]
        reference_view = reference_panel.plot_widget.getViewBox()

        # Link all other panels to reference
        for panel in valid_panels[1:]:
            try:
                target_view = panel.plot_widget.getViewBox()
                target_view.setXLink(reference_view)
                logger.debug("panel_x_linked", panel=panel)
            except Exception as e:
                logger.error("failed_to_link_x_axis", error=str(e), panel=panel)

        logger.info("x_axes_synchronized", panel_count=len(valid_panels))

    def sync_selections(self) -> None:
        """Synchronize selections across all panels.
        
        When a selection is made in one panel, the same selection
        region is displayed in all other panels.
        """
        # Get all valid panels
        valid_panels = [p for p in self._panels if p is not None]

        if len(valid_panels) < 2:
            logger.debug("sync_selections_skipped", reason="Less than 2 panels")
            return

        # Connect selection changed signals between panels
        for source_panel in valid_panels:
            if not hasattr(source_panel, "_brush_selection") or source_panel._brush_selection is None:
                continue

            for target_panel in valid_panels:
                if source_panel is target_panel:
                    continue

                if not hasattr(target_panel, "_brush_selection") or target_panel._brush_selection is None:
                    continue

                try:
                    # Connect source selection changes to update target
                    source_panel.selection_changed.connect(
                        lambda xmin, xmax, panel=target_panel:
                        panel._update_selection_from_sync(xmin, xmax),
                    )
                except Exception as e:
                    logger.error("failed_to_sync_selections", error=str(e))

        logger.info("selections_synchronized", panel_count=len(valid_panels))

