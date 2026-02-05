"""
Stream Filters - Widget para configuração avançada de filtros conforme seção 11.2

Features:
- Filtros temporais (inclusão/exclusão)
- Filtros de amostragem (LTTB, minmax, adaptive)
- Filtros de qualidade (interpolated, NaN, threshold)
- Filtros de valor (predicados condicionais)
- Filtros visuais (smoothing, hidden series, scale)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from platform_base.core.models import SeriesID
from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.utils.logging import get_logger
from platform_base.viz.streaming import (
    SmoothConfig,
    StreamFilters,
    TimeInterval,
    ValuePredicate,
)

logger = get_logger(__name__)


class TimeIntervalWidget(QWidget):
    """Widget para configurar intervalo temporal"""

    # Signals
    interval_changed = pyqtSignal(object)  # TimeInterval or None

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.current_interval: TimeInterval | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Start time
        self.start_spinbox = QDoubleSpinBox()
        self.start_spinbox.setRange(-999999.0, 999999.0)
        self.start_spinbox.setDecimals(2)
        self.start_spinbox.setSuffix(" s")
        self.start_spinbox.valueChanged.connect(self._update_interval)
        layout.addWidget(QLabel("Start:"))
        layout.addWidget(self.start_spinbox)

        # End time
        self.end_spinbox = QDoubleSpinBox()
        self.end_spinbox.setRange(-999999.0, 999999.0)
        self.end_spinbox.setDecimals(2)
        self.end_spinbox.setSuffix(" s")
        self.end_spinbox.valueChanged.connect(self._update_interval)
        layout.addWidget(QLabel("End:"))
        layout.addWidget(self.end_spinbox)

        # Enable checkbox
        self.enabled_checkbox = QCheckBox("Enabled")
        self.enabled_checkbox.stateChanged.connect(self._update_interval)
        layout.addWidget(self.enabled_checkbox)

    def _update_interval(self):
        """Atualiza intervalo e emite sinal"""
        if self.enabled_checkbox.isChecked():
            self.current_interval = TimeInterval(
                start=self.start_spinbox.value(),
                end=self.end_spinbox.value(),
            )
        else:
            self.current_interval = None

        self.interval_changed.emit(self.current_interval)

    def get_interval(self) -> TimeInterval | None:
        """Retorna intervalo atual"""
        return self.current_interval

    def set_interval(self, interval: TimeInterval | None):
        """Define intervalo"""
        if interval:
            self.start_spinbox.setValue(interval.start)
            self.end_spinbox.setValue(interval.end)
            self.enabled_checkbox.setChecked(True)
            self.current_interval = interval
        else:
            self.enabled_checkbox.setChecked(False)
            self.current_interval = None


class ValuePredicateWidget(QWidget):
    """Widget para configurar predicado de valor"""

    # Signals
    predicate_changed = pyqtSignal(str, object)  # series_id, ValuePredicate or None

    def __init__(self, series_id: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.series_id = series_id
        self.current_predicate: ValuePredicate | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Series name
        self.series_label = QLabel(self.series_id)
        self.series_label.setMinimumWidth(100)
        layout.addWidget(self.series_label)

        # Operator
        self.operator_combo = QComboBox()
        self.operator_combo.addItems([">", "<", ">=", "<=", "==", "!="])
        self.operator_combo.currentTextChanged.connect(self._update_predicate)
        layout.addWidget(self.operator_combo)

        # Value
        self.value_spinbox = QDoubleSpinBox()
        self.value_spinbox.setRange(-999999.0, 999999.0)
        self.value_spinbox.setDecimals(3)
        self.value_spinbox.valueChanged.connect(self._update_predicate)
        layout.addWidget(self.value_spinbox)

        # Enable checkbox
        self.enabled_checkbox = QCheckBox("Enabled")
        self.enabled_checkbox.stateChanged.connect(self._update_predicate)
        layout.addWidget(self.enabled_checkbox)

    def _update_predicate(self):
        """Atualiza predicado e emite sinal"""
        if self.enabled_checkbox.isChecked():
            self.current_predicate = ValuePredicate(
                series_id=SeriesID(self.series_id),
                operator=self.operator_combo.currentText(),
                value=self.value_spinbox.value(),
            )
        else:
            self.current_predicate = None

        self.predicate_changed.emit(self.series_id, self.current_predicate)

    def get_predicate(self) -> ValuePredicate | None:
        """Retorna predicado atual"""
        return self.current_predicate

    def set_predicate(self, predicate: ValuePredicate | None):
        """Define predicado"""
        if predicate:
            self.operator_combo.setCurrentText(predicate.operator)
            self.value_spinbox.setValue(predicate.value)
            self.enabled_checkbox.setChecked(True)
            self.current_predicate = predicate
        else:
            self.enabled_checkbox.setChecked(False)
            self.current_predicate = None


class StreamFiltersWidget(QWidget):
    """
    Widget principal para configuração de filtros de streaming conforme seção 11.2

    Features:
    - Filtros temporais de inclusão/exclusão
    - Filtros de amostragem configuráveis
    - Filtros de qualidade
    - Filtros de valor por série
    - Filtros visuais
    """

    # Signals
    filters_changed = pyqtSignal(object)  # StreamFilters

    def __init__(self, available_series: list[str] | None = None, parent: QWidget | None = None):
        super().__init__(parent)

        self.available_series = available_series or []
        self.current_filters = StreamFilters()

        # Widgets para intervalos temporais
        self.time_include_widgets: list[TimeIntervalWidget] = []
        self.time_exclude_widgets: list[TimeIntervalWidget] = []

        # Widgets para predicados de valor
        self.value_predicate_widgets: dict[str, ValuePredicateWidget] = {}

        self._setup_ui()
        self._setup_connections()

        logger.debug("stream_filters_widget_initialized",
                    n_series=len(self.available_series))

    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Create scrollable area for filters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Tab widget for different filter categories
        self.tabs = QTabWidget()

        # 1) Temporal filters tab
        self._create_temporal_tab()

        # 2) Sampling filters tab
        self._create_sampling_tab()

        # 3) Quality filters tab
        self._create_quality_tab()

        # 4) Value filters tab
        self._create_value_tab()

        # 5) Visual filters tab
        self._create_visual_tab()

        content_layout.addWidget(self.tabs)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.reset_button = QPushButton("Reset All")
        self.reset_button.clicked.connect(self._reset_filters)
        buttons_layout.addWidget(self.reset_button)

        self.apply_button = QPushButton("Apply Filters")
        self.apply_button.clicked.connect(self._apply_filters)
        self.apply_button.setDefault(True)
        buttons_layout.addWidget(self.apply_button)

        content_layout.addLayout(buttons_layout)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _create_temporal_tab(self):
        """Cria aba de filtros temporais"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Time include section
        include_group = QGroupBox("Time Include (only these intervals)")
        include_layout = QVBoxLayout(include_group)

        self.time_include_list = QWidget()
        self.time_include_list_layout = QVBoxLayout(self.time_include_list)
        include_layout.addWidget(self.time_include_list)

        include_buttons = QHBoxLayout()
        add_include_btn = QPushButton("Add Include Interval")
        add_include_btn.clicked.connect(self._add_time_include_interval)
        include_buttons.addWidget(add_include_btn)
        include_buttons.addStretch()
        include_layout.addLayout(include_buttons)

        layout.addWidget(include_group)

        # Time exclude section
        exclude_group = QGroupBox("Time Exclude (skip these intervals)")
        exclude_layout = QVBoxLayout(exclude_group)

        self.time_exclude_list = QWidget()
        self.time_exclude_list_layout = QVBoxLayout(self.time_exclude_list)
        exclude_layout.addWidget(self.time_exclude_list)

        exclude_buttons = QHBoxLayout()
        add_exclude_btn = QPushButton("Add Exclude Interval")
        add_exclude_btn.clicked.connect(self._add_time_exclude_interval)
        exclude_buttons.addWidget(add_exclude_btn)
        exclude_buttons.addStretch()
        exclude_layout.addLayout(exclude_buttons)

        layout.addWidget(exclude_group)

        layout.addStretch()
        self.tabs.addTab(tab, "Temporal")

    def _create_sampling_tab(self):
        """Cria aba de filtros de amostragem"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Max points per window
        self.max_points_spinbox = QSpinBox()
        self.max_points_spinbox.setRange(100, 100000)
        self.max_points_spinbox.setValue(5000)
        layout.addRow("Max Points Per Window:", self.max_points_spinbox)

        # Downsampling method
        self.downsample_combo = QComboBox()
        self.downsample_combo.addItems(["lttb", "minmax", "adaptive"])
        layout.addRow("Downsampling Method:", self.downsample_combo)

        self.tabs.addTab(tab, "Sampling")

    def _create_quality_tab(self):
        """Cria aba de filtros de qualidade"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Hide interpolated
        self.hide_interpolated_checkbox = QCheckBox("Hide interpolated points")
        layout.addRow("Interpolation:", self.hide_interpolated_checkbox)

        # Hide NaN
        self.hide_nan_checkbox = QCheckBox("Hide NaN values")
        self.hide_nan_checkbox.setChecked(True)
        layout.addRow("NaN Handling:", self.hide_nan_checkbox)

        # Quality threshold
        quality_layout = QHBoxLayout()
        self.quality_threshold_checkbox = QCheckBox("Enable")
        self.quality_threshold_spinbox = QDoubleSpinBox()
        self.quality_threshold_spinbox.setRange(0.0, 1.0)
        self.quality_threshold_spinbox.setDecimals(3)
        self.quality_threshold_spinbox.setValue(0.5)
        self.quality_threshold_spinbox.setEnabled(False)

        self.quality_threshold_checkbox.stateChanged.connect(
            lambda state: self.quality_threshold_spinbox.setEnabled(
                state == Qt.CheckState.Checked.value,
            ),
        )

        quality_layout.addWidget(self.quality_threshold_checkbox)
        quality_layout.addWidget(self.quality_threshold_spinbox)
        quality_layout.addStretch()

        layout.addRow("Quality Threshold:", quality_layout)

        self.tabs.addTab(tab, "Quality")

    def _create_value_tab(self):
        """Cria aba de filtros de valor"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Value predicates section
        group = QGroupBox("Value Predicates (conditional filtering)")
        group_layout = QVBoxLayout(group)

        # Scroll area for predicates
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.predicates_widget = QWidget()
        self.predicates_layout = QVBoxLayout(self.predicates_widget)

        # Create predicate widgets for each series
        for series_id in self.available_series:
            predicate_widget = ValuePredicateWidget(series_id)
            predicate_widget.predicate_changed.connect(self._on_predicate_changed)
            self.value_predicate_widgets[series_id] = predicate_widget
            self.predicates_layout.addWidget(predicate_widget)

        scroll.setWidget(self.predicates_widget)
        group_layout.addWidget(scroll)

        layout.addWidget(group)

        self.tabs.addTab(tab, "Value")

    def _create_visual_tab(self):
        """Cria aba de filtros visuais"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Visual smoothing section
        smoothing_group = QGroupBox("Visual Smoothing (render-only)")
        smoothing_layout = QFormLayout(smoothing_group)

        # Enable smoothing
        smoothing_enable_layout = QHBoxLayout()
        self.smoothing_enabled_checkbox = QCheckBox("Enable visual smoothing")
        smoothing_enable_layout.addWidget(self.smoothing_enabled_checkbox)
        smoothing_enable_layout.addStretch()
        smoothing_layout.addRow("", smoothing_enable_layout)

        # Smoothing method
        self.smoothing_method_combo = QComboBox()
        self.smoothing_method_combo.addItems([
            "savitzky_golay", "gaussian", "median", "lowpass",
        ])
        self.smoothing_method_combo.setEnabled(False)
        smoothing_layout.addRow("Method:", self.smoothing_method_combo)

        # Window size
        self.smoothing_window_spinbox = QSpinBox()
        self.smoothing_window_spinbox.setRange(3, 101)
        self.smoothing_window_spinbox.setValue(5)
        self.smoothing_window_spinbox.setSingleStep(2)
        self.smoothing_window_spinbox.setEnabled(False)
        smoothing_layout.addRow("Window Size:", self.smoothing_window_spinbox)

        # Sigma (for gaussian)
        self.smoothing_sigma_spinbox = QDoubleSpinBox()
        self.smoothing_sigma_spinbox.setRange(0.1, 10.0)
        self.smoothing_sigma_spinbox.setValue(1.0)
        self.smoothing_sigma_spinbox.setEnabled(False)
        smoothing_layout.addRow("Sigma:", self.smoothing_sigma_spinbox)

        # Connect enable checkbox
        self.smoothing_enabled_checkbox.stateChanged.connect(self._on_smoothing_enabled_changed)

        layout.addWidget(smoothing_group)

        # Hidden series section
        hidden_group = QGroupBox("Hidden Series")
        hidden_layout = QVBoxLayout(hidden_group)

        self.hidden_series_list = QListWidget()
        self.hidden_series_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        for series_id in self.available_series:
            item = QListWidgetItem(series_id)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.hidden_series_list.addItem(item)

        hidden_layout.addWidget(self.hidden_series_list)

        layout.addWidget(hidden_group)

        layout.addStretch()
        self.tabs.addTab(tab, "Visual")

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Connect all input widgets to update filters
        widgets_to_connect = [
            self.max_points_spinbox, self.downsample_combo,
            self.hide_interpolated_checkbox, self.hide_nan_checkbox,
            self.quality_threshold_checkbox, self.quality_threshold_spinbox,
            self.smoothing_enabled_checkbox, self.smoothing_method_combo,
            self.smoothing_window_spinbox, self.smoothing_sigma_spinbox,
            self.hidden_series_list,
        ]

        for widget in widgets_to_connect:
            if hasattr(widget, "valueChanged"):
                widget.valueChanged.connect(self._update_filters)
            elif hasattr(widget, "stateChanged"):
                widget.stateChanged.connect(self._update_filters)
            elif hasattr(widget, "currentTextChanged"):
                widget.currentTextChanged.connect(self._update_filters)
            elif hasattr(widget, "itemChanged"):
                widget.itemChanged.connect(self._update_filters)

    @pyqtSlot(int)
    def _on_smoothing_enabled_changed(self, state: int):
        """Habilita/desabilita controles de smoothing"""
        enabled = state == Qt.CheckState.Checked.value

        self.smoothing_method_combo.setEnabled(enabled)
        self.smoothing_window_spinbox.setEnabled(enabled)
        self.smoothing_sigma_spinbox.setEnabled(enabled)

        self._update_filters()

    @pyqtSlot(str, object)
    def _on_predicate_changed(self, series_id: str, predicate: ValuePredicate | None):
        """Callback quando predicado de valor é alterado"""
        self._update_filters()

    @pyqtSlot()
    def _add_time_include_interval(self):
        """Adiciona novo intervalo de inclusão temporal"""
        widget = TimeIntervalWidget()
        widget.interval_changed.connect(self._update_filters)

        # Add remove button
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(widget)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self._remove_time_interval(container, self.time_include_widgets, widget))
        layout.addWidget(remove_btn)

        self.time_include_widgets.append(widget)
        self.time_include_list_layout.addWidget(container)

    @pyqtSlot()
    def _add_time_exclude_interval(self):
        """Adiciona novo intervalo de exclusão temporal"""
        widget = TimeIntervalWidget()
        widget.interval_changed.connect(self._update_filters)

        # Add remove button
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(widget)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self._remove_time_interval(container, self.time_exclude_widgets, widget))
        layout.addWidget(remove_btn)

        self.time_exclude_widgets.append(widget)
        self.time_exclude_list_layout.addWidget(container)

    def _remove_time_interval(self, container: QWidget, widget_list: list, interval_widget):
        """Remove intervalo temporal"""
        widget_list.remove(interval_widget)
        container.setParent(None)
        self._update_filters()

    def _update_filters(self):
        """Atualiza filtros baseado nos controles"""
        # Time intervals
        time_include = []
        for widget in self.time_include_widgets:
            interval = widget.get_interval()
            if interval:
                time_include.append(interval)

        time_exclude = []
        for widget in self.time_exclude_widgets:
            interval = widget.get_interval()
            if interval:
                time_exclude.append(interval)

        # Sampling filters
        max_points = self.max_points_spinbox.value()
        downsample_method = self.downsample_combo.currentText()

        # Quality filters
        hide_interpolated = self.hide_interpolated_checkbox.isChecked()
        hide_nan = self.hide_nan_checkbox.isChecked()
        quality_threshold = None
        if self.quality_threshold_checkbox.isChecked():
            quality_threshold = self.quality_threshold_spinbox.value()

        # Value predicates
        value_predicates = {}
        for series_id, widget in self.value_predicate_widgets.items():
            predicate = widget.get_predicate()
            if predicate:
                value_predicates[SeriesID(series_id)] = predicate

        # Visual smoothing
        visual_smoothing = None
        if self.smoothing_enabled_checkbox.isChecked():
            visual_smoothing = SmoothConfig(
                method=self.smoothing_method_combo.currentText(),
                window=self.smoothing_window_spinbox.value(),
                sigma=self.smoothing_sigma_spinbox.value() if self.smoothing_method_combo.currentText() == "gaussian" else None,
            )

        # Hidden series
        hidden_series = []
        for i in range(self.hidden_series_list.count()):
            item = self.hidden_series_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                hidden_series.append(SeriesID(item.text()))

        # Create updated filters
        self.current_filters = StreamFilters(
            time_include=time_include if time_include else None,
            time_exclude=time_exclude if time_exclude else None,
            max_points_per_window=max_points,
            downsample_method=downsample_method,
            hide_interpolated=hide_interpolated,
            hide_nan=hide_nan,
            quality_threshold=quality_threshold,
            value_predicates=value_predicates,
            visual_smoothing=visual_smoothing,
            hidden_series=hidden_series,
        )

        logger.debug("stream_filters_updated",
                    time_include_count=len(time_include),
                    time_exclude_count=len(time_exclude),
                    value_predicates_count=len(value_predicates),
                    hidden_series_count=len(hidden_series))

    @pyqtSlot()
    def _reset_filters(self):
        """Reset all filters to default"""
        # Reset temporal intervals
        for widget in self.time_include_widgets[:]:
            widget.setParent(None)
        self.time_include_widgets.clear()

        for widget in self.time_exclude_widgets[:]:
            widget.setParent(None)
        self.time_exclude_widgets.clear()

        # Reset sampling
        self.max_points_spinbox.setValue(5000)
        self.downsample_combo.setCurrentText("lttb")

        # Reset quality
        self.hide_interpolated_checkbox.setChecked(False)
        self.hide_nan_checkbox.setChecked(True)
        self.quality_threshold_checkbox.setChecked(False)

        # Reset value predicates
        for widget in self.value_predicate_widgets.values():
            widget.set_predicate(None)

        # Reset visual
        self.smoothing_enabled_checkbox.setChecked(False)

        # Reset hidden series
        for i in range(self.hidden_series_list.count()):
            item = self.hidden_series_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

        # Update filters
        self._update_filters()

        logger.info("stream_filters_reset")

    @pyqtSlot()
    def _apply_filters(self):
        """Apply current filters and emit signal"""
        self.filters_changed.emit(self.current_filters)

        logger.info("stream_filters_applied",
                   time_include=len(self.current_filters.time_include or []),
                   time_exclude=len(self.current_filters.time_exclude or []),
                   max_points=self.current_filters.max_points_per_window)

    def get_filters(self) -> StreamFilters:
        """Retorna filtros atuais"""
        return self.current_filters

    def set_filters(self, filters: StreamFilters):
        """Define filtros"""
        self.current_filters = filters

        # Update UI to reflect filters
        # This is a simplified implementation - full implementation would
        # restore all UI state from the filters object
        self.max_points_spinbox.setValue(filters.max_points_per_window)
        self.downsample_combo.setCurrentText(filters.downsample_method)
        self.hide_interpolated_checkbox.setChecked(filters.hide_interpolated)
        self.hide_nan_checkbox.setChecked(filters.hide_nan)

        logger.debug("stream_filters_set", filters=str(filters))

    def update_available_series(self, series_list: list[str]):
        """Atualiza lista de séries disponíveis"""
        self.available_series = series_list

        # Rebuild value predicates
        for widget in self.value_predicate_widgets.values():
            widget.setParent(None)
        self.value_predicate_widgets.clear()

        for series_id in self.available_series:
            predicate_widget = ValuePredicateWidget(series_id)
            predicate_widget.predicate_changed.connect(self._on_predicate_changed)
            self.value_predicate_widgets[series_id] = predicate_widget
            self.predicates_layout.addWidget(predicate_widget)

        # Rebuild hidden series list
        self.hidden_series_list.clear()
        for series_id in self.available_series:
            item = QListWidgetItem(series_id)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.hidden_series_list.addItem(item)

        logger.info("stream_filters_series_updated", n_series=len(series_list))

