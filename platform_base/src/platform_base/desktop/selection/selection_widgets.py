"""
Interactive Selection Widgets - Platform Base v2.0

Provides UI components for advanced selection functionality:
- Selection toolbar with tools
- Selection criteria dialog
- Selection statistics panel
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.selection import SelectionMode, SelectionType
from platform_base.desktop.widgets.base import UiLoaderMixin
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

    def __init__(self, parent: QWidget | None = None):
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


class ConditionalSelectionDialog(QDialog, UiLoaderMixin):
    """
    Dialog for creating conditional value-based selections.

    Allows users to create complex selection criteria using
    mathematical expressions and value conditions.
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "conditionalSelectionDialog.ui"

    selection_requested = pyqtSignal(str, object)  # condition, SelectionMode

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWindowTitle("Conditional Selection")
        self.setModal(True)
        self.resize(400, 300)

        # Carrega do arquivo .ui ou lança erro
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()
        
        logger.debug("conditional_selection_dialog_created", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        self.condition_edit = self.findChild(QTextEdit, "conditionEdit")
        self.threshold_spin = self.findChild(QDoubleSpinBox, "thresholdSpin")
        self.threshold_operator = self.findChild(QComboBox, "thresholdOperator")
        self.percentile_spin = self.findChild(QSpinBox, "percentileSpin")
        self.percentile_type = self.findChild(QComboBox, "percentileType")
        self.mode_combo = self.findChild(QComboBox, "modeCombo")
        
        apply_threshold_btn = self.findChild(QPushButton, "applyThresholdBtn")
        apply_percentile_btn = self.findChild(QPushButton, "applyPercentileBtn")
        apply_btn = self.findChild(QPushButton, "applyBtn")
        close_btn = self.findChild(QPushButton, "closeBtn")
        
        # Configura valores iniciais
        if self.condition_edit:
            self.condition_edit.setPlainText("value > 0")
        
        # Conecta sinais
        if apply_threshold_btn:
            apply_threshold_btn.clicked.connect(self._apply_threshold_condition)
        if apply_percentile_btn:
            apply_percentile_btn.clicked.connect(self._apply_percentile_condition)
        if apply_btn:
            apply_btn.clicked.connect(self._apply_selection)
        if close_btn:
            close_btn.clicked.connect(self.close)

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
            "Intersect": SelectionMode.INTERSECT,
        }
        mode = mode_map[mode_text]

        self.selection_requested.emit(condition, mode)
        self.accept()

        logger.debug("conditional_selection_applied",
                    condition=condition, mode=mode.value)


class SelectionStatsWidget(QWidget, UiLoaderMixin):
    """
    Widget displaying statistics about current selection.

    Shows:
    - Number of selected points
    - Selection percentage
    - Value statistics (min, max, mean, etc.)
    - Time range information
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "selectionStatsWidget.ui"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Carrega do arquivo .ui ou lança erro
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()
        
        self._clear_stats()
        logger.debug("selection_stats_widget_created", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        self.total_points_label = self.findChild(QLabel, "totalPointsLabel")
        self.selected_points_label = self.findChild(QLabel, "selectedPointsLabel")
        self.selection_ratio_label = self.findChild(QLabel, "selectionRatioLabel")
        self.selection_progress = self.findChild(QProgressBar, "selectionProgress")
        self.min_value_label = self.findChild(QLabel, "minValueLabel")
        self.max_value_label = self.findChild(QLabel, "maxValueLabel")
        self.mean_value_label = self.findChild(QLabel, "meanValueLabel")
        self.std_value_label = self.findChild(QLabel, "stdValueLabel")
        self.time_ranges_label = self.findChild(QLabel, "timeRangesLabel")
        self.total_duration_label = self.findChild(QLabel, "totalDurationLabel")

    def update_stats(self, total_points: int, selected_points: int,
                    value_stats: dict[str, float] | None = None,
                    time_ranges: list | None = None):
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


class SelectionPanel(QWidget, UiLoaderMixin):
    """
    Complete selection control panel combining toolbar, stats and dialogs.

    Provides integrated selection interface for plot widgets.
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "selectionPanel.ui"

    # Signals for communication with plot widgets
    temporal_selection_requested = pyqtSignal(float, float, object)  # start, end, mode
    graphical_selection_requested = pyqtSignal(object, object)  # region, mode
    conditional_selection_requested = pyqtSignal(str, object)  # condition, mode
    clear_selection_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._conditional_dialog: ConditionalSelectionDialog | None = None

        # Carrega do arquivo .ui ou lança erro
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()
        
        self._connect_signals()
        logger.debug("selection_panel_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Cria os widgets filhos
        self.toolbar = SelectionToolbar()
        self.stats_widget = SelectionStatsWidget()
        
        # Adiciona ao layout do arquivo .ui
        main_layout = self.layout()
        if main_layout:
            main_layout.addWidget(self.toolbar)
            main_layout.addWidget(self.stats_widget)

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
                             value_stats: dict[str, float] | None = None,
                             time_ranges: list | None = None):
        """Update selection statistics display"""
        self.stats_widget.update_stats(total_points, selected_points,
                                     value_stats, time_ranges)

    def update_undo_redo_state(self, can_undo: bool, can_redo: bool):
        """Update undo/redo button states"""
        self.toolbar.update_undo_redo_state(can_undo, can_redo)


# Alias for backward compatibility
SelectionStatisticsPanel = SelectionStatsWidget
