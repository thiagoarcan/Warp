"""
Heatmaps - Sistema de visualização de heatmaps conforme seção 10.5

Features:
- Heatmaps com colormap configurável
- Correlation matrices
- Time-series heatmaps
- Statistical heatmaps
- Performance otimizada para grandes matrices
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np

try:
    import pyqtgraph as pg
    import scipy.stats
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget
    HEATMAP_DEPENDENCIES_AVAILABLE = True
except ImportError:
    HEATMAP_DEPENDENCIES_AVAILABLE = False

from platform_base.utils.logging import get_logger
from platform_base.viz.base import BaseFigure
from platform_base.viz.config import ColorScale, VizConfig

if TYPE_CHECKING:
    from platform_base.core.models import Dataset

logger = get_logger(__name__)


if not HEATMAP_DEPENDENCIES_AVAILABLE:
    logger.error("heatmap_dependencies_not_available",
                message="PyQtGraph and/or scipy not available for heatmap visualization")


def _create_colormap_lut(colorscale: ColorScale, n_colors: int = 256) -> np.ndarray:
    """Cria lookup table de cores para PyQtGraph"""
    if colorscale == ColorScale.VIRIDIS:
        # Simplified viridis colormap
        colors = np.array([
            [68, 1, 84],      # Dark purple
            [59, 82, 139],    # Blue
            [33, 144, 140],   # Teal
            [93, 201, 99],    # Green
            [253, 231, 37],    # Yellow
        ])
    elif colorscale == ColorScale.PLASMA:
        colors = np.array([
            [13, 8, 135],     # Dark blue
            [106, 0, 168],    # Purple
            [177, 42, 144],   # Magenta
            [228, 100, 98],   # Red-orange
            [252, 163, 54],    # Orange-yellow
        ])
    elif colorscale == ColorScale.COOLWARM:
        colors = np.array([
            [59, 76, 192],    # Cool blue
            [144, 178, 254],  # Light blue
            [255, 255, 255],  # White
            [255, 178, 144],  # Light red
            [180, 4, 38],      # Warm red
        ])
    else:
        # Default grayscale
        colors = np.array([
            [0, 0, 0],        # Black
            [255, 255, 255],   # White
        ])

    # Interpolate to desired number of colors
    n_base_colors = len(colors)
    indices = np.linspace(0, n_base_colors - 1, n_colors)

    lut = np.zeros((n_colors, 3), dtype=np.uint8)
    for i in range(3):  # RGB channels
        lut[:, i] = np.interp(indices, np.arange(n_base_colors), colors[:, i])

    return lut


class HeatmapWidget(QWidget):
    """
    Widget para visualização de heatmaps conforme seção 10.5

    Features:
    - Colormap configurável
    - Zoom e pan interativos
    - Tooltips com valores
    - Export de imagens
    - Colorbar com escala
    """

    # Signals
    cell_clicked = pyqtSignal(int, int, float)  # row, col, value

    def __init__(self, config: VizConfig, parent: QWidget | None = None):
        super().__init__(parent)

        if not HEATMAP_DEPENDENCIES_AVAILABLE:
            raise ImportError("Dependencies not available for heatmap visualization")

        self.config = config
        self.current_data: np.ndarray | None = None
        self.x_labels: list[str] | None = None
        self.y_labels: list[str] | None = None

        self._setup_ui()

        logger.debug("heatmap_widget_initialized")

    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Controls
        controls_layout = QHBoxLayout()

        # Colormap selector
        controls_layout.addWidget(QLabel("Colormap:"))
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems([
            "viridis", "plasma", "coolwarm", "grayscale",
        ])
        self.colormap_combo.currentTextChanged.connect(self._update_colormap)
        controls_layout.addWidget(self.colormap_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Heatmap plot
        self.heatmap_widget = pg.PlotWidget()
        self.heatmap_widget.setAspectLocked(True)

        # Create image item for heatmap
        self.image_item = pg.ImageItem()
        self.heatmap_widget.addItem(self.image_item)

        # Create colorbar
        self.colorbar = pg.ColorBarItem(
            values=(0, 1),
            colorMap=pg.colormap.get("viridis"),
            width=20,
            interactive=False,
        )
        self.colorbar.setImageItem(self.image_item)

        layout.addWidget(self.heatmap_widget)

        # Configure plot widget
        self.heatmap_widget.setLabel("left", "Rows")
        self.heatmap_widget.setLabel("bottom", "Columns")
        self.heatmap_widget.showGrid(
            x=self.config.style.grid_enabled,
            y=self.config.style.grid_enabled,
            alpha=self.config.style.grid_alpha,
        )

        # Apply theme
        self._apply_theme()

    def _apply_theme(self):
        """Aplica tema à visualização"""
        from platform_base.viz.figures_2d import _hex_to_qcolor

        bg_color = _hex_to_qcolor(self.config.colors.background_color)
        self.heatmap_widget.setBackground(bg_color)

    def set_data(self, data: np.ndarray, x_labels: list[str] | None = None,
                 y_labels: list[str] | None = None, title: str = "Heatmap"):
        """
        Define dados do heatmap

        Args:
            data: Array 2D com dados do heatmap
            x_labels: Labels para eixo X (colunas)
            y_labels: Labels para eixo Y (linhas)
            title: Título do heatmap
        """
        start_time = time.perf_counter()

        self.current_data = data.copy()
        self.x_labels = x_labels
        self.y_labels = y_labels

        # Transpose data for correct orientation in PyQtGraph
        display_data = data.T

        # Set image data
        self.image_item.setImage(display_data)

        # Update colorbar range
        self.colorbar.setLevels((np.nanmin(data), np.nanmax(data)))

        # Set axis labels
        if x_labels is not None:
            # Create custom axis with labels
            x_axis = self.heatmap_widget.getAxis("bottom")
            x_ticks = [(i, label) for i, label in enumerate(x_labels)]
            x_axis.setTicks([x_ticks])

        if y_labels is not None:
            y_axis = self.heatmap_widget.getAxis("left")
            y_ticks = [(i, label) for i, label in enumerate(y_labels)]
            y_axis.setTicks([y_ticks])

        # Set title
        self.heatmap_widget.setTitle(title)

        # Auto-range to fit data
        self.heatmap_widget.autoRange()

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("heatmap_data_set",
                   shape=data.shape,
                   duration_ms=duration_ms)

    def _update_colormap(self, colormap_name: str):
        """Atualiza colormap do heatmap"""
        try:
            if colormap_name == "viridis":
                colorscale = ColorScale.VIRIDIS
            elif colormap_name == "plasma":
                colorscale = ColorScale.PLASMA
            elif colormap_name == "coolwarm":
                colorscale = ColorScale.COOLWARM
            else:
                colorscale = ColorScale.GRAYSCALE

            # Create custom colormap
            lut = _create_colormap_lut(colorscale)

            # Update image item colormap
            colormap = pg.ColorMap(pos=np.linspace(0, 1, len(lut)), color=lut)
            self.image_item.setColorMap(colormap)

            # Update colorbar
            self.colorbar.setColorMap(colormap)

            logger.debug("heatmap_colormap_updated", colormap=colormap_name)

        except Exception as e:
            logger.exception("heatmap_colormap_update_failed", colormap=colormap_name, error=str(e))

    def export_image(self, file_path: str, width: int = 1920, height: int = 1080):
        """Exporta heatmap como imagem"""
        try:
            exporter = pg.exporters.ImageExporter(self.heatmap_widget.plotItem)
            exporter.parameters()["width"] = width
            exporter.parameters()["height"] = height
            exporter.export(file_path)

            logger.info("heatmap_exported", file_path=file_path, width=width, height=height)

        except Exception as e:
            logger.exception("heatmap_export_failed", file_path=file_path, error=str(e))
            raise


class CorrelationHeatmap(BaseFigure):
    """Heatmap de correlação entre séries"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: HeatmapWidget | None = None

    def render(self, dataset: Dataset, method: str = "pearson") -> HeatmapWidget:
        """
        Cria heatmap de correlação

        Args:
            dataset: Dataset com múltiplas séries
            method: Método de correlação ('pearson', 'spearman', 'kendall')
        """
        # Create widget if not exists
        if self._widget is None:
            self._widget = HeatmapWidget(self.config)

        series_list = list(dataset.series.values())
        if len(series_list) < 2:
            raise ValueError("Need at least 2 series for correlation heatmap")

        # Prepare data matrix
        series_names = [series.name or series.series_id for series in series_list]
        n_series = len(series_list)
        min_length = min(len(series.values) for series in series_list)

        # Create data matrix (samples x features)
        data_matrix = np.zeros((min_length, n_series))
        for i, series in enumerate(series_list):
            data_matrix[:, i] = series.values[:min_length]

        # Calculate correlation matrix
        if method == "pearson":
            corr_matrix = np.corrcoef(data_matrix.T)
        elif method == "spearman":
            corr_matrix, _ = scipy.stats.spearmanr(data_matrix, axis=0)
        elif method == "kendall":
            # Kendall correlation is expensive, so we'll compute it pairwise
            corr_matrix = np.zeros((n_series, n_series))
            for i in range(n_series):
                for j in range(n_series):
                    if i == j:
                        corr_matrix[i, j] = 1.0
                    else:
                        tau, _ = scipy.stats.kendalltau(data_matrix[:, i], data_matrix[:, j])
                        corr_matrix[i, j] = tau
        else:
            raise ValueError(f"Unknown correlation method: {method}")

        # Set data to widget
        self._widget.set_data(
            data=corr_matrix,
            x_labels=series_names,
            y_labels=series_names,
            title=f"Correlation Matrix ({method.capitalize()})",
        )

        # Set colormap to coolwarm (good for correlation)
        self._widget.colormap_combo.setCurrentText("coolwarm")

        logger.info("correlation_heatmap_rendered",
                   method=method,
                   n_series=n_series,
                   min_length=min_length)

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual"""

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta correlation heatmap"""
        if self._widget:
            width = kwargs.get("width", self.config.export_2d.default_width)
            height = kwargs.get("height", self.config.export_2d.default_height)
            self._widget.export_image(file_path, width, height)