# =============================================================================
# Signal Processing Filters
# =============================================================================

class StreamFilter:
    """
    Base class for signal processing filters.
    
    All filter classes should inherit from this and implement
    the apply() method.
    """

    def __init__(self, fs: float = 1000.0):
        """
        Initialize filter.
        
        Args:
            fs: Sampling frequency in Hz
        """
        self.fs = fs
        self._coefficients = None

    def apply(self, data: "np.ndarray") -> "np.ndarray":
        """
        Apply filter to data.
        
        Args:
            data: Input signal array (1D numpy array of float values)
            
        Returns:
            Filtered signal array (same shape as input)
        
        Note:
            Subclasses (LowpassFilter, HighpassFilter, BandpassFilter, etc.)
            must override this method with specific filter implementations.
            Base implementation returns data unchanged.
        
        Example (subclass):
            def apply(self, data: np.ndarray) -> np.ndarray:
                if self._coefficients is None:
                    return data
                b, a = self._coefficients
                return scipy.signal.filtfilt(b, a, data)
        """
        # Base implementation: return data unchanged (passthrough)
        import numpy as np
        return np.asarray(data)

    def reset(self):
        """Reset filter state.
        
        Clears any internal state (coefficients, buffers) and 
        re-designs the filter. Useful when changing filter parameters
        or switching between data streams.
        """
        self._coefficients = None

    def get_frequency_response(self, n_points: int = 512) -> tuple["np.ndarray", "np.ndarray"]:
        """
        Get frequency response of filter.
        
        Args:
            n_points: Number of frequency points
            
        Returns:
            Tuple of (frequencies, magnitude response)
        """
        try:
            import numpy as np
            from scipy import signal as scipy_signal

            if self._coefficients is not None:
                b, a = self._coefficients
                w, h = scipy_signal.freqz(b, a, worN=n_points)
                freq = w * self.fs / (2 * np.pi)
                return freq, np.abs(h)
        except ImportError:
            pass

        import numpy as np
        return np.linspace(0, self.fs/2, n_points), np.ones(n_points)


