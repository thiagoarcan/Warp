"""
Selection Widgets - Widgets de interface para sistema de seleção completo

Features:
- Range picker temporal
- Seleção interativa (brush, lasso)  
- Query builder para seleções condicionais
- Sincronização entre views
- Histórico de seleções
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Callable, Tuple
import numpy as np
from dataclasses import dataclass
import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QFormLayout, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QLabel, QLineEdit, QTextEdit, QSlider, QFrame,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QProgressBar, QSplitter, QScrollArea,
    QDateTimeEdit, QCalendarWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QDateTime, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QBrush

try:
    import pyqtgraph as pg
    from pyqtgraph import PlotWidget, LinearRegionItem, InfiniteLine
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False

from platform_base.core.models import Dataset, Series, SeriesID
from platform_base.ui.selection import DataSelector, Selection, SelectionMode, SelectionCriteria
from platform_base.ui.state import SessionState
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class RangePickerWidget(QWidget):
    """Widget para seleção temporal com range picker"""
    
    # Signals
    range_selected = pyqtSignal(float, float)  # start_time, end_time
    range_changed = pyqtSignal(float, float)   # start_time, end_time (during drag)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.current_dataset: Optional[Dataset] = None
        self.range_item: Optional[LinearRegionItem] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Start time
        controls_layout.addWidget(QLabel("Start:"))
        self.start_spinbox = QDoubleSpinBox()
        self.start_spinbox.setRange(-99999.0, 99999.0)
        self.start_spinbox.setDecimals(3)
        self.start_spinbox.setSuffix(" s")
        self.start_spinbox.valueChanged.connect(self._on_manual_range_change)
        controls_layout.addWidget(self.start_spinbox)
        
        # End time
        controls_layout.addWidget(QLabel("End:"))
        self.end_spinbox = QDoubleSpinBox()
        self.end_spinbox.setRange(-99999.0, 99999.0)
        self.end_spinbox.setDecimals(3)
        self.end_spinbox.setSuffix(" s")
        self.end_spinbox.valueChanged.connect(self._on_manual_range_change)
        controls_layout.addWidget(self.end_spinbox)
        
        # Select button
        self.select_button = QPushButton("Select Range")
        self.select_button.clicked.connect(self._emit_range_selected)
        controls_layout.addWidget(self.select_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Plot widget
        if PYQTGRAPH_AVAILABLE:
            self.plot_widget = PlotWidget()
            self.plot_widget.setLabel('left', 'Value')
            self.plot_widget.setLabel('bottom', 'Time (s)')
            layout.addWidget(self.plot_widget)
        else:
            placeholder = QLabel("PyQtGraph required for range picker")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
    
    def set_dataset(self, dataset: Dataset):
        """Define dataset para visualização"""
        self.current_dataset = dataset
        
        if not PYQTGRAPH_AVAILABLE or not dataset:
            return
        
        # Clear existing plots
        self.plot_widget.clear()
        
        # Plot first series as reference
        series_list = list(dataset.series.values())
        if series_list:
            first_series = series_list[0]
            self.plot_widget.plot(dataset.t_seconds, first_series.values, 
                                pen='b', alpha=0.7, name=first_series.name)
        
        # Add range selector
        if self.range_item:
            self.plot_widget.removeItem(self.range_item)
        
        # Set initial range to 10% of data
        t_min, t_max = dataset.t_seconds[0], dataset.t_seconds[-1]
        range_size = (t_max - t_min) * 0.1
        range_center = (t_min + t_max) * 0.5
        initial_range = [range_center - range_size/2, range_center + range_size/2]
        
        self.range_item = LinearRegionItem(initial_range, brush=(0, 100, 200, 50))
        self.range_item.sigRegionChanged.connect(self._on_range_changed)
        self.plot_widget.addItem(self.range_item)
        
        # Update spinboxes
        self.start_spinbox.setRange(t_min, t_max)
        self.end_spinbox.setRange(t_min, t_max)
        self.start_spinbox.setValue(initial_range[0])
        self.end_spinbox.setValue(initial_range[1])
    
    @pyqtSlot()
    def _on_range_changed(self):
        """Callback quando range visual muda"""
        if self.range_item:
            start, end = self.range_item.getRegion()
            
            # Update spinboxes without triggering signals
            self.start_spinbox.blockSignals(True)
            self.end_spinbox.blockSignals(True)
            self.start_spinbox.setValue(start)
            self.end_spinbox.setValue(end)
            self.start_spinbox.blockSignals(False)
            self.end_spinbox.blockSignals(False)
            
            self.range_changed.emit(start, end)
    
    @pyqtSlot()
    def _on_manual_range_change(self):
        """Callback quando range é alterado manualmente"""
        start = self.start_spinbox.value()
        end = self.end_spinbox.value()
        
        if start >= end:
            return
        
        if self.range_item:
            self.range_item.setRegion([start, end])
    
    @pyqtSlot()
    def _emit_range_selected(self):
        """Emite sinal de seleção finalizada"""
        start = self.start_spinbox.value()
        end = self.end_spinbox.value()
        
        if start >= end:
            QMessageBox.warning(self, "Invalid Range", "Start time must be less than end time.")
            return
        
        self.range_selected.emit(start, end)
        logger.info("range_selected", start=start, end=end)
    
    def get_current_range(self) -> Tuple[float, float]:
        """Retorna range atual"""
        return self.start_spinbox.value(), self.end_spinbox.value()


class BrushSelectionWidget(QWidget):
    """Widget para seleção interativa com brush"""
    
    # Signals
    points_selected = pyqtSignal(list)  # List of selected point indices
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.current_dataset: Optional[Dataset] = None
        self.selection_enabled = False
        self.selected_points = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.enable_selection_btn = QPushButton("Enable Selection")
        self.enable_selection_btn.setCheckable(True)
        self.enable_selection_btn.clicked.connect(self._toggle_selection)
        controls_layout.addWidget(self.enable_selection_btn)
        
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self._clear_selection)
        controls_layout.addWidget(self.clear_selection_btn)
        
        self.select_btn = QPushButton("Apply Selection")
        self.select_btn.clicked.connect(self._apply_selection)
        controls_layout.addWidget(self.select_btn)
        
        controls_layout.addStretch()
        
        self.selection_info = QLabel("0 points selected")
        controls_layout.addWidget(self.selection_info)
        
        layout.addLayout(controls_layout)
        
        # Plot widget
        if PYQTGRAPH_AVAILABLE:
            self.plot_widget = PlotWidget()
            self.plot_widget.setLabel('left', 'Value')
            self.plot_widget.setLabel('bottom', 'Time (s)')
            
            # Enable crosshair
            self.crosshair_v = InfiniteLine(angle=90, movable=False, pen='y')
            self.crosshair_h = InfiniteLine(angle=0, movable=False, pen='y')
            self.plot_widget.addItem(self.crosshair_v, ignoreBounds=True)
            self.plot_widget.addItem(self.crosshair_h, ignoreBounds=True)
            
            layout.addWidget(self.plot_widget)
        else:
            placeholder = QLabel("PyQtGraph required for brush selection")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
    
    def set_dataset(self, dataset: Dataset):
        """Define dataset para visualização"""
        self.current_dataset = dataset
        
        if not PYQTGRAPH_AVAILABLE or not dataset:
            return
        
        # Clear existing plots
        self.plot_widget.clear()
        self._clear_selection()
        
        # Plot all series
        colors = ['b', 'r', 'g', 'm', 'c', 'y']
        for i, (series_id, series) in enumerate(dataset.series.items()):
            color = colors[i % len(colors)]
            self.plot_widget.plot(dataset.t_seconds, series.values, 
                                pen=color, alpha=0.7, name=series.name)
    
    @pyqtSlot()
    def _toggle_selection(self):
        """Liga/desliga modo de seleção"""
        self.selection_enabled = self.enable_selection_btn.isChecked()
        
        if self.selection_enabled:
            self.enable_selection_btn.setText("Disable Selection")
            # Connect mouse events
            if PYQTGRAPH_AVAILABLE:
                self.plot_widget.scene().sigMouseClicked.connect(self._on_mouse_click)
        else:
            self.enable_selection_btn.setText("Enable Selection")
            # Disconnect mouse events
            if PYQTGRAPH_AVAILABLE:
                try:
                    self.plot_widget.scene().sigMouseClicked.disconnect(self._on_mouse_click)
                except:
                    pass
    
    def _on_mouse_click(self, event):
        """Callback para cliques do mouse"""
        if not self.selection_enabled or not self.current_dataset:
            return
        
        # Get click position in data coordinates
        pos = event.pos()
        if self.plot_widget.plotItem.vb.mapSceneToView(pos):
            view_pos = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            click_time = view_pos.x()
            
            # Find nearest time point
            time_diff = np.abs(self.current_dataset.t_seconds - click_time)
            nearest_idx = np.argmin(time_diff)
            
            # Toggle point selection
            if nearest_idx in self.selected_points:
                self.selected_points.remove(nearest_idx)
            else:
                self.selected_points.append(nearest_idx)
            
            self._update_selection_display()
    
    def _update_selection_display(self):
        """Atualiza visualização dos pontos selecionados"""
        self.selection_info.setText(f"{len(self.selected_points)} points selected")
        
        if not PYQTGRAPH_AVAILABLE or not self.current_dataset:
            return
        
        # Remove existing selection markers
        items_to_remove = []
        for item in self.plot_widget.plotItem.items:
            if hasattr(item, '_selection_marker'):
                items_to_remove.append(item)
        
        for item in items_to_remove:
            self.plot_widget.removeItem(item)
        
        # Add new selection markers
        for idx in self.selected_points:
            t = self.current_dataset.t_seconds[idx]
            
            # Draw vertical line at selected time
            line = InfiniteLine(pos=t, angle=90, pen={'color': 'red', 'width': 2})
            line._selection_marker = True  # Mark as selection item
            self.plot_widget.addItem(line)
    
    @pyqtSlot()
    def _clear_selection(self):
        """Limpa seleção atual"""
        self.selected_points.clear()
        self._update_selection_display()
    
    @pyqtSlot()
    def _apply_selection(self):
        """Aplica seleção atual"""
        self.points_selected.emit(self.selected_points.copy())
        logger.info("brush_selection_applied", n_points=len(self.selected_points))


class QueryBuilderWidget(QWidget):
    """Widget para construção de queries condicionais"""
    
    # Signals
    query_built = pyqtSignal(str, str)  # series_id, condition_string
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.available_series: List[str] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        
        # Series selection
        series_group = QGroupBox("Target Series")
        series_layout = QFormLayout(series_group)
        
        self.series_combo = QComboBox()
        series_layout.addRow("Series:", self.series_combo)
        
        layout.addWidget(series_group)
        
        # Condition builder
        condition_group = QGroupBox("Condition Builder")
        condition_layout = QVBoxLayout(condition_group)
        
        # Simple condition builder
        simple_layout = QFormLayout()
        
        self.operator_combo = QComboBox()
        self.operator_combo.addItems([">", "<", ">=", "<=", "==", "!="])
        simple_layout.addRow("Operator:", self.operator_combo)
        
        self.value_type_combo = QComboBox()
        self.value_type_combo.addItems(["Number", "Statistics", "Percentile"])
        self.value_type_combo.currentTextChanged.connect(self._on_value_type_changed)
        simple_layout.addRow("Value Type:", self.value_type_combo)
        
        # Value input (changes based on type)
        self.value_widget = QWidget()
        self.value_layout = QHBoxLayout(self.value_widget)
        self.value_layout.setContentsMargins(0, 0, 0, 0)
        
        self.number_input = QDoubleSpinBox()
        self.number_input.setRange(-999999.0, 999999.0)
        self.number_input.setDecimals(3)
        self.value_layout.addWidget(self.number_input)
        
        self.stats_combo = QComboBox()
        self.stats_combo.addItems(["mean", "std", "median", "min", "max"])
        self.stats_combo.setVisible(False)
        self.value_layout.addWidget(self.stats_combo)
        
        self.percentile_input = QSpinBox()
        self.percentile_input.setRange(0, 100)
        self.percentile_input.setValue(50)
        self.percentile_input.setSuffix("%")
        self.percentile_input.setVisible(False)
        self.value_layout.addWidget(self.percentile_input)
        
        simple_layout.addRow("Value:", self.value_widget)
        
        condition_layout.addLayout(simple_layout)
        
        # Advanced condition input
        advanced_group = QGroupBox("Advanced Condition (Raw)")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.condition_text = QLineEdit()
        self.condition_text.setPlaceholderText("e.g., > mean + 2*std")
        advanced_layout.addWidget(self.condition_text)
        
        condition_layout.addWidget(advanced_group)
        
        layout.addWidget(condition_group)
        
        # Preview and actions
        actions_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self._preview_condition)
        actions_layout.addWidget(self.preview_btn)
        
        self.apply_btn = QPushButton("Apply Condition")
        self.apply_btn.clicked.connect(self._apply_condition)
        actions_layout.addWidget(self.apply_btn)
        
        layout.addLayout(actions_layout)
        
        # Results preview
        self.results_label = QLabel("No condition applied")
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("border: 1px solid gray; padding: 8px; background: #f0f0f0;")
        layout.addWidget(self.results_label)
    
    def set_available_series(self, series_list: List[str]):
        """Define séries disponíveis"""
        self.available_series = series_list
        
        self.series_combo.clear()
        self.series_combo.addItems(series_list)
    
    @pyqtSlot(str)
    def _on_value_type_changed(self, value_type: str):
        """Callback quando tipo de valor muda"""
        # Hide all value inputs
        self.number_input.setVisible(False)
        self.stats_combo.setVisible(False)
        self.percentile_input.setVisible(False)
        
        # Show appropriate input
        if value_type == "Number":
            self.number_input.setVisible(True)
        elif value_type == "Statistics":
            self.stats_combo.setVisible(True)
        elif value_type == "Percentile":
            self.percentile_input.setVisible(True)
    
    def _build_condition_string(self) -> str:
        """Constrói string de condição baseada na UI"""
        if self.condition_text.text().strip():
            # Use advanced condition if provided
            return self.condition_text.text().strip()
        
        # Build from simple inputs
        operator = self.operator_combo.currentText()
        value_type = self.value_type_combo.currentText()
        
        if value_type == "Number":
            value = str(self.number_input.value())
        elif value_type == "Statistics":
            value = self.stats_combo.currentText()
        elif value_type == "Percentile":
            percentile = self.percentile_input.value()
            value = f"percentile_{percentile}"  # Would need to implement in evaluator
        else:
            value = "0"
        
        return f"{operator} {value}"
    
    @pyqtSlot()
    def _preview_condition(self):
        """Preview da condição"""
        series_id = self.series_combo.currentText()
        condition = self._build_condition_string()
        
        if not series_id or not condition:
            self.results_label.setText("Please select series and condition")
            return
        
        # Mock preview (would integrate with actual data)
        self.results_label.setText(f"Preview: {series_id} {condition}\n"
                                  f"Estimated matching points: ~25% of data")
    
    @pyqtSlot()
    def _apply_condition(self):
        """Aplica condição construída"""
        series_id = self.series_combo.currentText()
        condition = self._build_condition_string()
        
        if not series_id or not condition:
            QMessageBox.warning(self, "Incomplete Query", 
                              "Please select both series and condition.")
            return
        
        self.query_built.emit(series_id, condition)
        logger.info("query_built", series_id=series_id, condition=condition)


class SelectionHistoryWidget(QWidget):
    """Widget para histórico de seleções"""
    
    # Signals
    selection_restored = pyqtSignal(object)  # Selection object
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.selections: List[Selection] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_layout.addWidget(QLabel("Selection History"))
        header_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self._clear_history)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._restore_selection)
        layout.addWidget(self.history_list)
        
        # Selection details
        details_group = QGroupBox("Selection Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # Connect selection change
        self.history_list.itemSelectionChanged.connect(self._show_selection_details)
    
    def add_selection(self, selection: Selection):
        """Adiciona seleção ao histórico"""
        self.selections.append(selection)
        
        # Create list item
        timestamp_str = time.strftime("%H:%M:%S", time.localtime(selection.criteria.timestamp or time.time()))
        item_text = f"[{timestamp_str}] {selection.criteria.description} ({selection.n_points} points)"
        
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, len(self.selections) - 1)  # Store index
        self.history_list.addItem(item)
        
        # Auto-scroll to bottom
        self.history_list.scrollToBottom()
    
    @pyqtSlot()
    def _show_selection_details(self):
        """Mostra detalhes da seleção selecionada"""
        current_item = self.history_list.currentItem()
        if not current_item:
            self.details_text.clear()
            return
        
        selection_index = current_item.data(Qt.ItemDataRole.UserRole)
        if selection_index >= len(self.selections):
            return
        
        selection = self.selections[selection_index]
        
        details = f"Mode: {selection.criteria.mode.value}\n"
        details += f"Points: {selection.n_points}\n"
        details += f"Series: {', '.join(selection.series_ids)}\n"
        
        if selection.criteria.mode == SelectionMode.TEMPORAL:
            details += f"Time range: {selection.criteria.start_time:.3f} - {selection.criteria.end_time:.3f}s\n"
        elif selection.criteria.mode == SelectionMode.CONDITIONAL:
            details += f"Condition: {selection.criteria.series_id} {selection.criteria.condition}\n"
        
        details += f"\nMetadata: {selection.metadata}"
        
        self.details_text.setText(details)
    
    @pyqtSlot(QListWidgetItem)
    def _restore_selection(self, item: QListWidgetItem):
        """Restaura seleção do histórico"""
        selection_index = item.data(Qt.ItemDataRole.UserRole)
        if selection_index >= len(self.selections):
            return
        
        selection = self.selections[selection_index]
        self.selection_restored.emit(selection)
        logger.info("selection_restored", description=selection.criteria.description)
    
    @pyqtSlot()
    def _clear_history(self):
        """Limpa histórico"""
        self.selections.clear()
        self.history_list.clear()
        self.details_text.clear()


class SelectionManagerWidget(QWidget):
    """Widget principal do sistema de seleção"""
    
    # Signals
    selection_made = pyqtSignal(object)  # Selection object
    selection_changed = pyqtSignal(object)  # Selection object
    
    def __init__(self, session_state: SessionState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.data_selector = DataSelector()
        self.current_dataset: Optional[Dataset] = None
        
        self._setup_ui()
        self._setup_connections()
        
        logger.debug("selection_manager_widget_initialized")
    
    def _setup_ui(self):
        """Configura interface principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Dataset selection
        dataset_group = QGroupBox("Dataset")
        dataset_layout = QFormLayout(dataset_group)
        
        self.dataset_combo = QComboBox()
        self.dataset_combo.currentTextChanged.connect(self._on_dataset_changed)
        dataset_layout.addRow("Current Dataset:", self.dataset_combo)
        
        layout.addWidget(dataset_group)
        
        # Selection methods tabs
        self.selection_tabs = QTabWidget()
        
        # Temporal selection
        self.range_picker = RangePickerWidget()
        self.range_picker.range_selected.connect(self._on_temporal_selection)
        self.selection_tabs.addTab(self.range_picker, "Time Range")
        
        # Interactive selection
        self.brush_selection = BrushSelectionWidget()
        self.brush_selection.points_selected.connect(self._on_interactive_selection)
        self.selection_tabs.addTab(self.brush_selection, "Interactive")
        
        # Conditional selection
        self.query_builder = QueryBuilderWidget()
        self.query_builder.query_built.connect(self._on_conditional_selection)
        self.selection_tabs.addTab(self.query_builder, "Conditional")
        
        layout.addWidget(self.selection_tabs)
        
        # History
        self.history_widget = SelectionHistoryWidget()
        self.history_widget.selection_restored.connect(self._on_selection_restored)
        layout.addWidget(self.history_widget)
        
        # Update dataset list
        self._update_dataset_list()
    
    def _setup_connections(self):
        """Setup de conexões"""
        self.session_state.dataset_added.connect(self._update_dataset_list)
        self.session_state.dataset_removed.connect(self._update_dataset_list)
    
    def _update_dataset_list(self):
        """Atualiza lista de datasets"""
        current_text = self.dataset_combo.currentText()
        
        self.dataset_combo.clear()
        for dataset_id in self.session_state.datasets.keys():
            self.dataset_combo.addItem(dataset_id)
        
        # Restore selection if possible
        index = self.dataset_combo.findText(current_text)
        if index >= 0:
            self.dataset_combo.setCurrentIndex(index)
    
    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Callback quando dataset muda"""
        if not dataset_id or dataset_id not in self.session_state.datasets:
            self.current_dataset = None
            return
        
        self.current_dataset = self.session_state.datasets[dataset_id]
        
        # Update all selection widgets
        self.range_picker.set_dataset(self.current_dataset)
        self.brush_selection.set_dataset(self.current_dataset)
        
        series_names = [series.name for series in self.current_dataset.series.values()]
        self.query_builder.set_available_series(series_names)
        
        logger.info("selection_dataset_changed", dataset_id=dataset_id)
    
    @pyqtSlot(float, float)
    def _on_temporal_selection(self, start_time: float, end_time: float):
        """Callback para seleção temporal"""
        if not self.current_dataset:
            return
        
        try:
            selection = self.data_selector.select_temporal(
                self.current_dataset, start_time, end_time
            )
            
            self._handle_new_selection(selection)
            
        except Exception as e:
            QMessageBox.warning(self, "Selection Error", f"Failed to create temporal selection: {e}")
            logger.error("temporal_selection_failed", error=str(e))
    
    @pyqtSlot(list)
    def _on_interactive_selection(self, point_indices: List[int]):
        """Callback para seleção interativa"""
        if not self.current_dataset or not point_indices:
            return
        
        try:
            selection = self.data_selector.select_interactive(
                self.current_dataset, point_indices
            )
            
            self._handle_new_selection(selection)
            
        except Exception as e:
            QMessageBox.warning(self, "Selection Error", f"Failed to create interactive selection: {e}")
            logger.error("interactive_selection_failed", error=str(e))
    
    @pyqtSlot(str, str)
    def _on_conditional_selection(self, series_id: str, condition: str):
        """Callback para seleção condicional"""
        if not self.current_dataset:
            return
        
        try:
            # Map series name back to series ID
            target_series_id = None
            for sid, series in self.current_dataset.series.items():
                if series.name == series_id:
                    target_series_id = sid
                    break
            
            if not target_series_id:
                raise ValueError(f"Series '{series_id}' not found")
            
            selection = self.data_selector.select_conditional(
                self.current_dataset, target_series_id, condition
            )
            
            self._handle_new_selection(selection)
            
        except Exception as e:
            QMessageBox.warning(self, "Selection Error", f"Failed to create conditional selection: {e}")
            logger.error("conditional_selection_failed", error=str(e))
    
    @pyqtSlot(object)
    def _on_selection_restored(self, selection: Selection):
        """Callback quando seleção é restaurada do histórico"""
        self._handle_new_selection(selection)
    
    def _handle_new_selection(self, selection: Selection):
        """Manipula nova seleção"""
        # Add to history
        self.history_widget.add_selection(selection)
        
        # Emit signals
        self.selection_made.emit(selection)
        self.selection_changed.emit(selection)
        
        logger.info("selection_created", 
                   mode=selection.criteria.mode.value,
                   points=selection.n_points,
                   series_count=len(selection.series_ids))
    
    def get_current_selection(self) -> Optional[Selection]:
        """Retorna seleção atual"""
        return self.data_selector.active_selection
    
    def clear_selection(self):
        """Limpa seleção atual"""
        self.data_selector.clear_selection()
        self.selection_changed.emit(None)