class TimeSeriesHeatmap(BaseFigure):
    """Heatmap temporal de múltiplas séries"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: HeatmapWidget | None = None

    def render(self, dataset: Dataset, time_bins: int = 100) -> HeatmapWidget:
        """
        Cria heatmap temporal

        Args:
            dataset: Dataset com séries temporais
            time_bins: Número de bins temporais
        """
        # Create widget if not exists
        if self._widget is None:
            self._widget = HeatmapWidget(self.config)

        series_list = list(dataset.series.values())
        if len(series_list) == 0:
            raise ValueError("No series in dataset")

        # Prepare data
        n_series = len(series_list)
        n_time = len(dataset.t_seconds)

        # Bin time if needed
        if n_time > time_bins:
            bin_size = n_time // time_bins
            binned_data = np.zeros((time_bins, n_series))
            time_labels = []

            for i in range(time_bins):
                start_idx = i * bin_size
                end_idx = min((i + 1) * bin_size, n_time)

                for j, series in enumerate(series_list):
                    binned_data[i, j] = np.nanmean(series.values[start_idx:end_idx])

                # Create time label
                avg_time = np.mean(dataset.t_seconds[start_idx:end_idx])
                time_labels.append(f"{avg_time:.1f}s")
        else:
            # Use all time points
            binned_data = np.zeros((n_time, n_series))
            for j, series in enumerate(series_list):
                binned_data[:, j] = series.values

            time_labels = [f"{t:.1f}s" for t in dataset.t_seconds[::max(1, n_time//20)]]

        # Series names
        series_names = [series.name or series.series_id for series in series_list]

        # Set data to widget
        self._widget.set_data(
            data=binned_data,
            x_labels=series_names,
            y_labels=time_labels,
            title="Time Series Heatmap",
        )

        logger.info("timeseries_heatmap_rendered",
                   n_series=n_series,
                   n_time_bins=len(time_labels))

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual"""

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta time series heatmap"""
        if self._widget:
            width = kwargs.get("width", self.config.export_2d.default_width)
            height = kwargs.get("height", self.config.export_2d.default_height)
            self._widget.export_image(file_path, width, height)


class StatisticalHeatmap(BaseFigure):
    """Heatmap de estatísticas por janela temporal"""

    def __init__(self, config: VizConfig):
        super().__init__(config)
        self._widget: HeatmapWidget | None = None

    def render(self, dataset: Dataset, window_size: int = 100,
               statistics: list[str] | None = None) -> HeatmapWidget:
        """
        Cria heatmap de estatísticas

        Args:
            dataset: Dataset com séries temporais
            window_size: Tamanho da janela para cálculo de estatísticas
            statistics: Lista de estatísticas ('mean', 'std', 'min', 'max', 'median')
        """
        if statistics is None:
            statistics = ["mean", "std", "min", "max"]

        # Create widget if not exists
        if self._widget is None:
            self._widget = HeatmapWidget(self.config)

        series_list = list(dataset.series.values())
        if len(series_list) == 0:
            raise ValueError("No series in dataset")

        n_series = len(series_list)
        n_stats = len(statistics)
        n_time = len(dataset.t_seconds)
        n_windows = max(1, n_time // window_size)

        # Calculate statistics matrix
        stats_matrix = np.zeros((n_windows, n_series * n_stats))
        window_labels = []
        stat_labels = []

        # Create labels
        for series in series_list:
            series_name = series.name or series.series_id
            for stat in statistics:
                stat_labels.append(f"{series_name}_{stat}")

        # Calculate statistics for each window
        for w in range(n_windows):
            start_idx = w * window_size
            end_idx = min((w + 1) * window_size, n_time)

            window_labels.append(f"Win_{w}")

            col_idx = 0
            for series in series_list:
                window_data = series.values[start_idx:end_idx]

                for stat in statistics:
                    if stat == "mean":
                        value = np.nanmean(window_data)
                    elif stat == "std":
                        value = np.nanstd(window_data)
                    elif stat == "min":
                        value = np.nanmin(window_data)
                    elif stat == "max":
                        value = np.nanmax(window_data)
                    elif stat == "median":
                        value = np.nanmedian(window_data)
                    else:
                        value = np.nan

                    stats_matrix[w, col_idx] = value
                    col_idx += 1

        # Set data to widget
        self._widget.set_data(
            data=stats_matrix,
            x_labels=stat_labels,
            y_labels=window_labels,
            title=f"Statistical Heatmap (window={window_size})",
        )

        logger.info("statistical_heatmap_rendered",
                   n_series=n_series,
                   n_windows=n_windows,
                   statistics=statistics)

        return self._widget

    def update_selection(self, selection_indices: np.ndarray):
        """Atualiza seleção visual"""

    def export(self, file_path: str, format: str, **kwargs):
        """Exporta statistical heatmap"""
        if self._widget:
            width = kwargs.get("width", self.config.export_2d.default_width)
            height = kwargs.get("height", self.config.export_2d.default_height)
            self._widget.export_image(file_path, width, height)


# =============================================================================
# Simple Heatmap class for test compatibility
# =============================================================================

class Heatmap:
    """
    Simple Heatmap class for creating and manipulating heatmaps.
    
    This is a high-level interface that doesn't require a VizConfig.
    """
    
    AVAILABLE_COLORMAPS = [
        "viridis", "plasma", "inferno", "magma", "cividis",
        "hot", "cool", "coolwarm", "jet", "rainbow",
        "gray", "bone", "copper", "spring", "summer",
        "autumn", "winter", "spectral", "RdYlBu", "RdYlGn"
    ]
    
    def __init__(self, data: np.ndarray = None, x_labels: list = None, 
                 y_labels: list = None, normalize: bool = False,
                 colormap: str = "viridis", title: str = "Heatmap",
                 mask_nan: bool = False):
        """
        Initialize a Heatmap.
        
        Args:
            data: 2D array of values
            x_labels: Labels for x-axis (columns)
            y_labels: Labels for y-axis (rows)
            normalize: Whether to normalize data to [0, 1]
            colormap: Colormap name
            title: Heatmap title
            mask_nan: Whether to mask NaN values
        """
        self._data = None
        self._normalized_data = None
        self._x_labels = x_labels
        self._y_labels = y_labels
        self._normalize = normalize
        self._colormap = colormap
        self._title = title
        self._annotations = None
        self._vmin = None
        self._vmax = None
        self._mask_nan = mask_nan
        
        if data is not None:
            self.set_data(data)
    
    def set_data(self, data: np.ndarray) -> None:
        """Set the heatmap data."""
        self._data = np.asarray(data).copy()
        
        if self._normalize:
            self._update_normalized_data()
    
    def get_data(self) -> np.ndarray:
        """Get the original data."""
        return self._data.copy() if self._data is not None else None
    
    def _update_normalized_data(self) -> None:
        """Update normalized data cache."""
        if self._data is None:
            return
        
        data_min = np.nanmin(self._data)
        data_max = np.nanmax(self._data)
        
        if data_max - data_min > 0:
            self._normalized_data = (self._data - data_min) / (data_max - data_min)
        else:
            self._normalized_data = np.zeros_like(self._data)
    
    def get_normalized_data(self) -> np.ndarray:
        """Get normalized data (0-1 range)."""
        if self._normalized_data is None and self._data is not None:
            self._update_normalized_data()
        return self._normalized_data.copy() if self._normalized_data is not None else None
    
    def set_colormap(self, colormap: str) -> None:
        """Set the colormap."""
        if colormap in self.AVAILABLE_COLORMAPS:
            self._colormap = colormap
        else:
            logger.warning(f"Unknown colormap: {colormap}. Using default.")
    
    def get_colormap(self) -> str:
        """Get current colormap."""
        return self._colormap
    
    @classmethod
    def get_available_colormaps(cls) -> list:
        """Get list of available colormaps."""
        return cls.AVAILABLE_COLORMAPS.copy()
    
    def set_labels(self, x_labels: list = None, y_labels: list = None) -> None:
        """Set axis labels."""
        if x_labels is not None:
            self._x_labels = x_labels
        if y_labels is not None:
            self._y_labels = y_labels
    
    def get_labels(self) -> tuple:
        """Get axis labels."""
        return (self._x_labels, self._y_labels)
    
    def set_title(self, title: str) -> None:
        """Set heatmap title."""
        self._title = title
    
    def get_title(self) -> str:
        """Get heatmap title."""
        return self._title
    
    def set_value_range(self, vmin: float = None, vmax: float = None) -> None:
        """Set value range for colormap."""
        self._vmin = vmin
        self._vmax = vmax
    
    def get_value_range(self) -> tuple:
        """Get value range."""
        if self._data is None:
            return (None, None)
        
        vmin = self._vmin if self._vmin is not None else np.nanmin(self._data)
        vmax = self._vmax if self._vmax is not None else np.nanmax(self._data)
        return (vmin, vmax)
    
    def set_annotations(self, show: bool = True, format_str: str = ".2f") -> None:
        """Set annotation display."""
        self._annotations = {"show": show, "format": format_str}
    
    def get_cell_value(self, row: int, col: int) -> float:
        """Get value at specific cell."""
        if self._data is None:
            raise ValueError("No data set")
        return float(self._data[row, col])
    
    def get_statistics(self) -> dict:
        """Get basic statistics of the data."""
        if self._data is None:
            return {}
        
        return {
            "min": float(np.nanmin(self._data)),
            "max": float(np.nanmax(self._data)),
            "mean": float(np.nanmean(self._data)),
            "std": float(np.nanstd(self._data)),
            "shape": self._data.shape,
        }
    
    def resize(self, new_shape: tuple) -> None:
        """Resize heatmap data using interpolation."""
        if self._data is None:
            return
        
        from scipy.ndimage import zoom
        
        current_shape = self._data.shape
        zoom_factors = (new_shape[0] / current_shape[0], new_shape[1] / current_shape[1])
        self._data = zoom(self._data, zoom_factors)
        
        if self._normalize:
            self._update_normalized_data()
    
    def render(self) -> np.ndarray:
        """Render heatmap to RGB array."""
        if self._data is None:
            return None
        
        # Use matplotlib for rendering if available
        try:
            import matplotlib.pyplot as plt
            
            cmap = plt.get_cmap(self._colormap)
            normalized = self.get_normalized_data()
            
            # Apply colormap
            rgba = cmap(normalized)
            rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
            
            return rgb
        except ImportError:
            # Fallback to grayscale
            normalized = self.get_normalized_data()
            gray = (normalized * 255).astype(np.uint8)
            return np.stack([gray, gray, gray], axis=-1)
    
    def export(self, filepath: str, dpi: int = 100) -> None:
        """Export heatmap to file."""
        if self._data is None:
            raise ValueError("No data to export")
        
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            vmin, vmax = self.get_value_range()
            im = ax.imshow(self._data, cmap=self._colormap, vmin=vmin, vmax=vmax, aspect='auto')
            
            plt.colorbar(im, ax=ax)
            ax.set_title(self._title)
            
            if self._x_labels:
                ax.set_xticks(range(len(self._x_labels)))
                ax.set_xticklabels(self._x_labels, rotation=45, ha='right')
            
            if self._y_labels:
                ax.set_yticks(range(len(self._y_labels)))
                ax.set_yticklabels(self._y_labels)
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=dpi)
            plt.close(fig)
            
            logger.info(f"Heatmap exported to {filepath}")
        except ImportError:
            logger.warning("matplotlib not available for export")


def correlation_heatmap(data: np.ndarray, method: str = "pearson",
                        labels: list = None) -> Heatmap:
    """
    Create a correlation heatmap.
    
    Args:
        data: 2D array where each column is a variable
        method: Correlation method ('pearson', 'spearman', 'kendall')
        labels: Variable names
        
    Returns:
        Heatmap instance with correlation matrix
    """
    if method == "pearson":
        corr_matrix = np.corrcoef(data.T)
    elif method == "spearman":
        corr_matrix, _ = scipy.stats.spearmanr(data, axis=0)
        if np.isscalar(corr_matrix):
            corr_matrix = np.array([[1.0, corr_matrix], [corr_matrix, 1.0]])
    elif method == "kendall":
        n_vars = data.shape[1]
        corr_matrix = np.zeros((n_vars, n_vars))
        for i in range(n_vars):
            for j in range(n_vars):
                if i == j:
                    corr_matrix[i, j] = 1.0
                else:
                    tau, _ = scipy.stats.kendalltau(data[:, i], data[:, j])
                    corr_matrix[i, j] = tau
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return Heatmap(
        data=corr_matrix,
        x_labels=labels,
        y_labels=labels,
        colormap="coolwarm",
        title=f"Correlation Matrix ({method.capitalize()})"
    )


def spectrogram_heatmap(signal: np.ndarray, sample_rate: float = None,
                        window_size: int = 256, overlap: float = 0.5,
                        fs: float = None) -> Heatmap:
    """
    Create a spectrogram heatmap.
    
    Args:
        signal: 1D signal array
        sample_rate: Sampling rate in Hz (or use fs as alias)
        window_size: FFT window size
        overlap: Window overlap fraction
        fs: Alias for sample_rate (for scipy compatibility)
        
    Returns:
        Heatmap instance with spectrogram data
    """
    # Handle fs alias
    if sample_rate is None and fs is not None:
        sample_rate = fs
    elif sample_rate is None:
        sample_rate = 1000.0  # Default sample rate
    
    try:
        from scipy.signal import spectrogram as scipy_spectrogram
        
        nperseg = window_size
        noverlap = int(window_size * overlap)
        
        f, t, Sxx = scipy_spectrogram(signal, fs=sample_rate, 
                                       nperseg=nperseg, noverlap=noverlap)
        
        # Convert to dB
        Sxx_db = 10 * np.log10(Sxx + 1e-10)
        
        # Create labels
        time_labels = [f"{ti:.2f}s" for ti in t[::max(1, len(t)//10)]]
        freq_labels = [f"{fi:.0f}Hz" for fi in f[::max(1, len(f)//10)]]
        
        return Heatmap(
            data=Sxx_db,
            x_labels=time_labels,
            y_labels=freq_labels,
            colormap="viridis",
            title="Spectrogram"
        )
    except ImportError:
        logger.warning("scipy not available for spectrogram")
        return Heatmap(title="Spectrogram (scipy required)")
