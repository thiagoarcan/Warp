"""
Example: Refactored DataPanel using UI Designer file

This is a demonstration of how the DataPanel class would be refactored
to use the new .ui file approach with UiLoaderMixin.

NOTE: This is an EXAMPLE only. The actual refactoring will be done in Phase 4.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QHeaderView,
    QTableWidgetItem,
    QTreeWidgetItem,
    QWidget,
)

from platform_base.core.models import Dataset
from platform_base.ui.mixins import UiLoaderMixin
from platform_base.ui.state import SessionState
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class DataPanelRefactored(QWidget, UiLoaderMixin):
    """
    EXAMPLE: Refactored DataPanel using .ui file
    
    This demonstrates the new pattern:
    1. Define UI_FILE class attribute
    2. Call _load_ui() in __init__
    3. Access widgets directly (they're loaded from .ui)
    4. Keep business logic separate
    
    Original: ~800 lines of UI setup code
    Refactored: ~200 lines of business logic only
    """
    
    # Specify the UI file to load
    UI_FILE = "panels/data_panel"
    
    # Signals (same as original)
    dataset_loaded = pyqtSignal(str)  # dataset_id
    series_selected = pyqtSignal(str, str)  # dataset_id, series_id
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        
        self.session_state = session_state
        self._current_dataset: Optional[Dataset] = None
        
        # Load the UI from .ui file
        # This replaces all the _setup_modern_ui() code
        self._load_ui()
        
        # Setup widget configurations that can't be in .ui
        self._configure_widgets()
        
        # Connect signals
        self._setup_connections()
        
        logger.debug("data_panel_refactored_initialized")
    
    def _configure_widgets(self):
        """
        Configure widget properties that can't be fully specified in .ui
        
        This is where we set up:
        - Header resize modes
        - Special behaviors (drag-drop)
        - Context menus
        - Custom properties
        """
        # Configure datasets tree headers
        datasets_header = self.datasets_tree.header()
        datasets_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        datasets_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        datasets_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Configure series tree headers
        series_header = self.series_tree.header()
        series_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        series_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        series_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Enable custom context menu for series
        self.series_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Configure data table headers
        table_header = self.data_table.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table_header.setDefaultSectionSize(80)
        
        # Hide vertical header
        v_header = self.data_table.verticalHeader()
        v_header.setDefaultSectionSize(24)
        v_header.setVisible(False)
        
        logger.debug("widgets_configured")
    
    def _setup_connections(self):
        """
        Connect signals from UI widgets to handlers
        
        Note: All widget names come from the .ui file
        """
        # Button connections
        self.load_button.clicked.connect(self._open_file_dialog)
        
        # Tree widget connections
        self.datasets_tree.itemClicked.connect(self._on_dataset_selected)
        self.series_tree.itemClicked.connect(self._on_series_selected)
        self.series_tree.customContextMenuRequested.connect(self._show_series_context_menu)
        
        # Combo box connections
        self.preview_rows_combo.currentTextChanged.connect(self._update_data_table)
        
        # Session state connections
        self.session_state.dataset_changed.connect(self._on_dataset_changed)
        self.session_state.operation_started.connect(self._on_operation_started)
        self.session_state.operation_finished.connect(self._on_operation_finished)
        
        logger.debug("connections_setup_completed")
    
    # ==================== Event Handlers ====================
    # All business logic methods remain the same
    
    def _open_file_dialog(self):
        """Handler for load button click"""
        logger.info("open_file_dialog_clicked")
        # Implementation same as original...
        pass
    
    def _on_dataset_selected(self, item: QTreeWidgetItem, column: int):
        """Handler for dataset selection"""
        logger.info("dataset_selected", dataset=item.text(0))
        # Implementation same as original...
        pass
    
    def _on_series_selected(self, item: QTreeWidgetItem, column: int):
        """Handler for series selection"""
        logger.info("series_selected", series=item.text(0))
        # Implementation same as original...
        pass
    
    def _on_dataset_changed(self, dataset_id: str):
        """Handler for dataset change from session state"""
        if dataset_id:
            try:
                self._current_dataset = self.session_state.get_dataset(dataset_id)
                self._update_datasets_list()
                self._update_dataset_info()
                self._update_series_tree()
                self._update_data_table()
            except Exception as e:
                logger.error("dataset_change_failed", dataset_id=dataset_id, error=str(e))
        else:
            self._current_dataset = None
            self._clear_ui()
    
    def _on_operation_started(self, operation_name: str):
        """Handler for operation start"""
        self.load_button.setEnabled(False)
    
    def _on_operation_finished(self, operation_name: str, success: bool):
        """Handler for operation completion"""
        self.load_button.setEnabled(True)
    
    def _show_series_context_menu(self, position):
        """Show context menu for series"""
        logger.debug("series_context_menu_requested")
        # Implementation same as original...
        pass
    
    # ==================== UI Update Methods ====================
    
    def _update_datasets_list(self):
        """Update the datasets tree widget"""
        self.datasets_tree.clear()
        # Implementation same as original...
        pass
    
    def _update_dataset_info(self):
        """Update current dataset info labels"""
        if self._current_dataset:
            self.dataset_name_label.setText(self._current_dataset.name)
            n_series = len(self._current_dataset.series)
            n_points = sum(len(s.data) for s in self._current_dataset.series.values())
            self.dataset_stats_label.setText(f"{n_series} séries • {n_points} pontos")
        else:
            self.dataset_name_label.setText("Nenhum dataset")
            self.dataset_stats_label.setText("0 séries • 0 pontos")
    
    def _update_series_tree(self):
        """Update the series tree widget"""
        self.series_tree.clear()
        # Implementation same as original...
        pass
    
    def _update_data_table(self):
        """Update the data preview table"""
        self.data_table.clear()
        # Implementation same as original...
        pass
    
    def _clear_ui(self):
        """Clear all UI elements"""
        self.datasets_tree.clear()
        self.series_tree.clear()
        self.data_table.clear()
        self.dataset_name_label.setText("Nenhum dataset")
        self.dataset_stats_label.setText("0 séries • 0 pontos")
