"""
DataPanel - Dataset and series management widget for Platform Base v2.0

Provides tree view of datasets and series with selection capabilities.
Replaces Dash data selection components with native PyQt6 tree widget.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from platform_base.core.models import DatasetID, SeriesID
from platform_base.desktop.models.dataset_model import DatasetTreeModel
from platform_base.desktop.session_state import SessionState
from platform_base.desktop.signal_hub import SignalHub
from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class DataPanel(QWidget):
    """
    Data management panel widget.
    
    Features:
    - Dataset tree view with series
    - Dataset/series selection
    - Data summary information
    - Import/export actions
    """
    
    def __init__(self, session_state: SessionState, signal_hub: SignalHub, 
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.signal_hub = signal_hub
        
        self._setup_ui()
        self._connect_signals()
        
        logger.debug("data_panel_initialized")
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Data tree section
        tree_group = QGroupBox(tr("Datasets & Series"))
        tree_layout = QVBoxLayout(tree_group)
        
        # Tree view with model
        from PyQt6.QtWidgets import QTreeView
        self.data_tree = QTreeView()
        self.tree_model = DatasetTreeModel(self.session_state.dataset_store)
        self.data_tree.setModel(self.tree_model)
        
        self.data_tree.setAlternatingRowColors(True)
        self.data_tree.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.data_tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)
        self.data_tree.doubleClicked.connect(self._on_item_double_clicked)
        
        # Configure columns
        header = self.data_tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        tree_layout.addWidget(self.data_tree)
        
        # Tree action buttons
        tree_buttons = QHBoxLayout()
        
        self.load_btn = QPushButton(tr("Load Data"))
        self.load_btn.clicked.connect(self._load_data)
        tree_buttons.addWidget(self.load_btn)
        
        self.remove_btn = QPushButton(tr("Remove"))
        self.remove_btn.clicked.connect(self._remove_selected)
        self.remove_btn.setEnabled(False)
        tree_buttons.addWidget(self.remove_btn)
        
        tree_buttons.addStretch()
        
        self.refresh_btn = QPushButton(tr("Refresh"))
        self.refresh_btn.clicked.connect(self._refresh_data)
        tree_buttons.addWidget(self.refresh_btn)
        
        tree_layout.addLayout(tree_buttons)
        layout.addWidget(tree_group)
        
        # Data info section
        info_group = QGroupBox(tr("Data Information"))
        info_layout = QVBoxLayout(info_group)
        
        # Info tabs
        self.info_tabs = QTabWidget()
        
        # Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        self.info_tabs.addTab(self.summary_text, tr("Summary"))
        
        # Metadata tab
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(150)
        self.info_tabs.addTab(self.metadata_text, tr("Metadata"))
        
        # Quality tab
        self.quality_text = QTextEdit()
        self.quality_text.setReadOnly(True)
        self.quality_text.setMaximumHeight(150)
        self.info_tabs.addTab(self.quality_text, tr("Quality"))
        
        info_layout.addWidget(self.info_tabs)
        layout.addWidget(info_group)
        
        # Set initial summary
        self._update_summary()
    
    def _connect_signals(self):
        """Connect signals"""
        # Listen to dataset store changes
        self.signal_hub.dataset_loaded.connect(self._on_dataset_loaded)
        self.signal_hub.dataset_removed.connect(self._on_dataset_removed)
        
        # Listen to session state changes
        self.session_state.selection_changed.connect(self._on_selection_changed)
    
    @pyqtSlot()
    def _load_data(self):
        """Trigger load data action"""
        # This will be handled by main window
        logger.debug("load_data_requested")
    
    @pyqtSlot()
    def _remove_selected(self):
        """Remove selected items"""
        selected_items = self.data_tree.selectedItems()
        
        for item in selected_items:
            dataset_id = item.data(0, Qt.ItemDataRole.UserRole)
            series_id = item.data(1, Qt.ItemDataRole.UserRole)
            
            if dataset_id and series_id:
                # Remove series
                self.signal_hub.series_removed.emit(dataset_id, series_id)
                logger.debug("series_removal_requested", 
                           dataset_id=dataset_id, series_id=series_id)
            elif dataset_id:
                # Remove dataset
                self.signal_hub.dataset_removed.emit(dataset_id)
                logger.debug("dataset_removal_requested", dataset_id=dataset_id)
    
    @pyqtSlot()
    def _refresh_data(self):
        """Refresh data tree"""
        self._populate_tree()
    
    @pyqtSlot()
    def _on_tree_selection_changed(self):
        """Handle tree selection changes"""
        # Prevent recursion when session state changes trigger tree updates
        if getattr(self, '_updating_selection', False):
            return
        
        self._updating_selection = True
        try:
            selected_indexes = self.data_tree.selectionModel().selectedIndexes()
            
            if not selected_indexes:
                self.remove_btn.setEnabled(False)
                self.session_state.clear_selection()
                return
            
            self.remove_btn.setEnabled(True)
            
            # Get first selected item
            index = selected_indexes[0]
            item_info = self.tree_model.get_item_info(index)
            
            if item_info and item_info["dataset_id"]:
                dataset_id = item_info["dataset_id"]
                series_id = item_info["series_id"]
                
                # Update session state
                self.session_state.set_current_dataset(dataset_id)
                
                if series_id:
                    # Series selected
                    self.session_state.add_series_selection(series_id)
                    self.signal_hub.emit_series_selected(dataset_id, series_id)
                else:
                    # Dataset selected
                    self.signal_hub.dataset_selected.emit(dataset_id)
                
                # Update info display
                self._update_info_display(dataset_id, series_id)
        finally:
            self._updating_selection = False
    
    @pyqtSlot()
    def _on_item_double_clicked(self, index):
        """Handle item double click"""
        item_info = self.tree_model.get_item_info(index)
        
        if item_info and item_info["dataset_id"] and item_info["series_id"]:
            dataset_id = item_info["dataset_id"]
            series_id = item_info["series_id"]
            
            # Create plot for series
            self.signal_hub.plot_created.emit(f"plot_{dataset_id}_{series_id}")
            logger.debug("plot_creation_requested", 
                        dataset_id=dataset_id, series_id=series_id)
    
    @pyqtSlot(str)
    def _on_dataset_loaded(self, dataset_id: str):
        """Handle dataset loaded"""
        self.tree_model.add_dataset(dataset_id)
        logger.debug("dataset_loaded_in_panel", dataset_id=dataset_id)
    
    @pyqtSlot(str)
    def _on_dataset_removed(self, dataset_id: str):
        """Handle dataset removed"""
        self.tree_model.remove_dataset(dataset_id)
        logger.debug("dataset_removed_from_panel", dataset_id=dataset_id)
    
    @pyqtSlot(object)
    def _on_selection_changed(self, selection_state):
        """Handle selection state changes"""
        # Update tree selection to match session state
        self._sync_tree_selection(selection_state)
    
    def _populate_tree(self):
        """Populate data tree with datasets and series"""
        # With the model, we just need to refresh
        self.tree_model.refresh_data()
        
        # Expand all dataset items by default
        for row in range(self.tree_model.rowCount()):
            index = self.tree_model.index(row, 0)
            self.data_tree.expand(index)
        
        # Update summary
        self._update_summary()
    
    def _sync_tree_selection(self, selection_state):
        """Sync tree selection with session state"""
        # Clear current selection
        self.data_tree.selectionModel().clearSelection()
        
        if not selection_state.dataset_id:
            return
        
        # Find and select dataset
        dataset_index = self.tree_model.find_dataset_index(selection_state.dataset_id)
        if dataset_index.isValid():
            self.data_tree.selectionModel().select(dataset_index, 
                self.data_tree.selectionModel().SelectionFlag.Select)
            
            # Select series if specified
            for series_id in selection_state.series_ids:
                series_index = self.tree_model.find_series_index(
                    selection_state.dataset_id, series_id)
                if series_index.isValid():
                    self.data_tree.selectionModel().select(series_index,
                        self.data_tree.selectionModel().SelectionFlag.Select)
    
    def _update_info_display(self, dataset_id: str, series_id: Optional[str] = None):
        """Update information display for selected item"""
        try:
            dataset = self.session_state.dataset_store.get_dataset(dataset_id)
            
            if series_id:
                # Show series info
                series = dataset.series[series_id]
                self._show_series_info(dataset, series)
            else:
                # Show dataset info
                self._show_dataset_info(dataset)
                
        except Exception as e:
            logger.error("failed_to_update_info_display", 
                        dataset_id=dataset_id, series_id=series_id, error=str(e))
            self._show_error_info(str(e))
    
    def _show_dataset_info(self, dataset):
        """Show dataset information"""
        # Summary
        summary = f"""Dataset: {dataset.dataset_id}
