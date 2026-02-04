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

        # Tentar carregar UI do arquivo .ui
        if not self._load_ui():
            logger.warning("operations_panel_ui_load_failed_using_fallback")
            self._setup_ui_fallback()
        else:
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

    def _setup_ui_fallback(self):
        """Fallback: Setup UI programaticamente se arquivo .ui não carregar"""
        self.setMinimumWidth(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header
        header = QLabel("⚙️ Operações")
        header.setFont(QFont("", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #0d6efd; padding: 4px;")
        layout.addWidget(header)

        # Seletor de série
        series_group = QGroupBox("🎯 Série para Operações")
        series_layout = QVBoxLayout(series_group)
        self._series_combo = QComboBox()
        self._series_combo.addItem("(Nenhum dataset carregado)")
        self._series_combo.setEnabled(False)
        series_layout.addWidget(self._series_combo)
        layout.addWidget(series_group)

        # Tab widget
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, stretch=1)

        # Criar tabs simplificadas
        self._create_interpolation_tab_fallback()
        self._create_calculus_tab_fallback()
        self._create_filters_tab_fallback()
        self._create_sync_tab_fallback()
        self._create_export_tab_fallback()

        # Histórico
        history_group = QGroupBox("📜 Histórico")
        history_layout = QVBoxLayout(history_group)
        self._history_list = QListWidget()
        self._history_list.setMaximumHeight(100)
        history_layout.addWidget(self._history_list)
        self._clear_history_btn = QPushButton("Limpar Histórico")
        history_layout.addWidget(self._clear_history_btn)
        layout.addWidget(history_group)

        logger.debug("operations_panel_ui_fallback_created")

    def _create_interpolation_tab_fallback(self):
        """Cria tab de interpolação (fallback)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        method_group = QGroupBox("Método")
        method_layout = QHBoxLayout(method_group)
        method_layout.addWidget(QLabel("Método:"))
        self._interp_method_combo = QComboBox()
        self._interp_method_combo.addItems([
            "linear", "cubic", "quadratic", "nearest", "zero",
            "slinear", "akima", "pchip", "spline", "polynomial"
        ])
        method_layout.addWidget(self._interp_method_combo)
        layout.addWidget(method_group)
        
        points_group = QGroupBox("Pontos")
        points_layout = QHBoxLayout(points_group)
        points_layout.addWidget(QLabel("Pontos:"))
        self._interp_points_spin = QSpinBox()
        self._interp_points_spin.setRange(10, 100000)
        self._interp_points_spin.setValue(1000)
        points_layout.addWidget(self._interp_points_spin)
        layout.addWidget(points_group)
        
        buttons_layout = QHBoxLayout()
        self._interp_preview_btn = QPushButton("Preview")
        self._interp_apply_btn = QPushButton("Aplicar")
        buttons_layout.addWidget(self._interp_preview_btn)
        buttons_layout.addWidget(self._interp_apply_btn)
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        self._tabs.addTab(tab, "📈 Interpolação")

    def _create_calculus_tab_fallback(self):
        """Cria tab de cálculos (fallback)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        deriv_group = QGroupBox("Derivadas")
        deriv_layout = QHBoxLayout(deriv_group)
        deriv_layout.addWidget(QLabel("Ordem:"))
        self._deriv_order_spin = QSpinBox()
        self._deriv_order_spin.setRange(1, 3)
        self._deriv_order_spin.setValue(1)
        deriv_layout.addWidget(self._deriv_order_spin)
        self._deriv_apply_btn = QPushButton("Calcular")
        deriv_layout.addWidget(self._deriv_apply_btn)
        layout.addWidget(deriv_group)
        
        integral_group = QGroupBox("Integrais")
        integral_layout = QHBoxLayout(integral_group)
        integral_layout.addWidget(QLabel("Método:"))
        self._integral_method_combo = QComboBox()
        self._integral_method_combo.addItems(["trapezoid", "simpson", "cumulative"])
        integral_layout.addWidget(self._integral_method_combo)
        self._integral_apply_btn = QPushButton("Calcular")
        integral_layout.addWidget(self._integral_apply_btn)
        layout.addWidget(integral_group)
        
        layout.addStretch()
        self._tabs.addTab(tab, "📐 Cálculos")

    def _create_filters_tab_fallback(self):
        """Cria tab de filtros (fallback)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        smooth_group = QGroupBox("Suavização")
        smooth_layout = QHBoxLayout(smooth_group)
        smooth_layout.addWidget(QLabel("Método:"))
        self._smooth_method_combo = QComboBox()
        self._smooth_method_combo.addItems(["moving_average", "gaussian", "savgol", "lowess"])
        smooth_layout.addWidget(self._smooth_method_combo)
        smooth_layout.addWidget(QLabel("Janela:"))
        self._smooth_window_spin = QSpinBox()
        self._smooth_window_spin.setRange(3, 101)
        self._smooth_window_spin.setSingleStep(2)
        self._smooth_window_spin.setValue(5)
        smooth_layout.addWidget(self._smooth_window_spin)
        layout.addWidget(smooth_group)
        
        butter_group = QGroupBox("Butterworth")
        butter_layout = QVBoxLayout(butter_group)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo:"))
        self._butter_type_combo = QComboBox()
        self._butter_type_combo.addItems(["lowpass", "highpass", "bandpass", "bandstop"])
        type_layout.addWidget(self._butter_type_combo)
        butter_layout.addLayout(type_layout)
        
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("Ordem:"))
        self._butter_order_spin = QSpinBox()
        self._butter_order_spin.setRange(1, 10)
        self._butter_order_spin.setValue(4)
        params_layout.addWidget(self._butter_order_spin)
        params_layout.addWidget(QLabel("Cutoff:"))
        self._butter_cutoff_spin = QDoubleSpinBox()
        self._butter_cutoff_spin.setRange(0.001, 1000)
        self._butter_cutoff_spin.setValue(10)
        self._butter_cutoff_spin.setSuffix(" Hz")
        params_layout.addWidget(self._butter_cutoff_spin)
        butter_layout.addLayout(params_layout)
        
        layout.addWidget(butter_group)
        
        buttons_layout = QHBoxLayout()
        self._filter_preview_btn = QPushButton("Preview")
        self._filter_apply_btn = QPushButton("Aplicar")
        buttons_layout.addWidget(self._filter_preview_btn)
        buttons_layout.addWidget(self._filter_apply_btn)
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        self._tabs.addTab(tab, "🔧 Filtros")

    def _create_sync_tab_fallback(self):
        """Cria tab de sincronização (fallback)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        method_group = QGroupBox("Método de Sincronização")
        method_layout = QHBoxLayout(method_group)
        method_layout.addWidget(QLabel("Método:"))
        self._sync_method_combo = QComboBox()
        self._sync_method_combo.addItems(["common_grid_interpolate", "kalman_align", "dtw_align"])
        method_layout.addWidget(self._sync_method_combo)
        layout.addWidget(method_group)
        
        freq_group = QGroupBox("Frequência")
        freq_layout = QHBoxLayout(freq_group)
        freq_layout.addWidget(QLabel("Freq. Alvo:"))
        self._target_freq_spin = QDoubleSpinBox()
        self._target_freq_spin.setRange(0.001, 1000)
        self._target_freq_spin.setValue(1.0)
        self._target_freq_spin.setSuffix(" Hz")
        freq_layout.addWidget(self._target_freq_spin)
        layout.addWidget(freq_group)
        
        self._sync_apply_btn = QPushButton("Sincronizar Séries")
        layout.addWidget(self._sync_apply_btn)
        
        layout.addStretch()
        self._tabs.addTab(tab, "🔄 Sincronização")

    def _create_export_tab_fallback(self):
        """Cria tab de export (fallback)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        format_group = QGroupBox("Formato")
        format_layout = QHBoxLayout(format_group)
        format_layout.addWidget(QLabel("Formato:"))
        self._export_format_combo = QComboBox()
        self._export_format_combo.addItems(["CSV", "Excel", "Parquet", "HDF5", "JSON"])
        format_layout.addWidget(self._export_format_combo)
        layout.addWidget(format_group)
        
        options_group = QGroupBox("Opções")
        options_layout = QVBoxLayout(options_group)
        self._export_header_check = QCheckBox("Incluir cabeçalho")
        self._export_header_check.setChecked(True)
        options_layout.addWidget(self._export_header_check)
        self._export_metadata_check = QCheckBox("Incluir metadados")
        options_layout.addWidget(self._export_metadata_check)
        self._export_compress_check = QCheckBox("Comprimir arquivo")
        options_layout.addWidget(self._export_compress_check)
        layout.addWidget(options_group)
        
        self._export_btn = QPushButton("Exportar...")
        layout.addWidget(self._export_btn)
        
        layout.addStretch()
        self._tabs.addTab(tab, "💾 Export")

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