class LowpassFilter(StreamFilter):
    """
    Butterworth lowpass filter.
    
    Attenuates frequencies above the cutoff frequency.
    """

    def __init__(self, cutoff: float, fs: float = 1000.0, order: int = 4):
        """
        Initialize lowpass filter.
        
        Args:
            cutoff: Cutoff frequency in Hz
            fs: Sampling frequency in Hz
            order: Filter order
        """
        super().__init__(fs)
        self.cutoff = cutoff
        self.order = order
        self._design_filter()

    def _design_filter(self):
        """Design the filter coefficients."""
        try:
            from scipy import signal as scipy_signal

            nyq = self.fs / 2
            normalized_cutoff = self.cutoff / nyq

            # Ensure cutoff is valid
            if normalized_cutoff >= 1:
                normalized_cutoff = 0.99
            elif normalized_cutoff <= 0:
                normalized_cutoff = 0.01

            self._coefficients = scipy_signal.butter(
                self.order, normalized_cutoff, btype='low'
            )
        except ImportError:
            self._coefficients = None

    def apply(self, data: "np.ndarray") -> "np.ndarray":
        """
        Apply lowpass filter to data.
        
        Args:
            data: Input signal array
            
        Returns:
            Filtered signal array
        """
        import numpy as np

        if self._coefficients is None:
            return data

        try:
            from scipy import signal as scipy_signal

            b, a = self._coefficients
            # Use filtfilt for zero-phase filtering
            filtered = scipy_signal.filtfilt(b, a, data)
            return filtered
        except (ImportError, ValueError):
            return data


