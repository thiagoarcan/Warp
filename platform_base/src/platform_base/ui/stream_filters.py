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
