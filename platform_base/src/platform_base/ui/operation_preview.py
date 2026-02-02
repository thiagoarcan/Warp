"""
Operation Preview - Sistema de preview em tempo real para operações

Features:
- Preview em tempo real de operações
- Cache de resultados para performance
- Integração com diferentes tipos de operação
- Visualização interativa de resultados
- Comparação antes/depois
"""

from __future__ import annotations

import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTabWidget, QVBoxLayout, QWidget


try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class PreviewMode(Enum):
    """Modos de preview"""
    DISABLED = "disabled"
    MANUAL = "manual"      # Apenas quando solicitado
    AUTO = "auto"          # Automático com delay
    REALTIME = "realtime"  # Tempo real (pode ser custoso)


@dataclass
class PreviewRequest:
    """Request de preview"""
    operation_type: str
    parameters: dict[str, Any]
    input_data: dict[str, np.ndarray]
    timestamp: float = field(default_factory=time.time)
    request_id: str = field(default_factory=lambda: f"preview_{int(time.time() * 1000000)}")


@dataclass
class PreviewResult:
    """Resultado de preview"""
    request_id: str
    operation_type: str
    parameters: dict[str, Any]
    original_data: dict[str, np.ndarray]
    processed_data: dict[str, np.ndarray]
    metadata: dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: float = field(default_factory=time.time)


