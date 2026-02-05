"""
Enhanced DataPanel with Multi-File Excel Loading
Original implementation for Platform Base v2.0
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List
from pathlib import Path

import pandas as pd
import numpy as np
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QLabel, QCheckBox, QProgressBar
)

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub

logger = get_logger(__name__)


class EnhancedDataPanel(QWidget):
    """
    Enhanced data panel with:
    - Multi-file Excel loading
    - Dataset tree view
    - Series selection for plotting
    """
    
    def __init__(self, session_state: SessionState, signal_hub: SignalHub, parent=None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.signal_hub = signal_hub
        
        self.loaded_datasets: dict = {}
        
        self._build_interface()
        
        logger.info("EnhancedDataPanel initialized")
        
    def _build_interface(self):
        """Build panel interface"""
        layout = QVBoxLayout(self)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("📁 Carregar Excel")
        self.load_btn.clicked.connect(self._load_excel_files)
        self.load_btn.setToolTip("Selecionar múltiplos arquivos Excel")
        button_layout.addWidget(self.load_btn)
        
        self.load_multi_btn = QPushButton("📚 Carregar Múltiplos")
        self.load_multi_btn.clicked.connect(lambda: self._load_excel_files(multi=True))
        self.load_multi_btn.setToolTip("Carregar múltiplos arquivos de uma vez")
        button_layout.addWidget(self.load_multi_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpar")
        self.clear_btn.clicked.connect(self._clear_all_data)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Nenhum arquivo carregado")
        layout.addWidget(self.status_label)
        
        # Dataset tree
        tree_label = QLabel("Datasets e Séries:")
        layout.addWidget(tree_label)
        
        self.dataset_tree = QTreeWidget()
        self.dataset_tree.setHeaderLabels(["Nome", "Pontos", "Tipo"])
        self.dataset_tree.setColumnWidth(0, 250)
        self.dataset_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.dataset_tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.dataset_tree)
        
        # Actions
        action_layout = QHBoxLayout()
        
        self.plot_selected_btn = QPushButton("📊 Plotar Selecionados")
        self.plot_selected_btn.clicked.connect(self._plot_selected_series)
        action_layout.addWidget(self.plot_selected_btn)
        
        self.remove_selected_btn = QPushButton("❌ Remover Selecionados")
        self.remove_selected_btn.clicked.connect(self._remove_selected)
        action_layout.addWidget(self.remove_selected_btn)
        
        layout.addLayout(action_layout)
        
    def _load_excel_files(self, multi: bool = False):
        """Load Excel file(s)"""
        if multi:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "Selecionar Arquivos Excel",
                "", "Arquivos Excel (*.xlsx *.xls)"
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Selecionar Arquivo Excel",
                "", "Arquivos Excel (*.xlsx *.xls)"
            )
            file_paths = [file_path] if file_path else []
            
        if not file_paths:
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(file_paths))
        self.progress_bar.setValue(0)
        
        loaded_count = 0
        
        for idx, file_path in enumerate(file_paths):
            try:
                self._load_single_excel(file_path)
                loaded_count += 1
            except Exception as e:
                logger.exception(f"Failed to load {file_path}", error=str(e))
                QMessageBox.warning(
                    self, "Erro",
                    f"Falha ao carregar {Path(file_path).name}:\n{str(e)}"
                )
                
            self.progress_bar.setValue(idx + 1)
            
        self.progress_bar.setVisible(False)
        
        self.status_label.setText(
            f"{loaded_count} arquivo(s) carregado(s) - "
            f"Total: {len(self.loaded_datasets)} dataset(s)"
        )
        
        logger.info(f"Loaded {loaded_count} files successfully")
        
    def _load_single_excel(self, file_path: str):
        """Load a single Excel file"""
        df = pd.read_excel(file_path)
        
        # Validate structure
        if len(df.columns) < 2:
            raise ValueError("Excel deve ter pelo menos 2 colunas (tempo e valor)")
            
        # Get dataset name from filename
        dataset_name = Path(file_path).stem
        
        # Parse time column (first column)
        time_col = df.columns[0]
        value_col = df.columns[1]
        
        # Convert time to numeric (seconds from first timestamp)
        if pd.api.types.is_datetime64_any_dtype(df[time_col]):
            time_data = (df[time_col] - df[time_col].iloc[0]).dt.total_seconds().values
            datetime_original = df[time_col].values
        else:
            time_data = df[time_col].values
            datetime_original = None
            
        value_data = df[value_col].values
        
        # Store dataset
        dataset_id = f"ds_{len(self.loaded_datasets)}"
        self.loaded_datasets[dataset_id] = {
            'name': dataset_name,
            'file_path': file_path,
            'time_data': time_data,
            'value_data': value_data,
            'datetime_original': datetime_original,
            'dataframe': df
        }
        
        # Add to tree
        self._add_dataset_to_tree(dataset_id, dataset_name, len(time_data))
        
        # Store in session state
        if self.session_state:
            # You would add proper dataset storage here
            pass
            
        logger.debug(f"Loaded dataset: {dataset_name} with {len(time_data)} points")
        
    def _add_dataset_to_tree(self, dataset_id: str, dataset_name: str, num_points: int):
        """Add dataset to tree widget"""
        dataset_item = QTreeWidgetItem(self.dataset_tree)
        dataset_item.setText(0, dataset_name)
        dataset_item.setText(1, str(num_points))
        dataset_item.setText(2, "Dataset")
        dataset_item.setData(0, Qt.ItemDataRole.UserRole, dataset_id)
        dataset_item.setCheckState(0, Qt.CheckState.Unchecked)
        
        # Add series as children
        series_item = QTreeWidgetItem(dataset_item)
        series_item.setText(0, "valor")
        series_item.setText(1, str(num_points))
        series_item.setText(2, "Série")
        series_item.setData(0, Qt.ItemDataRole.UserRole, f"{dataset_id}_valor")
        series_item.setCheckState(0, Qt.CheckState.Unchecked)
        
        dataset_item.setExpanded(True)
        
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double-click - plot the series"""
        item_type = item.text(2)
        
        if item_type == "Série":
            # Get dataset and series info
            series_id = item.data(0, Qt.ItemDataRole.UserRole)
            dataset_id = series_id.rsplit('_', 1)[0]
            
            if dataset_id in self.loaded_datasets:
                self._plot_series(dataset_id)
                
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        # Propagate checkbox state to children
        if column == 0 and item.childCount() > 0:
            check_state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, check_state)
                
    def _plot_series(self, dataset_id: str):
        """Plot series on visualization panel"""
        if dataset_id not in self.loaded_datasets:
            return
            
        dataset = self.loaded_datasets[dataset_id]
        
        # Emit signal to visualization panel
        if self.signal_hub:
            self.signal_hub.series_selected.emit(dataset_id, "valor")
            
        logger.debug(f"Plotting series from {dataset_id}")
        
    def _plot_selected_series(self):
        """Plot all selected series"""
        selected_items = self._get_checked_items()
        
        for item in selected_items:
            if item.text(2) == "Série":
                series_id = item.data(0, Qt.ItemDataRole.UserRole)
                dataset_id = series_id.rsplit('_', 1)[0]
                self._plot_series(dataset_id)
                
        logger.info(f"Plotted {len(selected_items)} series")
        
    def _get_checked_items(self) -> List[QTreeWidgetItem]:
        """Get all checked items from tree"""
        checked_items = []
        
        for i in range(self.dataset_tree.topLevelItemCount()):
            dataset_item = self.dataset_tree.topLevelItem(i)
            
            # Check children
            for j in range(dataset_item.childCount()):
                child = dataset_item.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    checked_items.append(child)
                    
        return checked_items
        
    def _remove_selected(self):
        """Remove selected datasets"""
        selected_items = self._get_checked_items()
        
        if not selected_items:
            QMessageBox.information(self, "Aviso", "Nenhum item selecionado")
            return
            
        reply = QMessageBox.question(
            self, "Confirmar",
            f"Remover {len(selected_items)} item(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from tree
            for item in selected_items:
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                    
            # Remove empty datasets
            for i in reversed(range(self.dataset_tree.topLevelItemCount())):
                dataset_item = self.dataset_tree.topLevelItem(i)
                if dataset_item.childCount() == 0:
                    dataset_id = dataset_item.data(0, Qt.ItemDataRole.UserRole)
                    if dataset_id in self.loaded_datasets:
                        del self.loaded_datasets[dataset_id]
                    self.dataset_tree.takeTopLevelItem(i)
                    
            self.status_label.setText(f"Total: {len(self.loaded_datasets)} dataset(s)")
            
    def _clear_all_data(self):
        """Clear all loaded data"""
        reply = QMessageBox.question(
            self, "Confirmar",
            "Limpar todos os dados carregados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.loaded_datasets.clear()
            self.dataset_tree.clear()
            self.status_label.setText("Nenhum arquivo carregado")
            logger.info("All data cleared")
            
    def get_dataset_data(self, dataset_id: str):
        """Get data for a specific dataset"""
        return self.loaded_datasets.get(dataset_id)