class HighpassFilter(StreamFilter):
    """
    Butterworth highpass filter.
    
    Attenuates frequencies below the cutoff frequency.
    """

    def __init__(self, cutoff: float, fs: float = 1000.0, order: int = 4):
        """
        Initialize highpass filter.
        
        Args:
            cutoff: Cutoff frequency in Hz
            fs: Sampling frequency in Hz
            order: Filter order
        """
        super().__init__(fs)
        self.cutoff = cutoff
        self.order = order
        self._design_filter()

    def _design_filter(self):
        """Design the filter coefficients."""
        try:
            from scipy import signal as scipy_signal

            nyq = self.fs / 2
            normalized_cutoff = self.cutoff / nyq

            # Ensure cutoff is valid
            if normalized_cutoff >= 1:
                normalized_cutoff = 0.99
            elif normalized_cutoff <= 0:
                normalized_cutoff = 0.01

            self._coefficients = scipy_signal.butter(
                self.order, normalized_cutoff, btype='high'
            )
        except ImportError:
            self._coefficients = None

    def apply(self, data: "np.ndarray") -> "np.ndarray":
        """
        Apply highpass filter to data.
        
        Args:
            data: Input signal array
            
        Returns:
            Filtered signal array
        """
        import numpy as np

        if self._coefficients is None:
            return data

        try:
            from scipy import signal as scipy_signal

            b, a = self._coefficients
            # Use filtfilt for zero-phase filtering
            filtered = scipy_signal.filtfilt(b, a, data)
            return filtered
        except (ImportError, ValueError):
            return data