class PreviewProcessor(QObject):
    """Processador de previews em background"""

    # Signals
    preview_completed = pyqtSignal(object)  # PreviewResult
    preview_failed = pyqtSignal(str, str)   # request_id, error

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        # Thread pool para processamento
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="preview")

        # Cache de resultados
        self.result_cache: dict[str, PreviewResult] = {}
        self.cache_max_size = 50

        # Processadores de operação
        self.operation_processors = {
            "interpolation": self._process_interpolation,
            "synchronization": self._process_synchronization,
            "calculus": self._process_calculus,
        }

    def submit_preview(self, request: PreviewRequest) -> Future:
        """Submete request de preview para processamento"""

        # Check cache first
        cache_key = self._get_cache_key(request)
        if cache_key in self.result_cache:
            cached_result = self.result_cache[cache_key]
            # Emit immediately for cached results
            self.preview_completed.emit(cached_result)
            return None

        # Submit to thread pool
        return self.executor.submit(self._process_preview, request)

    def _process_preview(self, request: PreviewRequest) -> PreviewResult:
        """Processa preview request"""
        start_time = time.perf_counter()

        try:
            processor = self.operation_processors.get(request.operation_type)
            if not processor:
                raise ValueError(f"Unknown operation type: {request.operation_type}")

            # Process the operation
            processed_data, metadata = processor(request.input_data, request.parameters)

            # Create result
            result = PreviewResult(
                request_id=request.request_id,
                operation_type=request.operation_type,
                parameters=request.parameters,
                original_data=request.input_data,
                processed_data=processed_data,
                metadata=metadata,
                processing_time=time.perf_counter() - start_time,
            )

            # Cache result
            cache_key = self._get_cache_key(request)
            self._add_to_cache(cache_key, result)

            # Emit completion signal
            self.preview_completed.emit(result)

            return result

        except Exception as e:
            logger.exception("preview_processing_failed",
                        request_id=request.request_id,
                        operation=request.operation_type,
                        error=str(e))

            self.preview_failed.emit(request.request_id, str(e))
            raise

    def _process_interpolation(self, input_data: dict[str, np.ndarray],
                             parameters: dict[str, Any]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        """Processa preview de interpolação"""

        # Extract parameters
        method = parameters.get("method", "linear")
        num_points = parameters.get("num_points", 1000)

        processed_data = {}
        metadata = {"method": method, "num_points": num_points}

        for series_name, values in input_data.items():
            if series_name.startswith("time"):
                continue  # Skip time arrays

            # Get corresponding time array
            time_key = f"time_{series_name}" if f"time_{series_name}" in input_data else "time"
            time_array = input_data.get(time_key, np.arange(len(values)))

            # Create interpolated data
            if method == "linear":
                new_time = np.linspace(time_array[0], time_array[-1], num_points)
                new_values = np.interp(new_time, time_array, values)
            elif method == "cubic_spline":
                from scipy.interpolate import CubicSpline
                cs = CubicSpline(time_array, values)
                new_time = np.linspace(time_array[0], time_array[-1], num_points)
                new_values = cs(new_time)
            else:
                # Fallback to linear
                new_time = np.linspace(time_array[0], time_array[-1], num_points)
                new_values = np.interp(new_time, time_array, values)

            processed_data[f"time_{series_name}"] = new_time
            processed_data[series_name] = new_values

        return processed_data, metadata

    def _process_synchronization(self, input_data: dict[str, np.ndarray],
                               parameters: dict[str, Any]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        """Processa preview de sincronização"""

        method = parameters.get("method", "common_grid")
        sample_rate = parameters.get("sample_rate", 1.0)

        processed_data = {}
        metadata = {"method": method, "sample_rate": sample_rate}

        # Find common time range
        time_arrays = {k: v for k, v in input_data.items() if k.startswith("time")}
        if not time_arrays:
            return input_data, metadata

        # Calculate common time grid
        min_time = max(np.min(t) for t in time_arrays.values())
        max_time = min(np.max(t) for t in time_arrays.values())

        common_time = np.arange(min_time, max_time, 1.0 / sample_rate)

        for series_name, values in input_data.items():
            if series_name.startswith("time"):
                continue

            # Get corresponding time
            time_key = f"time_{series_name}" if f"time_{series_name}" in input_data else "time"
            if time_key in input_data:
                original_time = input_data[time_key]
                # Interpolate to common grid
                synced_values = np.interp(common_time, original_time, values)
                processed_data[series_name] = synced_values

        processed_data["time"] = common_time

        return processed_data, metadata

    def _process_calculus(self, input_data: dict[str, np.ndarray],
                        parameters: dict[str, Any]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        """Processa preview de cálculos"""

        operation = parameters.get("operation", "derivative")
        window_size = parameters.get("window_size", 5)

        processed_data = {}
        metadata = {"operation": operation, "window_size": window_size}

        for series_name, values in input_data.items():
            if series_name.startswith("time"):
                processed_data[series_name] = values  # Keep time arrays as-is
                continue

            # Apply operation
            if operation == "derivative":
                result = np.gradient(values)
            elif operation == "second_derivative":
                result = np.gradient(np.gradient(values))
            elif operation == "integral":
                result = np.cumsum(values)
            elif operation == "moving_average":
                # Simple moving average
                if window_size >= len(values):
                    result = np.full_like(values, np.mean(values))
                else:
                    padded = np.pad(values, (window_size//2, window_size//2), mode="edge")
                    result = np.convolve(padded, np.ones(window_size)/window_size, mode="valid")
            else:
                result = values  # No operation

            processed_data[series_name] = result

        return processed_data, metadata

    def _get_cache_key(self, request: PreviewRequest) -> str:
        """Gera chave de cache para request"""
        # Create deterministic cache key
        param_str = str(sorted(request.parameters.items()))
        data_hash = str(hash(str(sorted(request.input_data.keys()))))
        return f"{request.operation_type}_{hash(param_str)}_{data_hash}"

    def _add_to_cache(self, key: str, result: PreviewResult):
        """Adiciona resultado ao cache"""
        if len(self.result_cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = min(self.result_cache.keys(),
                           key=lambda k: self.result_cache[k].timestamp)
            del self.result_cache[oldest_key]

        self.result_cache[key] = result

    def clear_cache(self):
        """Limpa cache de resultados"""
        self.result_cache.clear()


class PreviewVisualizationWidget(QWidget):
    """Widget de visualização de previews"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.current_result: PreviewResult | None = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup da interface"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Preview")
        self.title_label.setFont(QFont("", 12, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray; font-size: 9pt;")
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Tabs for different views
        self.tabs = QTabWidget()

        # Comparison tab
        self.comparison_tab = self._create_comparison_tab()
        self.tabs.addTab(self.comparison_tab, "Before/After")

        # Statistics tab
        self.stats_tab = self._create_statistics_tab()
        self.tabs.addTab(self.stats_tab, "Statistics")

        layout.addWidget(self.tabs)

    def _create_comparison_tab(self) -> QWidget:
        """Cria aba de comparação"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        if MATPLOTLIB_AVAILABLE:
            self.comparison_figure = Figure(figsize=(10, 6))
            self.comparison_canvas = FigureCanvas(self.comparison_figure)
            layout.addWidget(self.comparison_canvas)
        else:
            label = QLabel("Matplotlib required for visualization")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

        return widget

    def _create_statistics_tab(self) -> QWidget:
        """Cria aba de estatísticas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.stats_label = QLabel("No statistics available")
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)

        return widget

    def update_preview(self, result: PreviewResult):
        """Atualiza preview com novo resultado"""
        self.current_result = result

        self.title_label.setText(f"Preview: {result.operation_type.title()}")
        self.status_label.setText(f"Processed in {result.processing_time:.3f}s")

        self._update_comparison_plot()
        self._update_statistics()

    def _update_comparison_plot(self):
        """Atualiza plot de comparação"""
        if not MATPLOTLIB_AVAILABLE or not self.current_result:
            return

        self.comparison_figure.clear()

        result = self.current_result

        # Create subplots for each series
        series_names = [k for k in result.original_data if not k.startswith("time")]
        n_series = len(series_names)

        if n_series == 0:
            return

        for i, series_name in enumerate(series_names):
            ax = self.comparison_figure.add_subplot(n_series, 1, i + 1)

            # Original data
            original_data = result.original_data[series_name]
            original_time = result.original_data.get(f"time_{series_name}",
                                                    result.original_data.get("time",
                                                    np.arange(len(original_data))))

            ax.plot(original_time, original_data, "b-", alpha=0.7, label="Original")

            # Processed data
            if series_name in result.processed_data:
                processed_data = result.processed_data[series_name]
                processed_time = result.processed_data.get(f"time_{series_name}",
                                                          result.processed_data.get("time",
                                                          np.arange(len(processed_data))))

                ax.plot(processed_time, processed_data, "r-", alpha=0.8, label="Processed")

            ax.set_title(f"{series_name}")
            ax.legend()
            ax.grid(True, alpha=0.3)

            if i == n_series - 1:  # Last subplot
                ax.set_xlabel("Time")

        self.comparison_figure.tight_layout()
        self.comparison_canvas.draw()

    def _update_statistics(self):
        """Atualiza estatísticas"""
        if not self.current_result:
            self.stats_label.setText("No statistics available")
            return

        result = self.current_result

        stats_text = f"Operation: {result.operation_type}\n"
        stats_text += f"Processing time: {result.processing_time:.3f}s\n"
        stats_text += f"Parameters: {len(result.parameters)}\n\n"

        # Parameter details
        for key, value in result.parameters.items():
            stats_text += f"{key}: {value}\n"

        stats_text += "\n"

        # Data statistics
        for series_name in result.original_data:
            if series_name.startswith("time"):
                continue

            original = result.original_data[series_name]
            stats_text += f"\n{series_name}:\n"
            stats_text += f"  Original: {len(original)} points\n"
            stats_text += f"  Mean: {np.mean(original):.3f}\n"
            stats_text += f"  Std: {np.std(original):.3f}\n"

            if series_name in result.processed_data:
                processed = result.processed_data[series_name]
                stats_text += f"  Processed: {len(processed)} points\n"
                stats_text += f"  New Mean: {np.mean(processed):.3f}\n"
                stats_text += f"  New Std: {np.std(processed):.3f}\n"

        self.stats_label.setText(stats_text)


class OperationPreviewManager(QObject):
    """Manager principal para preview de operações"""

    # Signals
    preview_updated = pyqtSignal(object)  # PreviewResult
    preview_error = pyqtSignal(str)       # error message

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self.mode = PreviewMode.AUTO
        self.processor = PreviewProcessor()

        # Timer para delays automáticos
        self.auto_timer = QTimer()
        self.auto_timer.setSingleShot(True)
        self.auto_timer.timeout.connect(self._process_pending_request)

        self.pending_request: PreviewRequest | None = None

        # Connect processor signals
        self.processor.preview_completed.connect(self._on_preview_completed)
        self.processor.preview_failed.connect(self._on_preview_failed)

    def set_mode(self, mode: PreviewMode):
        """Define modo de preview"""
        self.mode = mode
        logger.info("preview_mode_changed", mode=mode.value)

    def request_preview(self, operation_type: str, parameters: dict[str, Any],
                       input_data: dict[str, np.ndarray]) -> str | None:
        """Requisita preview de operação"""

        if self.mode == PreviewMode.DISABLED:
            return None

        request = PreviewRequest(
            operation_type=operation_type,
            parameters=parameters,
            input_data=input_data,
        )

        if self.mode == PreviewMode.REALTIME:
            # Process immediately
            self.processor.submit_preview(request)
        elif self.mode == PreviewMode.AUTO:
            # Delay processing
            self.pending_request = request
            self.auto_timer.start(500)  # 500ms delay
        elif self.mode == PreviewMode.MANUAL:
            # Store for manual processing
            self.pending_request = request

        return request.request_id

    def process_manual_preview(self) -> bool:
        """Processa preview manual pendente"""
        if self.pending_request and self.mode == PreviewMode.MANUAL:
            self.processor.submit_preview(self.pending_request)
            return True
        return False

    @pyqtSlot()
    def _process_pending_request(self):
        """Processa request pendente (para modo AUTO)"""
        if self.pending_request:
            self.processor.submit_preview(self.pending_request)
            self.pending_request = None

    @pyqtSlot(object)
    def _on_preview_completed(self, result: PreviewResult):
        """Callback quando preview completa"""
        self.preview_updated.emit(result)
        logger.debug("preview_completed",
                    request_id=result.request_id,
                    operation=result.operation_type,
                    processing_time=result.processing_time)

    @pyqtSlot(str, str)
    def _on_preview_failed(self, request_id: str, error: str):
        """Callback quando preview falha"""
        self.preview_error.emit(f"Preview failed: {error}")
        logger.error("preview_failed", request_id=request_id, error=error)

    def clear_cache(self):
        """Limpa cache do processor"""
        self.processor.clear_cache()


# Global preview manager instance
_preview_manager: OperationPreviewManager | None = None


def get_preview_manager() -> OperationPreviewManager:
    """Retorna manager global de preview"""
    global _preview_manager
    if _preview_manager is None:
        _preview_manager = OperationPreviewManager()
    return _preview_manager


def cleanup_preview_manager():
    """Limpa manager global (para shutdown)"""
    global _preview_manager
    if _preview_manager:
        _preview_manager.processor.executor.shutdown(wait=True)
        _preview_manager = None
