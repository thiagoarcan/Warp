"""
OperationsPanel - Painel de operações matemáticas (versão UI)

Interface carregada de: desktop/ui_files/operationsPanel.ui

Funcionalidades:
- Tabs: Interpolação, Cálculos (Derivadas/Integrais), Filtros, Sincronização, Export
- Histórico de operações
- Configuração de parâmetros
- Preview em tempo real

Este módulo usa UiLoaderMixin para carregar a interface do arquivo .ui.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


@dataclass
class OperationHistoryItem:
    """Item do histórico de operações"""
    operation_name: str
    params: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    result_info: str = ""


class OperationsPanel(QWidget, UiLoaderMixin):
    """
    Painel de operações completo com tabs e histórico.

    Interface carregada do arquivo .ui via UiLoaderMixin.

    Características:
    - Tab Interpolação: 10 métodos disponíveis
    - Tab Cálculos: Derivadas (1ª/2ª/3ª), Integrais, Área
    - Tab Filtros: Suavização, Butterworth
    - Tab Sincronização: Alinhamento de séries
    - Tab Export: CSV, Excel, Parquet, HDF5, JSON
    - Histórico: Últimas 50 operações
    """

    # Arquivo .ui que define a interface
    UI_FILE = "operationsPanel.ui"

    # Signals
    operation_requested = pyqtSignal(str, dict)  # operation_name, params
    export_requested = pyqtSignal(str, dict)     # format, options

    def __init__(
        self,
        session_state: SessionState,
        signal_hub: SignalHub | None = None,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self.session_state = session_state
        self.signal_hub = signal_hub
        self._history: list[OperationHistoryItem] = []
        self._max_history = 50

        # Carregar UI do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

        self._connect_signals()
        logger.debug("operations_panel_initialized")

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Os widgets já existem como atributos (criados pelo uic.loadUi)
        # Apenas precisamos configurar conexões e comportamentos adicionais
        
        # Buscar widgets do .ui
        self._tabs = self.findChild(QTabWidget, "operationTabs")
        self._series_combo = self.findChild(QComboBox, "seriesCombo")
        self._history_list = self.findChild(QListWidget, "historyList")
        
        # Tab Interpolação
        self._interp_method_combo = self.findChild(QComboBox, "interpMethodCombo")
        self._interp_points_spin = self.findChild(QSpinBox, "interpPointsSpin")
        self._interp_preview_btn = self.findChild(QPushButton, "interpPreviewBtn")
        self._interp_apply_btn = self.findChild(QPushButton, "interpApplyBtn")
        
        # Tab Cálculos
        self._deriv_order_spin = self.findChild(QSpinBox, "derivOrderSpin")
        self._deriv_apply_btn = self.findChild(QPushButton, "derivApplyBtn")
        self._integral_method_combo = self.findChild(QComboBox, "integralMethodCombo")
        self._integral_apply_btn = self.findChild(QPushButton, "integralApplyBtn")
        
        # Tab Filtros
        self._smooth_method_combo = self.findChild(QComboBox, "smoothMethodCombo")
        self._smooth_window_spin = self.findChild(QSpinBox, "smoothWindowSpin")
        self._butter_type_combo = self.findChild(QComboBox, "butterTypeCombo")
        self._butter_order_spin = self.findChild(QSpinBox, "butterOrderSpin")
        self._butter_cutoff_spin = self.findChild(QDoubleSpinBox, "butterCutoffSpin")
        self._filter_preview_btn = self.findChild(QPushButton, "filterPreviewBtn")
        self._filter_apply_btn = self.findChild(QPushButton, "filterApplyBtn")
        
        # Tab Sincronização
        self._sync_method_combo = self.findChild(QComboBox, "syncMethodCombo")
        self._target_freq_spin = self.findChild(QDoubleSpinBox, "targetFreqSpin")
        self._sync_apply_btn = self.findChild(QPushButton, "syncApplyBtn")
        
        # Tab Export
        self._export_format_combo = self.findChild(QComboBox, "exportFormatCombo")
        self._export_header_check = self.findChild(QCheckBox, "exportHeaderCheck")
        self._export_metadata_check = self.findChild(QCheckBox, "exportMetadataCheck")
        self._export_compress_check = self.findChild(QCheckBox, "exportCompressCheck")
        self._export_btn = self.findChild(QPushButton, "exportBtn")
        
        # Histórico
        self._clear_history_btn = self.findChild(QPushButton, "clearHistoryBtn")
        
        # Inicializar estado
        if self._series_combo:
            self._series_combo.addItem("(Nenhum dataset carregado)")
            self._series_combo.setEnabled(False)
        
        logger.debug("operations_panel_ui_loaded_from_file")

    def _connect_signals(self):
        """Conecta signals dos widgets"""
        # Interpolação
        if self._interp_preview_btn:
            self._interp_preview_btn.clicked.connect(self._preview_interpolation)
        if self._interp_apply_btn:
            self._interp_apply_btn.clicked.connect(self._apply_interpolation)
        
        # Cálculos
        if self._deriv_apply_btn:
            self._deriv_apply_btn.clicked.connect(self._apply_derivative)
        if self._integral_apply_btn:
            self._integral_apply_btn.clicked.connect(self._apply_integral)
        
        # Filtros
        if self._filter_preview_btn:
            self._filter_preview_btn.clicked.connect(self._preview_filter)
        if self._filter_apply_btn:
            self._filter_apply_btn.clicked.connect(self._apply_filter)
        
        # Sincronização
        if self._sync_apply_btn:
            self._sync_apply_btn.clicked.connect(self._apply_sync)
        
        # Export
        if self._export_btn:
            self._export_btn.clicked.connect(self._export_data)
        
        # Histórico
        if self._clear_history_btn:
            self._clear_history_btn.clicked.connect(self._clear_history)
        
        # SignalHub
        if self.signal_hub:
            self.signal_hub.dataset_loaded.connect(self._on_dataset_loaded)
            self.signal_hub.series_selected.connect(self._on_series_selected)

    # ========================
    # Slots de operações
    # ========================

    @pyqtSlot()
    def _preview_interpolation(self):
        """Preview da interpolação"""
        if not self._validate_series_selection():
            return
        params = self._get_interpolation_params()
        self.operation_requested.emit("interpolation_preview", params)

    @pyqtSlot()
    def _apply_interpolation(self):
        """Aplica interpolação"""
        if not self._validate_series_selection():
            return
        params = self._get_interpolation_params()
        self.operation_requested.emit("interpolation", params)
        self._add_to_history("interpolation", params)

    @pyqtSlot()
    def _apply_derivative(self):
        """Aplica derivada"""
        if not self._validate_series_selection():
            return
        order = self._deriv_order_spin.value() if self._deriv_order_spin else 1
        params = {"order": order}
        self.operation_requested.emit("derivative", params)
        self._add_to_history("derivative", params)

    @pyqtSlot()
    def _apply_integral(self):
        """Aplica integral"""
        if not self._validate_series_selection():
            return
        method = self._integral_method_combo.currentText() if self._integral_method_combo else "trapezoid"
        params = {"method": method}
        self.operation_requested.emit("integral", params)
        self._add_to_history("integral", params)

    @pyqtSlot()
    def _preview_filter(self):
        """Preview do filtro"""
        if not self._validate_series_selection():
            return
        params = self._get_filter_params()
        self.operation_requested.emit("filter_preview", params)

    @pyqtSlot()
    def _apply_filter(self):
        """Aplica filtro"""
        if not self._validate_series_selection():
            return
        params = self._get_filter_params()
        self.operation_requested.emit("filter", params)
        self._add_to_history("filter", params)

    @pyqtSlot()
    def _apply_sync(self):
        """Aplica sincronização"""
        method = self._sync_method_combo.currentText() if self._sync_method_combo else "common_grid_interpolate"
        freq = self._target_freq_spin.value() if self._target_freq_spin else 1.0
        params = {"method": method, "target_frequency": freq}
        self.operation_requested.emit("synchronization", params)
        self._add_to_history("synchronization", params)

    @pyqtSlot()
    def _export_data(self):
        """Exporta dados"""
        format_name = self._export_format_combo.currentText() if self._export_format_combo else "CSV"
        options = {
            "include_header": self._export_header_check.isChecked() if self._export_header_check else True,
            "include_metadata": self._export_metadata_check.isChecked() if self._export_metadata_check else False,
            "compress": self._export_compress_check.isChecked() if self._export_compress_check else False,
        }
        self.export_requested.emit(format_name, options)

    @pyqtSlot()
    def _clear_history(self):
        """Limpa histórico"""
        self._history.clear()
        if self._history_list:
            self._history_list.clear()

    # ========================
    # Helpers
    # ========================

    def _validate_series_selection(self) -> bool:
        """Valida se uma série está selecionada"""
        if not self._series_combo or not self._series_combo.isEnabled():
            QMessageBox.warning(self, "Aviso", "Nenhum dataset carregado.")
            return False
        if self._series_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma série.")
            return False
        return True

    def _get_interpolation_params(self) -> dict[str, Any]:
        """Retorna parâmetros de interpolação"""
        return {
            "method": self._interp_method_combo.currentText() if self._interp_method_combo else "linear",
            "num_points": self._interp_points_spin.value() if self._interp_points_spin else 1000,
        }

    def _get_filter_params(self) -> dict[str, Any]:
        """Retorna parâmetros de filtro"""
        return {
            "smoothing_method": self._smooth_method_combo.currentText() if self._smooth_method_combo else "moving_average",
            "window_size": self._smooth_window_spin.value() if self._smooth_window_spin else 5,
            "butter_type": self._butter_type_combo.currentText() if self._butter_type_combo else "lowpass",
            "butter_order": self._butter_order_spin.value() if self._butter_order_spin else 4,
            "butter_cutoff": self._butter_cutoff_spin.value() if self._butter_cutoff_spin else 10.0,
        }

    def _add_to_history(self, operation_name: str, params: dict[str, Any]):
        """Adiciona operação ao histórico"""
        item = OperationHistoryItem(operation_name=operation_name, params=params)
        self._history.insert(0, item)
        
        # Limitar tamanho
        if len(self._history) > self._max_history:
            self._history = self._history[:self._max_history]
        
        # Atualizar lista visual
        if self._history_list:
            list_item = QListWidgetItem(f"{item.timestamp.strftime('%H:%M:%S')} - {operation_name}")
            self._history_list.insertItem(0, list_item)
            if self._history_list.count() > self._max_history:
                self._history_list.takeItem(self._history_list.count() - 1)

    @pyqtSlot(str)
    def _on_dataset_loaded(self, dataset_id: str):
        """Callback quando dataset é carregado"""
        if self._series_combo:
            self._series_combo.setEnabled(True)
            self._series_combo.clear()
            # Adicionar séries do dataset
            if self.session_state and hasattr(self.session_state, 'dataset_store'):
                dataset = self.session_state.dataset_store.get(dataset_id)
                if dataset:
                    for series_id in dataset.series_ids:
                        self._series_combo.addItem(series_id)

    @pyqtSlot(str)
    def _on_series_selected(self, series_id: str):
        """Callback quando série é selecionada"""
        if self._series_combo:
            index = self._series_combo.findText(series_id)
            if index >= 0:
                self._series_combo.setCurrentIndex(index)