class BandpassFilter(StreamFilter):
    """
    Butterworth bandpass filter.
    
    Passes frequencies within a specified range.
    """

    def __init__(self, low_cutoff: float, high_cutoff: float, fs: float = 1000.0, order: int = 4):
        """
        Initialize bandpass filter.
        
        Args:
            low_cutoff: Low cutoff frequency in Hz
            high_cutoff: High cutoff frequency in Hz
            fs: Sampling frequency in Hz
            order: Filter order
        """
        super().__init__(fs)
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff
        self.order = order
        self._design_filter()

    def _design_filter(self):
        """Design the filter coefficients."""
        try:
            from scipy import signal as scipy_signal

            nyq = self.fs / 2
            low = self.low_cutoff / nyq
            high = self.high_cutoff / nyq

            # Ensure cutoffs are valid
            low = max(0.01, min(0.98, low))
            high = max(low + 0.01, min(0.99, high))

            self._coefficients = scipy_signal.butter(
                self.order, [low, high], btype='band'
            )
        except ImportError:
            self._coefficients = None

    def apply(self, data: "np.ndarray") -> "np.ndarray":
        """
        Apply bandpass filter to data.
        
        Args:
            data: Input signal array
            
        Returns:
            Filtered signal array
        """
        if self._coefficients is None:
            return data

        try:
            from scipy import signal as scipy_signal

            b, a = self._coefficients
            filtered = scipy_signal.filtfilt(b, a, data)
            return filtered
        except (ImportError, ValueError):
            return data


class NotchFilter(StreamFilter):
    """
    Notch (band-stop) filter.
    
    Removes a specific frequency from the signal.
    Commonly used to remove 50Hz/60Hz powerline interference.
    """

    def __init__(self, freq: float, q: float = 30.0, fs: float = 1000.0):
        """
        Initialize notch filter.
        
        Args:
            freq: Notch frequency in Hz
            q: Quality factor (higher = narrower notch)
            fs: Sampling frequency in Hz
        """
        super().__init__(fs)
        self.freq = freq
        self.q = q
        self._design_filter()

    def _design_filter(self):
        """Design the filter coefficients."""
        try:
            from scipy import signal as scipy_signal

            nyq = self.fs / 2
            normalized_freq = self.freq / nyq

            # Ensure frequency is valid
            if normalized_freq >= 1:
                normalized_freq = 0.99
            elif normalized_freq <= 0:
                normalized_freq = 0.01

            self._coefficients = scipy_signal.iirnotch(
                normalized_freq, self.q
            )
        except ImportError:
            self._coefficients = None

    def apply(self, data: "np.ndarray") -> "np.ndarray":
        """
        Apply notch filter to data.
        
        Args:
            data: Input signal array
            
        Returns:
            Filtered signal array
        """
        if self._coefficients is None:
            return data

        try:
            from scipy import signal as scipy_signal

            b, a = self._coefficients
            filtered = scipy_signal.filtfilt(b, a, data)
            return filtered
        except (ImportError, ValueError):
            return data


class MovingAverageFilter(StreamFilter):
    """
    Moving average filter for smoothing.
    
    Simple FIR filter that computes the average of N consecutive samples.
    """

    def __init__(self, window_size: int = 5, fs: float = 1000.0):
        """
        Initialize moving average filter.
        
        Args:
            window_size: Number of samples to average
            fs: Sampling frequency in Hz
        """
        super().__init__(fs)
        self.window_size = max(1, window_size)

    def apply(self, data: "np.ndarray") -> "np.ndarray":
        """
        Apply moving average filter to data.
        
        Args:
            data: Input signal array
            
        Returns:
            Filtered signal array
        """
        import numpy as np

        if len(data) < self.window_size:
            return data

        # Use convolution for efficient moving average
        kernel = np.ones(self.window_size) / self.window_size
        filtered = np.convolve(data, kernel, mode='same')

        return filtered


