"""
Interactive Selection Widgets - Platform Base v2.0

Provides UI components for advanced selection functionality:
- Selection toolbar with tools
- Selection criteria dialog
- Selection statistics panel
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QAction,
    QDialog, QFormLayout, QLineEdit, QPushButton, QLabel,
    QComboBox, QCheckBox, QGroupBox, QTextEdit, QSpinBox,
    QDoubleSpinBox, QSlider, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QRectF
from PyQt6.QtGui import QActionGroup, QIcon, QFont

from platform_base.desktop.selection import (
    SelectionManager, SelectionType, SelectionMode
)
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class SelectionToolbar(QToolBar):
    """
    Toolbar for selection tools and modes.
    
    Provides quick access to selection functionality:
    - Selection type buttons (temporal, graphical, conditional)
    - Selection mode buttons (replace, add, subtract, intersect)
    - Clear and undo/redo actions
    """
    
    # Signals
    selection_type_changed = pyqtSignal(object)  # SelectionType
    selection_mode_changed = pyqtSignal(object)  # SelectionMode
    clear_selection_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    conditional_dialog_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Selection Tools", parent)
        
        self._selection_type = SelectionType.TEMPORAL
        self._selection_mode = SelectionMode.REPLACE
        
        self._setup_ui()
        
        logger.debug("selection_toolbar_initialized")
    
    def _setup_ui(self):
        """Setup toolbar UI"""
        # Selection Type Group
        self.addWidget(QLabel("Type:"))
        
        type_group = QActionGroup(self)
        
        self.temporal_action = QAction("⏰ Temporal", self)
        self.temporal_action.setCheckable(True)
        self.temporal_action.setChecked(True)
        self.temporal_action.setToolTip("Select by time range")
        self.temporal_action.triggered.connect(
            lambda: self._set_selection_type(SelectionType.TEMPORAL))
        type_group.addAction(self.temporal_action)
        self.addAction(self.temporal_action)
        
        self.graphical_action = QAction("📐 Graphical", self)
        self.graphical_action.setCheckable(True)
        self.graphical_action.setToolTip("Select by drawing region on plot")
        self.graphical_action.triggered.connect(
            lambda: self._set_selection_type(SelectionType.GRAPHICAL))
        type_group.addAction(self.graphical_action)
        self.addAction(self.graphical_action)
        
        self.conditional_action = QAction("🔍 Conditional", self)
        self.conditional_action.setCheckable(True)
        self.conditional_action.setToolTip("Select by value conditions")
        self.conditional_action.triggered.connect(self._open_conditional_dialog)
        type_group.addAction(self.conditional_action)
        self.addAction(self.conditional_action)
        
        self.addSeparator()
        
        # Selection Mode Group
        self.addWidget(QLabel("Mode:"))
        
        mode_group = QActionGroup(self)
        
        self.replace_action = QAction("Replace", self)
        self.replace_action.setCheckable(True)
        self.replace_action.setChecked(True)
        self.replace_action.setToolTip("Replace current selection")
        self.replace_action.triggered.connect(
            lambda: self._set_selection_mode(SelectionMode.REPLACE))
        mode_group.addAction(self.replace_action)
        self.addAction(self.replace_action)
        
        self.add_action = QAction("➕ Add", self)
        self.add_action.setCheckable(True)
        self.add_action.setToolTip("Add to current selection")
        self.add_action.triggered.connect(
            lambda: self._set_selection_mode(SelectionMode.ADD))
        mode_group.addAction(self.add_action)
        self.addAction(self.add_action)
        
        self.subtract_action = QAction("➖ Subtract", self)
        self.subtract_action.setCheckable(True)
        self.subtract_action.setToolTip("Remove from current selection")
        self.subtract_action.triggered.connect(
            lambda: self._set_selection_mode(SelectionMode.SUBTRACT))
        mode_group.addAction(self.subtract_action)
        self.addAction(self.subtract_action)
        
        self.intersect_action = QAction("⚏ Intersect", self)
        self.intersect_action.setCheckable(True)
        self.intersect_action.setToolTip("Intersect with current selection")
        self.intersect_action.triggered.connect(
            lambda: self._set_selection_mode(SelectionMode.INTERSECT))
        mode_group.addAction(self.intersect_action)
        self.addAction(self.intersect_action)
        
        self.addSeparator()
        
        # Action buttons
        self.clear_action = QAction("🗑️ Clear", self)
        self.clear_action.setToolTip("Clear all selections")
        self.clear_action.triggered.connect(self.clear_selection_requested.emit)
        self.addAction(self.clear_action)
        
        self.undo_action = QAction("↶ Undo", self)
        self.undo_action.setToolTip("Undo last selection")
        self.undo_action.triggered.connect(self.undo_requested.emit)
        self.addAction(self.undo_action)
        
        self.redo_action = QAction("↷ Redo", self)
        self.redo_action.setToolTip("Redo selection")
        self.redo_action.triggered.connect(self.redo_requested.emit)
        self.addAction(self.redo_action)
    
    def _set_selection_type(self, selection_type: SelectionType):
        """Set current selection type"""
        self._selection_type = selection_type
        self.selection_type_changed.emit(selection_type)
        logger.debug("selection_type_changed", type=selection_type.value)
    
    def _set_selection_mode(self, selection_mode: SelectionMode):
        """Set current selection mode"""
        self._selection_mode = selection_mode
        self.selection_mode_changed.emit(selection_mode)
        logger.debug("selection_mode_changed", mode=selection_mode.value)
    
    def _open_conditional_dialog(self):
        """Open conditional selection dialog"""
        self._set_selection_type(SelectionType.CONDITIONAL)
        self.conditional_dialog_requested.emit()
    
    @property
    def selection_type(self) -> SelectionType:
        return self._selection_type
    
    @property
    def selection_mode(self) -> SelectionMode:
        return self._selection_mode
    
    def update_undo_redo_state(self, can_undo: bool, can_redo: bool):
        """Update undo/redo button states"""
        self.undo_action.setEnabled(can_undo)
        self.redo_action.setEnabled(can_redo)


class ConditionalSelectionDialog(QDialog):
    """
    Dialog for creating conditional value-based selections.
    
    Allows users to create complex selection criteria using
    mathematical expressions and value conditions.
    """
    
    selection_requested = pyqtSignal(str, object)  # condition, SelectionMode
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setWindowTitle("Conditional Selection")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
        
        logger.debug("conditional_selection_dialog_created")
    
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Condition input group
        condition_group = QGroupBox("Selection Condition")
        condition_layout = QVBoxLayout(condition_group)
        
        # Help text
        help_text = QLabel(
            "Enter a Python expression using 't' (time) and 'value' variables.\\n"
            "Examples:\\n"
            "• value > 10  (values greater than 10)\\n"
            "• abs(value) < 5  (absolute values less than 5)\\n"
            "• value > 2*t  (value greater than 2 times time)\\n"
            "• sin(t) > 0.5  (sine of time greater than 0.5)"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: gray; font-size: 10px;")
        condition_layout.addWidget(help_text)
        
        # Condition input
        self.condition_edit = QTextEdit()
        self.condition_edit.setMaximumHeight(80)
        self.condition_edit.setPlainText("value > 0")
        condition_layout.addWidget(self.condition_edit)
        
        layout.addWidget(condition_group)
        
        # Quick conditions group
        quick_group = QGroupBox("Quick Conditions")
        quick_layout = QVBoxLayout(quick_group)
        
        # Threshold controls
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Value threshold:"))
        
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(-1e10, 1e10)
        self.threshold_spin.setDecimals(6)
        self.threshold_spin.setValue(0.0)
        threshold_layout.addWidget(self.threshold_spin)
        
        self.threshold_operator = QComboBox()
        self.threshold_operator.addItems([">", ">=", "<", "<=", "==", "!="])
        threshold_layout.addWidget(self.threshold_operator)
        
        apply_threshold_btn = QPushButton("Apply Threshold")
        apply_threshold_btn.clicked.connect(self._apply_threshold_condition)
        threshold_layout.addWidget(apply_threshold_btn)
        
        quick_layout.addLayout(threshold_layout)
        
        # Percentile controls
        percentile_layout = QHBoxLayout()
        percentile_layout.addWidget(QLabel("Top/bottom percentile:"))
        
        self.percentile_spin = QSpinBox()
        self.percentile_spin.setRange(1, 50)
        self.percentile_spin.setValue(10)
        self.percentile_spin.setSuffix("%")
        percentile_layout.addWidget(self.percentile_spin)
        
        self.percentile_type = QComboBox()
        self.percentile_type.addItems(["Top", "Bottom"])
        percentile_layout.addWidget(self.percentile_type)
        
        apply_percentile_btn = QPushButton("Apply Percentile")
        apply_percentile_btn.clicked.connect(self._apply_percentile_condition)
        percentile_layout.addWidget(apply_percentile_btn)
        
        quick_layout.addLayout(percentile_layout)
        
        layout.addWidget(quick_group)
        
        # Selection mode
        mode_group = QGroupBox("Selection Mode")
        mode_layout = QHBoxLayout(mode_group)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Replace", "Add", "Subtract", "Intersect"])
        mode_layout.addWidget(self.mode_combo)
        
        layout.addWidget(mode_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply Selection")
        apply_btn.clicked.connect(self._apply_selection)
        apply_btn.setDefault(True)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _apply_threshold_condition(self):
        """Apply threshold-based condition"""
        threshold = self.threshold_spin.value()
        operator = self.threshold_operator.currentText()
        condition = f"value {operator} {threshold}"
        self.condition_edit.setPlainText(condition)
    
    def _apply_percentile_condition(self):
        """Apply percentile-based condition"""
        percentile = self.percentile_spin.value()
        is_top = self.percentile_type.currentText() == "Top"
        
        if is_top:
            condition = f"value >= np.percentile(values, {100 - percentile})"
        else:
            condition = f"value <= np.percentile(values, {percentile})"
        
        self.condition_edit.setPlainText(condition)
    
    def _apply_selection(self):
        """Apply the conditional selection"""
        condition = self.condition_edit.toPlainText().strip()
        if not condition:
            return
        
        mode_text = self.mode_combo.currentText()
        mode_map = {
            "Replace": SelectionMode.REPLACE,
            "Add": SelectionMode.ADD,
            "Subtract": SelectionMode.SUBTRACT,
            "Intersect": SelectionMode.INTERSECT
        }
        mode = mode_map[mode_text]
        
        self.selection_requested.emit(condition, mode)
        self.accept()
        
        logger.debug("conditional_selection_applied", 
                    condition=condition, mode=mode.value)


class SelectionStatsWidget(QWidget):
    """
    Widget displaying statistics about current selection.
    
    Shows:
    - Number of selected points
    - Selection percentage  
    - Value statistics (min, max, mean, etc.)
    - Time range information
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._setup_ui()
        self._clear_stats()
        
        logger.debug("selection_stats_widget_created")
    
    def _setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Selection Statistics")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Count information
        count_group = QGroupBox("Count")
        count_layout = QFormLayout(count_group)
        
        self.total_points_label = QLabel("0")
        count_layout.addRow("Total Points:", self.total_points_label)
        
        self.selected_points_label = QLabel("0")
        count_layout.addRow("Selected:", self.selected_points_label)
        
        self.selection_ratio_label = QLabel("0.0%")
        count_layout.addRow("Percentage:", self.selection_ratio_label)
        
        # Progress bar for selection ratio
        self.selection_progress = QProgressBar()
        self.selection_progress.setMaximum(100)
        self.selection_progress.setValue(0)
        count_layout.addRow("", self.selection_progress)
        
        layout.addWidget(count_group)
        
        # Value statistics
        stats_group = QGroupBox("Value Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.min_value_label = QLabel("-")
        stats_layout.addRow("Minimum:", self.min_value_label)
        
        self.max_value_label = QLabel("-")
        stats_layout.addRow("Maximum:", self.max_value_label)
        
        self.mean_value_label = QLabel("-")
        stats_layout.addRow("Mean:", self.mean_value_label)
        
        self.std_value_label = QLabel("-")
        stats_layout.addRow("Std Dev:", self.std_value_label)
        
        layout.addWidget(stats_group)
        
        # Time range information
        time_group = QGroupBox("Time Range")
        time_layout = QFormLayout(time_group)
        
        self.time_ranges_label = QLabel("-")
        self.time_ranges_label.setWordWrap(True)
        time_layout.addRow("Ranges:", self.time_ranges_label)
        
        self.total_duration_label = QLabel("-")
        time_layout.addRow("Total Duration:", self.total_duration_label)
        
        layout.addWidget(time_group)
        
        layout.addStretch()
    
    def update_stats(self, total_points: int, selected_points: int,
                    value_stats: Optional[Dict[str, float]] = None,
                    time_ranges: Optional[list] = None):
        """Update displayed statistics"""
        # Count information
        self.total_points_label.setText(f"{total_points:,}")
        self.selected_points_label.setText(f"{selected_points:,}")
        
        if total_points > 0:
            ratio = (selected_points / total_points) * 100
            self.selection_ratio_label.setText(f"{ratio:.1f}%")
            self.selection_progress.setValue(int(ratio))
        else:
            self.selection_ratio_label.setText("0.0%")
            self.selection_progress.setValue(0)
        
        # Value statistics
        if value_stats and selected_points > 0:
            self.min_value_label.setText(f"{value_stats['min']:.6g}")
            self.max_value_label.setText(f"{value_stats['max']:.6g}")
            self.mean_value_label.setText(f"{value_stats['mean']:.6g}")
            self.std_value_label.setText(f"{value_stats['std']:.6g}")
        else:
            self.min_value_label.setText("-")
            self.max_value_label.setText("-")
            self.mean_value_label.setText("-")
            self.std_value_label.setText("-")
        
        # Time ranges
        if time_ranges and len(time_ranges) > 0:
            if len(time_ranges) == 1:
                start, end = time_ranges[0]
                self.time_ranges_label.setText(f"{start:.2f} - {end:.2f} s")
                self.total_duration_label.setText(f"{end - start:.2f} s")
            else:
                range_text = f"{len(time_ranges)} ranges"
                self.time_ranges_label.setText(range_text)
                
                total_duration = sum(end - start for start, end in time_ranges)
                self.total_duration_label.setText(f"{total_duration:.2f} s")
        else:
            self.time_ranges_label.setText("-")
            self.total_duration_label.setText("-")
        
        logger.debug("selection_stats_updated",
                    total=total_points, selected=selected_points)
    
    def _clear_stats(self):
        """Clear all statistics"""
        self.update_stats(0, 0)


class SelectionPanel(QWidget):
    """
    Complete selection control panel combining toolbar, stats and dialogs.
    
    Provides integrated selection interface for plot widgets.
    """
    
    # Signals for communication with plot widgets
    temporal_selection_requested = pyqtSignal(float, float, object)  # start, end, mode
    graphical_selection_requested = pyqtSignal(object, object)  # region, mode  
    conditional_selection_requested = pyqtSignal(str, object)  # condition, mode
    clear_selection_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._setup_ui()
        self._connect_signals()
        
        self._conditional_dialog: Optional[ConditionalSelectionDialog] = None
        
        logger.debug("selection_panel_initialized")
    
    def _setup_ui(self):
        """Setup panel UI"""
        layout = QVBoxLayout(self)
        
        # Selection toolbar
        self.toolbar = SelectionToolbar()
        layout.addWidget(self.toolbar)
        
        # Selection statistics
        self.stats_widget = SelectionStatsWidget()
        layout.addWidget(self.stats_widget)
    
    def _connect_signals(self):
        """Connect internal signals"""
        # Toolbar signals
        self.toolbar.clear_selection_requested.connect(
            self.clear_selection_requested.emit)
        self.toolbar.undo_requested.connect(self.undo_requested.emit)
        self.toolbar.redo_requested.connect(self.redo_requested.emit)
        self.toolbar.conditional_dialog_requested.connect(
            self._show_conditional_dialog)
    
    def _show_conditional_dialog(self):
        """Show conditional selection dialog"""
        if self._conditional_dialog is None:
            self._conditional_dialog = ConditionalSelectionDialog(self)
            self._conditional_dialog.selection_requested.connect(
                self.conditional_selection_requested.emit)
        
        self._conditional_dialog.show()
        self._conditional_dialog.raise_()
        self._conditional_dialog.activateWindow()
    
    @property
    def selection_type(self) -> SelectionType:
        return self.toolbar.selection_type
    
    @property 
    def selection_mode(self) -> SelectionMode:
        return self.toolbar.selection_mode
    
    def update_selection_stats(self, total_points: int, selected_points: int,
                             value_stats: Optional[Dict[str, float]] = None,
                             time_ranges: Optional[list] = None):
        """Update selection statistics display"""
        self.stats_widget.update_stats(total_points, selected_points, 
                                     value_stats, time_ranges)
    
    def update_undo_redo_state(self, can_undo: bool, can_redo: bool):
        """Update undo/redo button states"""
        self.toolbar.update_undo_redo_state(can_undo, can_redo)