Source: {dataset.source.filename}
Format: {dataset.source.format}
Size: {dataset.source.size_bytes / 1024 / 1024:.2f} MB
Points: {len(dataset.t_seconds):,}
Series: {len(dataset.series)}
Time Range: {dataset.t_seconds[0]:.2f} - {dataset.t_seconds[-1]:.2f} sec
Duration: {dataset.t_seconds[-1] - dataset.t_seconds[0]:.2f} sec"""
        
        self.summary_text.setPlainText(summary)
        
        # Metadata
        metadata = f"""Description: {dataset.metadata.description or 'N/A'}
Tags: {', '.join(dataset.metadata.tags) if dataset.metadata.tags else 'None'}
Schema Confidence: {dataset.metadata.schema_confidence:.2%}
Timezone: {dataset.metadata.timezone}
Created: {dataset.source.loaded_at}"""
        
        self.metadata_text.setPlainText(metadata)
        
        # Quality
        quality = f"""Validation Warnings: {len(dataset.metadata.validation_warnings)}
Validation Errors: {len(dataset.metadata.validation_errors)}
Checksum: {dataset.source.checksum[:16]}...

Warnings:
{chr(10).join(dataset.metadata.validation_warnings[:5])}"""
        
        self.quality_text.setPlainText(quality)
    
    def _show_series_info(self, dataset, series):
        """Show series information"""
        # Summary
        summary = f"""Series: {series.name}