class FilterChain:
    """
    Chain of filters to be applied sequentially.
    
    Allows combining multiple filters into a single processing pipeline.
    """

    def __init__(self):
        """Initialize empty filter chain."""
        self._filters: list[StreamFilter] = []

    def add_filter(self, filter_obj: StreamFilter):
        """
        Add a filter to the chain.
        
        Args:
            filter_obj: Filter to add
        """
        self._filters.append(filter_obj)

    def remove_filter(self, index: int):
        """
        Remove a filter from the chain by index.
        
        Args:
            index: Index of filter to remove
        """
        if 0 <= index < len(self._filters):
            self._filters.pop(index)

    def clear(self):
        """Remove all filters from the chain."""
        self._filters.clear()

    def apply(self, data: "np.ndarray") -> "np.ndarray":
        """
        Apply all filters in the chain sequentially.
        
        Args:
            data: Input signal array
            
        Returns:
            Filtered signal array
        """
        result = data
        for filter_obj in self._filters:
            result = filter_obj.apply(result)
        return result

    def __len__(self) -> int:
        """Return number of filters in chain."""
        return len(self._filters)

    def __getitem__(self, index: int) -> StreamFilter:
        """Get filter by index."""
        return self._filters[index]

    @property
    def filters(self) -> list[StreamFilter]:
        """Return list of filters in chain."""
        return self._filters.copy()


class FilterDialog(QWidget, UiLoaderMixin):
    """
    Dialog for configuring signal processing filters.
    
    Provides UI for creating and configuring various filter types.
    """

    UI_FILE = "desktop/ui_files/filterDialog.ui"

    # Signals
    filter_created = pyqtSignal(object)  # StreamFilter
    filter_applied = pyqtSignal(object)  # filtered data

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Filter Configuration")

        self._current_filter: StreamFilter | None = None
        if not self._load_ui():
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()

    def _setup_ui_from_file(self):
        """Configura widgets após carregar .ui"""
        # Busca widgets do arquivo .ui
        self.filter_type_combo = self.findChild(QComboBox, "filter_type_combo")
        self.params_group = self.findChild(QGroupBox, "params_group")
        self.fs_spinbox = self.findChild(QDoubleSpinBox, "fs_spinbox")
        self.cutoff_spinbox = self.findChild(QDoubleSpinBox, "cutoff_spinbox")
        self.high_cutoff_spinbox = self.findChild(QDoubleSpinBox, "high_cutoff_spinbox")
        self.q_spinbox = self.findChild(QDoubleSpinBox, "q_spinbox")
        self.window_spinbox = self.findChild(QSpinBox, "window_spinbox")
        self.order_spinbox = self.findChild(QSpinBox, "order_spinbox")
        self.preview_button = self.findChild(QPushButton, "preview_button")
        self.create_button = self.findChild(QPushButton, "create_button")
        
        # Conecta sinais
        if self.filter_type_combo:
            self.filter_type_combo.currentTextChanged.connect(self._on_filter_type_changed)
        if self.preview_button:
            self.preview_button.clicked.connect(self._on_preview)
        if self.create_button:
            self.create_button.clicked.connect(self._on_create)
        
        # Initialize visibility
        if self.filter_type_combo:
            self._on_filter_type_changed(self.filter_type_combo.currentText())

    def _setup_ui_fallback(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Filter type selection
        type_group = QGroupBox("Filter Type")
        type_layout = QFormLayout(type_group)

        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems([
            "Lowpass",
            "Highpass",
            "Bandpass",
            "Notch",
            "Moving Average"
        ])
        self.filter_type_combo.currentTextChanged.connect(self._on_filter_type_changed)
        type_layout.addRow("Type:", self.filter_type_combo)

        layout.addWidget(type_group)

        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QFormLayout(self.params_group)

        # Sampling frequency
        self.fs_spinbox = QDoubleSpinBox()
        self.fs_spinbox.setRange(1.0, 100000.0)
        self.fs_spinbox.setValue(1000.0)
        self.fs_spinbox.setSuffix(" Hz")
        self.params_layout.addRow("Sampling Frequency:", self.fs_spinbox)

        # Cutoff frequency
        self.cutoff_spinbox = QDoubleSpinBox()
        self.cutoff_spinbox.setRange(0.1, 50000.0)
        self.cutoff_spinbox.setValue(10.0)
        self.cutoff_spinbox.setSuffix(" Hz")
        self.params_layout.addRow("Cutoff Frequency:", self.cutoff_spinbox)

        # High cutoff (for bandpass)
        self.high_cutoff_spinbox = QDoubleSpinBox()
        self.high_cutoff_spinbox.setRange(0.1, 50000.0)
        self.high_cutoff_spinbox.setValue(100.0)
        self.high_cutoff_spinbox.setSuffix(" Hz")
        self.high_cutoff_spinbox.setVisible(False)
        self.params_layout.addRow("High Cutoff:", self.high_cutoff_spinbox)

        # Q factor (for notch)
        self.q_spinbox = QDoubleSpinBox()
        self.q_spinbox.setRange(1.0, 100.0)
        self.q_spinbox.setValue(30.0)
        self.q_spinbox.setVisible(False)
        self.params_layout.addRow("Q Factor:", self.q_spinbox)

        # Window size (for moving average)
        self.window_spinbox = QSpinBox()
        self.window_spinbox.setRange(2, 1000)
        self.window_spinbox.setValue(5)
        self.window_spinbox.setVisible(False)
        self.params_layout.addRow("Window Size:", self.window_spinbox)

        # Order
        self.order_spinbox = QSpinBox()
        self.order_spinbox.setRange(1, 10)
        self.order_spinbox.setValue(4)
        self.params_layout.addRow("Filter Order:", self.order_spinbox)

        layout.addWidget(self.params_group)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self._on_preview)
        buttons_layout.addWidget(self.preview_button)

        self.create_button = QPushButton("Create Filter")
        self.create_button.clicked.connect(self._on_create)
        buttons_layout.addWidget(self.create_button)

        layout.addLayout(buttons_layout)

        # Initialize visibility
        self._on_filter_type_changed(self.filter_type_combo.currentText())

    def _on_filter_type_changed(self, filter_type: str):
        """Update UI based on selected filter type."""
        # Hide all optional fields first
        self.high_cutoff_spinbox.setVisible(False)
        self.q_spinbox.setVisible(False)
        self.window_spinbox.setVisible(False)
        self.cutoff_spinbox.setVisible(True)
        self.order_spinbox.setVisible(True)

        if filter_type == "Bandpass":
            self.high_cutoff_spinbox.setVisible(True)
        elif filter_type == "Notch":
            self.q_spinbox.setVisible(True)
            self.order_spinbox.setVisible(False)
        elif filter_type == "Moving Average":
            self.cutoff_spinbox.setVisible(False)
            self.order_spinbox.setVisible(False)
            self.window_spinbox.setVisible(True)

    def _on_preview(self):
        """Preview the filter."""
        self._create_filter()

    def _on_create(self):
        """Create and emit the filter."""
        self._create_filter()
        if self._current_filter is not None:
            self.filter_created.emit(self._current_filter)

    def _create_filter(self) -> StreamFilter | None:
        """Create filter based on current settings."""
        filter_type = self.filter_type_combo.currentText()
        fs = self.fs_spinbox.value()

        if filter_type == "Lowpass":
            self._current_filter = LowpassFilter(
                cutoff=self.cutoff_spinbox.value(),
                fs=fs,
                order=self.order_spinbox.value()
            )
        elif filter_type == "Highpass":
            self._current_filter = HighpassFilter(
                cutoff=self.cutoff_spinbox.value(),
                fs=fs,
                order=self.order_spinbox.value()
            )
        elif filter_type == "Bandpass":
            self._current_filter = BandpassFilter(
                low_cutoff=self.cutoff_spinbox.value(),
                high_cutoff=self.high_cutoff_spinbox.value(),
                fs=fs,
                order=self.order_spinbox.value()
            )
        elif filter_type == "Notch":
            self._current_filter = NotchFilter(
                freq=self.cutoff_spinbox.value(),
                q=self.q_spinbox.value(),
                fs=fs
            )
        elif filter_type == "Moving Average":
            self._current_filter = MovingAverageFilter(
                window_size=self.window_spinbox.value(),
                fs=fs
            )

        return self._current_filter

    def get_filter(self) -> StreamFilter | None:
        """Return the currently configured filter."""
        return self._current_filter

    def set_filter(self, filter_obj: StreamFilter):
        """Set filter and update UI."""
        self._current_filter = filter_obj

        # Update UI based on filter type
        if isinstance(filter_obj, LowpassFilter):
            self.filter_type_combo.setCurrentText("Lowpass")
            self.cutoff_spinbox.setValue(filter_obj.cutoff)
            self.order_spinbox.setValue(filter_obj.order)
        elif isinstance(filter_obj, HighpassFilter):
            self.filter_type_combo.setCurrentText("Highpass")
            self.cutoff_spinbox.setValue(filter_obj.cutoff)
            self.order_spinbox.setValue(filter_obj.order)
        elif isinstance(filter_obj, BandpassFilter):
            self.filter_type_combo.setCurrentText("Bandpass")
            self.cutoff_spinbox.setValue(filter_obj.low_cutoff)
            self.high_cutoff_spinbox.setValue(filter_obj.high_cutoff)
            self.order_spinbox.setValue(filter_obj.order)
        elif isinstance(filter_obj, NotchFilter):
            self.filter_type_combo.setCurrentText("Notch")
            self.cutoff_spinbox.setValue(filter_obj.freq)
            self.q_spinbox.setValue(filter_obj.q)
        elif isinstance(filter_obj, MovingAverageFilter):
            self.filter_type_combo.setCurrentText("Moving Average")
            self.window_spinbox.setValue(filter_obj.window_size)

        self.fs_spinbox.setValue(filter_obj.fs)