Original Name: {series.metadata.original_name}
Unit: {series.unit}
Points: {len(series.values):,}
Data Type: {series.values.dtype}
Valid Points: {(~np.isnan(series.values)).sum():,}
NaN Points: {np.isnan(series.values).sum():,}
Min Value: {np.nanmin(series.values):.6f}
Max Value: {np.nanmax(series.values):.6f}
Mean Value: {np.nanmean(series.values):.6f}"""
        
        self.summary_text.setPlainText(summary)
        
        # Metadata
        metadata = f"""Original Unit: {series.metadata.original_unit or 'N/A'}
Source Column: {series.metadata.source_column}
Description: {series.metadata.description or 'N/A'}
Tags: {', '.join(series.metadata.tags) if series.metadata.tags else 'None'}"""
        
        self.metadata_text.setPlainText(metadata)
        
        # Quality & Lineage
        quality_info = []
        
        if series.interpolation_info:
            interp_count = series.interpolation_info.is_interpolated.sum()
            quality_info.append(f"Interpolated Points: {interp_count:,}")
            
            if series.interpolation_info.confidence is not None:
                avg_confidence = series.interpolation_info.confidence.mean()
                quality_info.append(f"Avg Confidence: {avg_confidence:.2%}")
        
        if series.lineage:
            quality_info.append(f"\\nLineage:")
            quality_info.append(f"Operation: {series.lineage.operation}")
            quality_info.append(f"Origin Series: {', '.join(series.lineage.origin_series)}")
            quality_info.append(f"Created: {series.lineage.timestamp}")
            quality_info.append(f"Parameters: {series.lineage.parameters}")
        
        self.quality_text.setPlainText('\\n'.join(quality_info))
    
    def _show_error_info(self, error_msg: str):
        """Show error information"""
        self.summary_text.setPlainText(f"Error loading information: {error_msg}")
        self.metadata_text.setPlainText("")
        self.quality_text.setPlainText("")
    
    def _update_summary(self):
        """Update overall summary"""
        if not hasattr(self, 'tree_model'):
            return
            
        dataset_count = self.tree_model.rowCount()
        series_count = 0
        
        # Count series in all datasets
        for row in range(dataset_count):
            dataset_index = self.tree_model.index(row, 0)
            series_count += self.tree_model.rowCount(dataset_index)
        
        if dataset_count == 0:
            self.summary_text.setPlainText("No data loaded.\\n\\nUse 'Load Data' button to import datasets.")
        else:
            summary = f"Total Datasets: {dataset_count}\\nTotal Series: {series_count}\\n\\nSelect items to view detailed information."
            if self.data_tree.selectionModel().hasSelection():
                return  # Don't override detailed info
            self.summary_text.setPlainText(summary)
    
    def _get_dataset_icon(self) -> QIcon:
        """Get icon for dataset items"""
        return self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon)
    
    def _get_series_icon(self) -> QIcon:
        """Get icon for series items"""
        return self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon)
    
    def _get_derived_series_icon(self) -> QIcon:
        """Get icon for derived series items"""
        return self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView)