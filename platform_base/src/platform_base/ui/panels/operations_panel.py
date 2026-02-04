"""
OperationsPanel - Painel completo de operações matemáticas

Funcionalidades:
- Tabs: Interpolação, Cálculos (Derivadas/Integrais), Filtros, Export
- Histórico de operações
- Configuração de parâmetros
- Preview em tempo real
- Integração com SessionState
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QFont
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
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.preview_dialog import OperationPreviewDialog
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.ui.state import SessionState


logger = get_logger(__name__)


class StableComboBox(QComboBox):
    """
    ComboBox estável que não fecha automaticamente no Windows.
    
    Solução para o problema de QWindowsWindow::setMouseGrabEnabled.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(30)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMaxVisibleItems(20)
        
        # Configurações específicas para Windows
        self.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #0d6efd;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #ced4da;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                selection-background-color: #0d6efd;
                selection-color: white;
                background-color: white;
            }
        """)
        
        # Desabilitar context menu para evitar interferências
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
    def showPopup(self):
        """Override para garantir que o popup seja mostrado corretamente"""
        super().showPopup()
        # Garantir que o popup não seja fechado imediatamente
        self.view().setFocus()
        
    def focusOutEvent(self, event):
        """Evitar fechamento prematuro do popup"""
        # Não propagar se o popup estiver visível
        if self.view().isVisible():
            return
        super().focusOutEvent(event)


class OperationHistoryItem:
    """Item do histórico de operações"""
    def __init__(self, operation: str, params: dict[str, Any], timestamp: datetime | None = None):
        self.operation = operation
        self.params = params
        self.timestamp = timestamp or datetime.now()
        self.success = True
        self.result_info = ""


class OperationsPanel(QWidget):
    """
    Painel de operações completo com tabs e histórico

    Características:
    - Tab Interpolação: 10 métodos disponíveis
    - Tab Cálculos: Derivadas (1ª/2ª/3ª), Integrais, Área
    - Tab Filtros: Suavização, Butterworth, Outliers
    - Tab Export: CSV, Excel, Parquet, HDF5, JSON
    - Histórico: Últimas 50 operações
    """

    # Signals
    operation_requested = pyqtSignal(str, dict)  # operation_name, params
    export_requested = pyqtSignal(str, dict)     # format, options

    def __init__(self, session_state: SessionState):
        super().__init__()

        self.session_state = session_state
        self._history: list[OperationHistoryItem] = []
        self._max_history = 50

        self._setup_ui()
        self._setup_connections()

        logger.debug("operations_panel_initialized")

    def _create_combo_box(self) -> StableComboBox:
        """Cria um ComboBox estável que não fecha automaticamente"""
        return StableComboBox()
    
    def _setup_ui(self):
        """Configura interface completa"""
        self.setMinimumWidth(200)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Styling moderno
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 2px 6px;
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QPushButton[objectName="secondary"] {
                background-color: #6c757d;
            }
            QPushButton[objectName="success"] {
                background-color: #198754;
            }
            QSpinBox, QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                min-height: 24px;
            }
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                min-height: 24px;
            }
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 6px 10px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
        """)

        # Header
        header = QLabel("⚙️ Operações")
        header.setFont(QFont("", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #0d6efd; padding: 4px;")
        layout.addWidget(header)

        # === SELETOR DE SÉRIE GLOBAL ===
        series_group = QGroupBox("🎯 Série para Operações")
        series_layout = QFormLayout(series_group)
        series_layout.setContentsMargins(6, 10, 6, 6)
        
        self._series_combo = self._create_combo_box()
        self._series_combo.setMinimumWidth(150)
        self._series_combo.setToolTip("Selecione a série para aplicar as operações")
        self._series_combo.addItem("(Nenhum dataset carregado)")
        self._series_combo.setEnabled(False)
        series_layout.addRow("Série:", self._series_combo)
        layout.addWidget(series_group)

        # Tab widget principal
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(self._tabs, stretch=1)

        # Criar tabs
        self._create_interpolation_tab()
        self._create_calculus_tab()
        self._create_filters_tab()
        self._create_sync_tab()  # Tab de sincronização
        self._create_streaming_tab()  # Tab de streaming
        self._create_export_tab()
        self._create_settings_tab()  # Tab de configuração
        self._create_history_tab()

    def _create_interpolation_tab(self):
        """Tab de interpolação"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # Método de interpolação
        method_group = QGroupBox("📐 Método")
        method_layout = QFormLayout(method_group)

        self._interp_method = self._create_combo_box()
        self._interp_method.addItems([
            "linear", "cubic_spline", "smoothing_spline",
            "akima", "pchip", "polynomial",
            "mls", "gpr", "lomb_scargle", "resample_grid",
        ])
        self._interp_method.setToolTip("Método de interpolação a utilizar")
        method_layout.addRow("Método:", self._interp_method)

        layout.addWidget(method_group)

        # Parâmetros
        params_group = QGroupBox("🔧 Parâmetros")
        params_layout = QFormLayout(params_group)

        self._interp_points = QSpinBox()
        self._interp_points.setRange(10, 100000)
        self._interp_points.setValue(1000)
        self._interp_points.setToolTip("Número de pontos de saída")
        params_layout.addRow("Pontos:", self._interp_points)

        self._interp_smooth = QDoubleSpinBox()
        self._interp_smooth.setRange(0.0, 1.0)
        self._interp_smooth.setSingleStep(0.01)
        self._interp_smooth.setValue(0.0)
        self._interp_smooth.setToolTip("Fator de suavização (0 = nenhuma)")
        params_layout.addRow("Suavização:", self._interp_smooth)

        self._interp_degree = QSpinBox()
        self._interp_degree.setRange(1, 10)
        self._interp_degree.setValue(3)
        self._interp_degree.setToolTip("Grau do polinômio (para métodos polinomiais)")
        params_layout.addRow("Grau:", self._interp_degree)

        self._interp_extrapolate = QCheckBox("Permitir extrapolação")
        self._interp_extrapolate.setToolTip("Extrapolar além do range dos dados")
        params_layout.addRow(self._interp_extrapolate)

        layout.addWidget(params_group)

        # Botões de ação
        btn_layout = QHBoxLayout()

        preview_btn = QPushButton("👁️ Preview")
        preview_btn.setToolTip("Visualizar resultado antes de aplicar")
        preview_btn.clicked.connect(self._preview_interpolation)
        btn_layout.addWidget(preview_btn)

        apply_btn = QPushButton("✅ Aplicar")
        apply_btn.setObjectName("success")
        apply_btn.setToolTip("Aplicar interpolação à série selecionada")
        apply_btn.clicked.connect(self._apply_interpolation)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "📐")

    def _create_calculus_tab(self):
        """Tab de cálculos matemáticos"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # === DERIVADAS ===
        deriv_group = QGroupBox("📈 Derivadas")
        deriv_layout = QFormLayout(deriv_group)

        self._deriv_order = self._create_combo_box()
        self._deriv_order.addItems(["1ª Ordem", "2ª Ordem", "3ª Ordem"])
        self._deriv_order.setToolTip("Ordem da derivada")
        deriv_layout.addRow("Ordem:", self._deriv_order)

        self._deriv_method = self._create_combo_box()
        self._deriv_method.addItems(["finite_diff", "savitzky_golay", "spline_derivative"])
        self._deriv_method.setToolTip("Método de cálculo da derivada")
        deriv_layout.addRow("Método:", self._deriv_method)

        self._deriv_window = QSpinBox()
        self._deriv_window.setRange(3, 51)
        self._deriv_window.setValue(7)
        self._deriv_window.setSingleStep(2)
        self._deriv_window.setToolTip("Tamanho da janela (para Savitzky-Golay)")
        deriv_layout.addRow("Janela:", self._deriv_window)

        self._deriv_smooth = QCheckBox("Suavizar antes")
        self._deriv_smooth.setToolTip("Aplicar suavização antes de derivar")
        deriv_layout.addRow(self._deriv_smooth)

        deriv_btn = QPushButton("📊 Calcular Derivada")
        deriv_btn.setToolTip("Calcular derivada da série selecionada")
        deriv_btn.clicked.connect(self._calculate_derivative)

        deriv_preview_btn = QPushButton("👁️ Preview")
        deriv_preview_btn.setToolTip("Visualizar derivada antes de aplicar")
        deriv_preview_btn.setObjectName("secondary")
        deriv_preview_btn.clicked.connect(self._preview_derivative)

        deriv_btn_layout = QHBoxLayout()
        deriv_btn_layout.addWidget(deriv_preview_btn)
        deriv_btn_layout.addWidget(deriv_btn)
        deriv_layout.addRow(deriv_btn_layout)

        layout.addWidget(deriv_group)

        # === INTEGRAIS ===
        integ_group = QGroupBox("∫ Integrais")
        integ_layout = QFormLayout(integ_group)

        self._integ_method = self._create_combo_box()
        self._integ_method.addItems(["trapezoid", "simpson", "cumulative"])
        self._integ_method.setToolTip("Método de integração numérica")
        integ_layout.addRow("Método:", self._integ_method)

        integ_btn = QPushButton("📊 Calcular Integral")
        integ_btn.setToolTip("Calcular integral da série selecionada")
        integ_btn.clicked.connect(self._calculate_integral)

        integ_preview_btn = QPushButton("👁️ Preview")
        integ_preview_btn.setToolTip("Visualizar integral antes de aplicar")
        integ_preview_btn.setObjectName("secondary")
        integ_preview_btn.clicked.connect(self._preview_integral)

        integ_btn_layout = QHBoxLayout()
        integ_btn_layout.addWidget(integ_preview_btn)
        integ_btn_layout.addWidget(integ_btn)
        integ_layout.addRow(integ_btn_layout)

        layout.addWidget(integ_group)

        # === ÁREA ===
        area_group = QGroupBox("📏 Área")
        area_layout = QFormLayout(area_group)

        self._area_type = self._create_combo_box()
        self._area_type.addItems(["Área sob a curva", "Área entre curvas"])
        self._area_type.setToolTip("Tipo de cálculo de área")
        area_layout.addRow("Tipo:", self._area_type)

        area_btn = QPushButton("📊 Calcular Área")
        area_btn.setToolTip("Calcular área sob a curva ou entre curvas")
        area_btn.clicked.connect(self._calculate_area)
        area_layout.addRow(area_btn)

        layout.addWidget(area_group)
        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "🧮")

    def _create_filters_tab(self):
        """Tab de filtros e suavização"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # === SUAVIZAÇÃO ===
        smooth_group = QGroupBox("〰️ Suavização")
        smooth_layout = QFormLayout(smooth_group)

        self._smooth_method = self._create_combo_box()
        self._smooth_method.addItems([
            "gaussian", "moving_average", "savitzky_golay",
            "median", "exponential",
        ])
        self._smooth_method.setToolTip("Método de suavização")
        smooth_layout.addRow("Método:", self._smooth_method)

        self._smooth_window = QSpinBox()
        self._smooth_window.setRange(3, 101)
        self._smooth_window.setValue(5)
        self._smooth_window.setSingleStep(2)
        self._smooth_window.setToolTip("Tamanho da janela de suavização")
        smooth_layout.addRow("Janela:", self._smooth_window)

        self._smooth_sigma = QDoubleSpinBox()
        self._smooth_sigma.setRange(0.1, 10.0)
        self._smooth_sigma.setValue(1.0)
        self._smooth_sigma.setToolTip("Sigma para filtro Gaussiano")
        smooth_layout.addRow("Sigma:", self._smooth_sigma)

        smooth_btn = QPushButton("〰️ Aplicar Suavização")
        smooth_btn.setToolTip("Aplicar filtro de suavização à série")
        smooth_btn.clicked.connect(self._apply_smoothing)

        smooth_preview_btn = QPushButton("👁️ Preview")
        smooth_preview_btn.setToolTip("Visualizar suavização antes de aplicar")
        smooth_preview_btn.setObjectName("secondary")
        smooth_preview_btn.clicked.connect(self._preview_smoothing)

        smooth_btn_layout = QHBoxLayout()
        smooth_btn_layout.addWidget(smooth_preview_btn)
        smooth_btn_layout.addWidget(smooth_btn)
        smooth_layout.addRow(smooth_btn_layout)

        layout.addWidget(smooth_group)

        # === REMOÇÃO DE OUTLIERS ===
        outlier_group = QGroupBox("🚫 Outliers")
        outlier_layout = QFormLayout(outlier_group)

        self._outlier_method = self._create_combo_box()
        self._outlier_method.addItems(["zscore", "iqr", "mad"])
        self._outlier_method.setToolTip("Método de detecção de outliers")
        outlier_layout.addRow("Método:", self._outlier_method)

        self._outlier_threshold = QDoubleSpinBox()
        self._outlier_threshold.setRange(1.0, 10.0)
        self._outlier_threshold.setValue(3.0)
        self._outlier_threshold.setToolTip("Limiar para detecção (ex: 3 sigmas)")
        outlier_layout.addRow("Limiar:", self._outlier_threshold)

        outlier_btn = QPushButton("🚫 Remover Outliers")
        outlier_btn.setToolTip("Detectar e remover valores atípicos")
        outlier_btn.clicked.connect(self._remove_outliers)

        outlier_preview_btn = QPushButton("👁️ Preview")
        outlier_preview_btn.setToolTip("Visualizar detecção de outliers")
        outlier_preview_btn.setObjectName("secondary")
        outlier_preview_btn.clicked.connect(self._preview_remove_outliers)

        outlier_btn_layout = QHBoxLayout()
        outlier_btn_layout.addWidget(outlier_preview_btn)
        outlier_btn_layout.addWidget(outlier_btn)
        outlier_layout.addRow(outlier_btn_layout)

        layout.addWidget(outlier_group)

        # === FFT ANALYSIS ===
        fft_group = QGroupBox("📊 FFT Analysis")
        fft_layout = QFormLayout(fft_group)

        self._fft_window = self._create_combo_box()
        self._fft_window.addItems(["hann", "hamming", "blackman", "bartlett", "none"])
        self._fft_window.setToolTip("Window function for FFT")
        fft_layout.addRow("Window:", self._fft_window)

        self._fft_detrend = QCheckBox("Remove Trend")
        self._fft_detrend.setChecked(True)
        self._fft_detrend.setToolTip("Remove linear trend before FFT")
        fft_layout.addRow(self._fft_detrend)

        fft_btn = QPushButton("📊 Compute FFT")
        fft_btn.setToolTip("Calcular Transformada Rápida de Fourier")
        fft_btn.clicked.connect(self._compute_fft)
        fft_layout.addRow(fft_btn)

        layout.addWidget(fft_group)

        # === CORRELATION ANALYSIS ===
        corr_group = QGroupBox("🔗 Correlation")
        corr_layout = QFormLayout(corr_group)

        self._corr_mode = self._create_combo_box()
        self._corr_mode.addItems(["auto", "cross"])
        self._corr_mode.setToolTip("Auto-correlation or cross-correlation")
        corr_layout.addRow("Mode:", self._corr_mode)

        self._corr_normalize = QCheckBox("Normalize")
        self._corr_normalize.setChecked(True)
        self._corr_normalize.setToolTip("Normalize correlation to [-1, 1]")
        corr_layout.addRow(self._corr_normalize)

        corr_btn = QPushButton("🔗 Compute Correlation")
        corr_btn.setToolTip("Calcular auto-correlação ou correlação cruzada")
        corr_btn.clicked.connect(self._compute_correlation)
        corr_layout.addRow(corr_btn)

        layout.addWidget(corr_group)

        # === DIGITAL FILTERS ===
        filters_group = QGroupBox("🎛️ Digital Filters")
        filters_layout = QFormLayout(filters_group)

        self._filter_type = self._create_combo_box()
        self._filter_type.addItems(["lowpass", "highpass", "bandpass", "bandstop"])
        self._filter_type.setToolTip("Filter type")
        self._filter_type.currentTextChanged.connect(self._on_filter_type_changed)
        filters_layout.addRow("Type:", self._filter_type)

        self._filter_cutoff = QDoubleSpinBox()
        self._filter_cutoff.setRange(0.1, 1000.0)
        self._filter_cutoff.setValue(10.0)
        self._filter_cutoff.setToolTip("Cutoff frequency (Hz)")
        self._filter_cutoff_label = QLabel("Cutoff (Hz):")
        filters_layout.addRow(self._filter_cutoff_label, self._filter_cutoff)

        self._filter_cutoff_high = QDoubleSpinBox()
        self._filter_cutoff_high.setRange(0.1, 1000.0)
        self._filter_cutoff_high.setValue(50.0)
        self._filter_cutoff_high.setToolTip("High cutoff frequency (Hz)")
        self._filter_cutoff_high_label = QLabel("High Cutoff (Hz):")
        filters_layout.addRow(self._filter_cutoff_high_label, self._filter_cutoff_high)
        self._filter_cutoff_high.setVisible(False)
        self._filter_cutoff_high_label.setVisible(False)

        self._filter_order = QSpinBox()
        self._filter_order.setRange(1, 10)
        self._filter_order.setValue(4)
        self._filter_order.setToolTip("Filter order (higher = sharper)")
        filters_layout.addRow("Order:", self._filter_order)

        self._filter_method = self._create_combo_box()
        self._filter_method.addItems(["butter", "chebyshev1", "chebyshev2", "elliptic", "bessel"])
        self._filter_method.setToolTip("Filter design method")
        filters_layout.addRow("Method:", self._filter_method)

        filter_btn = QPushButton("🎛️ Apply Filter")
        filter_btn.setToolTip("Aplicar filtro digital à série")
        filter_btn.clicked.connect(self._apply_filter)

        filter_preview_btn = QPushButton("👁️ Preview")
        filter_preview_btn.setToolTip("Visualizar resultado do filtro")
        filter_preview_btn.setObjectName("secondary")
        filter_preview_btn.clicked.connect(self._preview_filter)

        filter_btn_layout = QHBoxLayout()
        filter_btn_layout.addWidget(filter_preview_btn)
        filter_btn_layout.addWidget(filter_btn)
        filters_layout.addRow(filter_btn_layout)

        layout.addWidget(filters_group)

        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "🎚️")

    def _create_sync_tab(self):
        """Tab de sincronização de timestamps entre datasets"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # === SELEÇÃO DE DATASETS ===
        datasets_group = QGroupBox("📊 Datasets para Sincronizar")
        datasets_layout = QVBoxLayout(datasets_group)

        # Lista de datasets disponíveis com checkboxes
        self._sync_datasets_list = QListWidget()
        self._sync_datasets_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self._sync_datasets_list.setToolTip("Selecione os datasets para sincronizar (mínimo 2)")
        self._sync_datasets_list.setMaximumHeight(150)
        datasets_layout.addWidget(self._sync_datasets_list)

        # Botão de atualizar lista
        refresh_btn = QPushButton("🔄 Atualizar Lista")
        refresh_btn.setToolTip("Recarregar lista de datasets disponíveis")
        refresh_btn.clicked.connect(self._refresh_sync_datasets)
        datasets_layout.addWidget(refresh_btn)

        layout.addWidget(datasets_group)

        # === MÉTODO DE SINCRONIZAÇÃO ===
        method_group = QGroupBox("⚙️ Método de Sincronização")
        method_layout = QFormLayout(method_group)

        self._sync_method = self._create_combo_box()
        self._sync_method.addItems([
            "common_grid_interpolate",  # Interpolação para grade comum
            "kalman_align",             # Alinhamento via Kalman
        ])
        self._sync_method.setToolTip(
            "common_grid_interpolate: Interpola todas as séries para uma grade temporal comum\n"
            "kalman_align: Usa filtro de Kalman para alinhamento suave"
        )
        self._sync_method.currentTextChanged.connect(self._on_sync_method_changed)
        method_layout.addRow("Método:", self._sync_method)

        layout.addWidget(method_group)

        # === PARÂMETROS DA GRADE TEMPORAL ===
        grid_group = QGroupBox("📏 Grade Temporal")
        grid_layout = QFormLayout(grid_group)

        self._sync_grid_method = self._create_combo_box()
        self._sync_grid_method.addItems(["median", "min", "max", "mean"])
        self._sync_grid_method.setToolTip(
            "Como calcular o intervalo de tempo (dt):\n"
            "median: Mediana dos intervalos (mais robusto)\n"
            "min: Menor intervalo (mais pontos)\n"
            "max: Maior intervalo (menos pontos)\n"
            "mean: Média dos intervalos"
        )
        grid_layout.addRow("Cálculo dt:", self._sync_grid_method)

        self._sync_dt_fixed = QCheckBox("Usar dt fixo")
        self._sync_dt_fixed.setToolTip("Definir intervalo de tempo manualmente")
        self._sync_dt_fixed.toggled.connect(self._on_sync_dt_fixed_changed)
        grid_layout.addRow(self._sync_dt_fixed)

        self._sync_dt_value = QDoubleSpinBox()
        self._sync_dt_value.setRange(0.001, 1000.0)
        self._sync_dt_value.setValue(1.0)
        self._sync_dt_value.setDecimals(3)
        self._sync_dt_value.setSuffix(" s")
        self._sync_dt_value.setToolTip("Intervalo de tempo fixo em segundos")
        self._sync_dt_value.setEnabled(False)
        grid_layout.addRow("dt fixo:", self._sync_dt_value)

        layout.addWidget(grid_group)

        # === PARÂMETROS DE INTERPOLAÇÃO ===
        interp_group = QGroupBox("📐 Interpolação")
        interp_layout = QFormLayout(interp_group)

        self._sync_interp_method = self._create_combo_box()
        self._sync_interp_method.addItems(["linear", "cubic", "nearest"])
        self._sync_interp_method.setToolTip(
            "Método de interpolação para grade comum:\n"
            "linear: Interpolação linear (rápido)\n"
            "cubic: Spline cúbica (suave)\n"
            "nearest: Vizinho mais próximo (preserva valores)"
        )
        interp_layout.addRow("Método:", self._sync_interp_method)

        layout.addWidget(interp_group)

        # === PARÂMETROS KALMAN (ocultos por padrão) ===
        self._kalman_group = QGroupBox("🎯 Filtro Kalman")
        kalman_layout = QFormLayout(self._kalman_group)

        self._sync_process_noise = QDoubleSpinBox()
        self._sync_process_noise.setRange(0.0001, 1.0)
        self._sync_process_noise.setValue(0.01)
        self._sync_process_noise.setDecimals(4)
        self._sync_process_noise.setToolTip("Ruído do processo (menor = mais suave)")
        kalman_layout.addRow("Process Noise:", self._sync_process_noise)

        self._sync_measurement_noise = QDoubleSpinBox()
        self._sync_measurement_noise.setRange(0.001, 10.0)
        self._sync_measurement_noise.setValue(0.1)
        self._sync_measurement_noise.setDecimals(3)
        self._sync_measurement_noise.setToolTip("Ruído da medição (menor = mais confiança nos dados)")
        kalman_layout.addRow("Measurement Noise:", self._sync_measurement_noise)

        self._kalman_group.setVisible(False)
        layout.addWidget(self._kalman_group)

        # === OPÇÕES DE SAÍDA ===
        output_group = QGroupBox("📤 Saída")
        output_layout = QVBoxLayout(output_group)

        self._sync_create_new = QCheckBox("Criar novo dataset sincronizado")
        self._sync_create_new.setChecked(True)
        self._sync_create_new.setToolTip("Criar um novo dataset com todas as séries sincronizadas")
        output_layout.addWidget(self._sync_create_new)

        self._sync_keep_original = QCheckBox("Manter datasets originais")
        self._sync_keep_original.setChecked(True)
        self._sync_keep_original.setToolTip("Não modificar os datasets originais")
        output_layout.addWidget(self._sync_keep_original)

        layout.addWidget(output_group)

        # === BOTÕES DE AÇÃO ===
        btn_layout = QHBoxLayout()

        preview_btn = QPushButton("👁️ Preview")
        preview_btn.setToolTip("Visualizar resultado da sincronização")
        preview_btn.clicked.connect(self._preview_sync)
        btn_layout.addWidget(preview_btn)

        apply_btn = QPushButton("🔗 Sincronizar")
        apply_btn.setObjectName("success")
        apply_btn.setToolTip("Aplicar sincronização aos datasets selecionados")
        apply_btn.clicked.connect(self._apply_sync)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

        # === INFO ===
        info_label = QLabel(
            "💡 A sincronização alinha múltiplos datasets para uma\n"
            "grade temporal comum, permitindo comparações diretas."
        )
        info_label.setStyleSheet("color: #6c757d; font-size: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "🔗")

        # Inicializar lista de datasets
        QTimer.singleShot(100, self._refresh_sync_datasets)

    def _on_sync_method_changed(self, method: str):
        """Mostra/oculta parâmetros Kalman conforme método selecionado"""
        self._kalman_group.setVisible(method == "kalman_align")

    def _on_sync_dt_fixed_changed(self, checked: bool):
        """Habilita/desabilita campo de dt fixo"""
        self._sync_dt_value.setEnabled(checked)
        self._sync_grid_method.setEnabled(not checked)

    def _refresh_sync_datasets(self):
        """Atualiza lista de datasets disponíveis para sincronização"""
        self._sync_datasets_list.clear()

        if not self.session_state:
            return

        # Obter todos os datasets carregados
        dataset_ids = self.session_state.list_datasets()

        for dataset_id in dataset_ids:
            dataset = self.session_state.get_dataset(dataset_id)
            if dataset:
                n_series = len(dataset.series) if dataset.series else 0
                item_text = f"{dataset_id} ({n_series} séries)"
                self._sync_datasets_list.addItem(item_text)

        if len(dataset_ids) < 2:
            info_item = self._sync_datasets_list.item(0)
            if info_item:
                info_item.setToolTip("Carregue pelo menos 2 datasets para sincronizar")

    def _get_sync_params(self) -> dict:
        """Coleta parâmetros de sincronização"""
        params = {
            "method": self._sync_method.currentText(),
            "grid_method": self._sync_grid_method.currentText(),
            "interp_method": self._sync_interp_method.currentText(),
        }

        if self._sync_dt_fixed.isChecked():
            params["dt"] = self._sync_dt_value.value()

        if self._sync_method.currentText() == "kalman_align":
            params["process_noise"] = self._sync_process_noise.value()
            params["measurement_noise"] = self._sync_measurement_noise.value()

        return params

    def _get_selected_sync_datasets(self) -> list[str]:
        """Retorna IDs dos datasets selecionados para sincronização"""
        selected = []
        for item in self._sync_datasets_list.selectedItems():
            # Extrair ID do texto (formato: "dataset_id (N séries)")
            text = item.text()
            dataset_id = text.split(" (")[0]
            selected.append(dataset_id)
        return selected

    def _preview_sync(self):
        """Preview da sincronização com visualização gráfica"""
        import numpy as np
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        
        selected_datasets = self._get_selected_sync_datasets()

        if len(selected_datasets) < 2:
            QMessageBox.warning(
                self, "Aviso",
                "Selecione pelo menos 2 datasets para sincronizar.\n"
                "Use Ctrl+Click para selecionar múltiplos."
            )
            return

        params = self._get_sync_params()
        
        # Coletar dados para preview
        all_series_data = {}
        all_t_data = {}
        
        for dataset_id in selected_datasets:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or not dataset.series:
                continue
                
            for series_id, series in dataset.series.items():
                key = f"{dataset_id}/{series_id}"
                if series.values is not None and len(series.values) > 0:
                    all_series_data[key] = np.array(series.values[:1000])  # Limitar para preview
                    if hasattr(dataset, 't_seconds') and dataset.t_seconds is not None:
                        all_t_data[key] = np.array(dataset.t_seconds[:1000])
                    else:
                        all_t_data[key] = np.arange(len(series.values[:1000]))
        
        if len(all_series_data) < 2:
            QMessageBox.warning(self, "Aviso", "Dados insuficientes para preview.")
            return
            
        # Criar diálogo de preview
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview de Sincronização")
        dialog.resize(900, 700)
        dialog_layout = QVBoxLayout(dialog)
        
        # Criar figura com 2 subplots
        fig = Figure(figsize=(10, 8), dpi=100)
        canvas = FigureCanvas(fig)
        
        # Subplot 1: Dados originais
        ax1 = fig.add_subplot(211)
        ax1.set_title("Dados Originais (antes da sincronização)", fontsize=12, fontweight='bold')
        
        colors = ['#0d6efd', '#198754', '#dc3545', '#fd7e14', '#6f42c1', '#20c997']
        for i, (key, values) in enumerate(all_series_data.items()):
            t = all_t_data[key]
            color = colors[i % len(colors)]
            ax1.plot(t, values, label=key[:30], color=color, alpha=0.8, linewidth=1)
        
        ax1.set_xlabel("Tempo (s)")
        ax1.set_ylabel("Valor")
        ax1.legend(loc='upper right', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Histograma de intervalos de tempo
        ax2 = fig.add_subplot(212)
        ax2.set_title("Distribuição de Intervalos de Tempo (dt)", fontsize=12, fontweight='bold')
        
        all_dts = []
        for key, t in all_t_data.items():
            if len(t) > 1:
                dt = np.diff(t)
                all_dts.extend(dt)
        
        if all_dts:
            ax2.hist(all_dts, bins=50, color='#0d6efd', alpha=0.7, edgecolor='white')
            ax2.axvline(np.median(all_dts), color='#dc3545', linestyle='--', 
                       label=f'Mediana: {np.median(all_dts):.4f}s')
            ax2.axvline(np.mean(all_dts), color='#198754', linestyle='--', 
                       label=f'Média: {np.mean(all_dts):.4f}s')
            ax2.legend()
        
        ax2.set_xlabel("dt (segundos)")
        ax2.set_ylabel("Frequência")
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        dialog_layout.addWidget(canvas)
        
        # Info label
        info_label = QLabel(
            f"📊 Datasets: {', '.join(selected_datasets)}\n"
            f"📈 Total de séries: {len(all_series_data)}\n"
            f"⚙️ Método: {params['method']} | Interpolação: {params['interp_method']}"
        )
        info_label.setStyleSheet("padding: 10px; background: #f8f9fa; border-radius: 4px;")
        dialog_layout.addWidget(info_label)
        
        # Botões
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        dialog_layout.addLayout(btn_layout)
        
        dialog.exec()
        logger.info(f"sync_preview_shown: {len(all_series_data)} series")

    def _apply_sync(self):
        """Aplica sincronização aos datasets selecionados"""
        from datetime import datetime as dt

        import numpy as np
        from pint import UnitRegistry

        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )
        from platform_base.processing.synchronization import synchronize

        ureg = UnitRegistry()
        selected_datasets = self._get_selected_sync_datasets()

        if len(selected_datasets) < 2:
            QMessageBox.warning(
                self, "Aviso",
                "Selecione pelo menos 2 datasets para sincronizar.\n"
                "Use Ctrl+Click para selecionar múltiplos."
            )
            return

        params = self._get_sync_params()

        logger.info(f"sync_requested: datasets={selected_datasets}, params={params}")

        try:
            # Coletar todas as séries de todos os datasets
            series_dict = {}  # nome -> valores
            t_dict = {}       # nome -> timestamps

            for dataset_id in selected_datasets:
                dataset = self.session_state.get_dataset(dataset_id)
                if not dataset or not dataset.series:
                    continue

                for series_id, series in dataset.series.items():
                    key = f"{dataset_id}/{series_id}"

                    if series.values is not None and len(series.values) > 0:
                        series_dict[key] = np.array(series.values, dtype=float)

                        # Usar timestamps se disponível, senão criar índice
                        if hasattr(dataset, 't_seconds') and dataset.t_seconds is not None:
                            t_dict[key] = np.array(dataset.t_seconds, dtype=float)
                        else:
                            t_dict[key] = np.arange(len(series.values), dtype=float)

            if len(series_dict) < 2:
                QMessageBox.warning(
                    self, "Aviso",
                    "Não há séries suficientes para sincronizar."
                )
                return

            # Executar sincronização
            result = synchronize(
                series_dict=series_dict,
                t_dict=t_dict,
                method=params["method"],
                params=params,
            )

            # Criar novo dataset com séries sincronizadas se solicitado
            if self._sync_create_new.isChecked():
                synced_series = {}
                for key, values in result.synced_series.items():
                    series_id = key.replace("/", "_").replace("-", "_")
                    series = Series(
                        series_id=series_id,
                        name=key,
                        unit=ureg.dimensionless,
                        values=np.array(values, dtype=np.float64),
                        metadata=SeriesMetadata(
                            original_name=key,
                            source_column=key,
                            description=f"Série sincronizada de {key}"
                        )
                    )
                    synced_series[series_id] = series

                # Criar timestamps como datetime
                t_common = result.t_common
                base_time = np.datetime64('2024-01-01T00:00:00')
                t_datetime = base_time + (t_common * 1e9).astype('timedelta64[ns]')

                synced_dataset = Dataset(
                    dataset_id="synchronized",
                    version=1,
                    parent_id=None,
                    source=SourceInfo(
                        filepath="memory://synchronized",
                        filename="synchronized.sync",
                        format="sync",
                        size_bytes=0,
                        checksum="sync_generated"
                    ),
                    t_seconds=np.array(t_common, dtype=np.float64),
                    t_datetime=t_datetime,
                    series=synced_series,
                    metadata=DatasetMetadata(
                        description=f"Datasets sincronizados: {', '.join(selected_datasets)}",
                        tags=["synchronized", "generated"],
                        custom={
                            "source_datasets": selected_datasets,
                            "sync_method": params["method"],
                            "alignment_error": result.alignment_error,
                            "confidence": result.confidence,
                        }
                    ),
                    created_at=dt.now(),
                )

                self.session_state.add_dataset(synced_dataset)

            # Adicionar ao histórico
            self._add_to_history("synchronize", {
                **params,
                "datasets": selected_datasets,
                "n_series": len(result.synced_series),
            })

            # Mostrar resultado
            QMessageBox.information(
                self, "Sincronização Concluída",
                f"Séries sincronizadas: {len(result.synced_series)}\n"
                f"Pontos na grade comum: {len(result.t_common):,}\n"
                f"Erro de alinhamento: {result.alignment_error:.4f}\n"
                f"Confiança: {result.confidence:.1%}\n\n"
                "Novo dataset 'synchronized' criado."
            )

            logger.info(f"sync_completed: n_series={len(result.synced_series)}, "
                       f"error={result.alignment_error:.4f}, confidence={result.confidence:.2f}")

        except Exception as e:
            logger.exception(f"sync_failed: {e}")
            QMessageBox.critical(
                self, "Erro na Sincronização",
                f"Falha ao sincronizar datasets:\n{e!s}"
            )

    def _create_export_tab(self):
        """Tab de exportação"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # Formato
        format_group = QGroupBox("📄 Formato")
        format_layout = QFormLayout(format_group)

        self._export_format = self._create_combo_box()
        self._export_format.addItems(["CSV", "Excel (.xlsx)", "Parquet", "HDF5", "JSON"])
        self._export_format.setToolTip("Formato de exportação")
        format_layout.addRow("Formato:", self._export_format)

        layout.addWidget(format_group)

        # Opções
        options_group = QGroupBox("⚙️ Opções")
        options_layout = QVBoxLayout(options_group)

        self._export_metadata = QCheckBox("Incluir metadados")
        self._export_metadata.setChecked(True)
        self._export_metadata.setToolTip("Incluir informações de processamento")
        options_layout.addWidget(self._export_metadata)

        self._export_timestamps = QCheckBox("Incluir timestamps")
        self._export_timestamps.setChecked(True)
        self._export_timestamps.setToolTip("Exportar coluna de timestamps")
        options_layout.addWidget(self._export_timestamps)

        self._export_interp_flags = QCheckBox("Flags de interpolação")
        self._export_interp_flags.setToolTip("Marcar pontos interpolados")
        options_layout.addWidget(self._export_interp_flags)

        self._export_selected_only = QCheckBox("Apenas séries selecionadas")
        self._export_selected_only.setToolTip("Exportar apenas séries selecionadas")
        options_layout.addWidget(self._export_selected_only)

        layout.addWidget(options_group)

        # Botões
        btn_layout = QVBoxLayout()

        export_data_btn = QPushButton("💾 Exportar Dados")
        export_data_btn.setObjectName("success")
        export_data_btn.setToolTip("Exportar dados para arquivo")
        export_data_btn.clicked.connect(self._export_data)
        btn_layout.addWidget(export_data_btn)

        export_session_btn = QPushButton("📦 Exportar Sessão")
        export_session_btn.setToolTip("Exportar configuração e estado da sessão")
        export_session_btn.clicked.connect(self._export_session)
        btn_layout.addWidget(export_session_btn)

        export_plot_btn = QPushButton("🖼️ Exportar Gráfico")
        export_plot_btn.setToolTip("Exportar visualização atual como imagem")
        export_plot_btn.clicked.connect(self._export_plot)
        btn_layout.addWidget(export_plot_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "💾")

    def _create_streaming_tab(self):
        """Tab de controle de streaming para visualização"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # === CONTROLE DE STREAMING ===
        stream_group = QGroupBox("📡 Controle de Streaming")
        stream_layout = QFormLayout(stream_group)

        # Status
        self._stream_status = QLabel("⏹️ Parado")
        self._stream_status.setStyleSheet("font-weight: bold; color: #6c757d;")
        stream_layout.addRow("Status:", self._stream_status)

        # Taxa de atualização
        self._stream_rate = QSpinBox()
        self._stream_rate.setRange(1, 60)
        self._stream_rate.setValue(10)
        self._stream_rate.setSuffix(" FPS")
        self._stream_rate.setToolTip("Taxa de atualização do gráfico (frames por segundo)")
        stream_layout.addRow("Taxa:", self._stream_rate)

        # Janela de visualização
        self._stream_window = QSpinBox()
        self._stream_window.setRange(100, 100000)
        self._stream_window.setValue(1000)
        self._stream_window.setToolTip("Número de pontos visíveis na janela")
        stream_layout.addRow("Janela:", self._stream_window)

        # Modo de scroll
        self._stream_scroll_mode = self._create_combo_box()
        self._stream_scroll_mode.addItems(["Auto-scroll", "Fixo", "Follow Last"])
        self._stream_scroll_mode.setToolTip("Modo de rolagem do gráfico")
        stream_layout.addRow("Scroll:", self._stream_scroll_mode)

        layout.addWidget(stream_group)

        # === BUFFER DE DADOS ===
        buffer_group = QGroupBox("📊 Buffer de Dados")
        buffer_layout = QFormLayout(buffer_group)

        self._buffer_size = QSpinBox()
        self._buffer_size.setRange(1000, 10000000)
        self._buffer_size.setValue(100000)
        self._buffer_size.setToolTip("Tamanho máximo do buffer de dados")
        buffer_layout.addRow("Tamanho:", self._buffer_size)

        self._buffer_current = QLabel("0 / 100000")
        self._buffer_current.setStyleSheet("color: #6c757d;")
        buffer_layout.addRow("Atual:", self._buffer_current)

        self._auto_decimate = QCheckBox("Auto-decimação")
        self._auto_decimate.setChecked(True)
        self._auto_decimate.setToolTip("Reduzir automaticamente pontos para melhor performance")
        buffer_layout.addRow(self._auto_decimate)

        layout.addWidget(buffer_group)

        # === BOTÕES DE CONTROLE ===
        ctrl_layout = QHBoxLayout()

        start_btn = QPushButton("▶️ Iniciar")
        start_btn.setToolTip("Iniciar streaming de dados")
        start_btn.clicked.connect(self._start_streaming)
        ctrl_layout.addWidget(start_btn)

        pause_btn = QPushButton("⏸️ Pausar")
        pause_btn.setToolTip("Pausar streaming")
        pause_btn.clicked.connect(self._pause_streaming)
        ctrl_layout.addWidget(pause_btn)

        stop_btn = QPushButton("⏹️ Parar")
        stop_btn.setToolTip("Parar streaming e limpar buffer")
        stop_btn.clicked.connect(self._stop_streaming)
        ctrl_layout.addWidget(stop_btn)

        layout.addLayout(ctrl_layout)

        # === ESTATÍSTICAS ===
        stats_group = QGroupBox("📈 Estatísticas em Tempo Real")
        stats_layout = QFormLayout(stats_group)

        self._stream_fps_label = QLabel("0 FPS")
        stats_layout.addRow("FPS Real:", self._stream_fps_label)

        self._stream_latency = QLabel("0 ms")
        stats_layout.addRow("Latência:", self._stream_latency)

        self._stream_points_sec = QLabel("0 pts/s")
        stats_layout.addRow("Pontos/s:", self._stream_points_sec)

        layout.addWidget(stats_group)

        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "📡")

    def _create_settings_tab(self):
        """Tab de configurações da aplicação"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # === VISUALIZAÇÃO ===
        viz_group = QGroupBox("📊 Visualização")
        viz_layout = QFormLayout(viz_group)

        # Tema
        self._theme_combo = self._create_combo_box()
        self._theme_combo.addItems(["Claro", "Escuro", "Alto Contraste", "Sistema"])
        self._theme_combo.setToolTip("Tema de cores da aplicação")
        viz_layout.addRow("Tema:", self._theme_combo)

        # Estilo de gráfico
        self._plot_style = self._create_combo_box()
        self._plot_style.addItems(["default", "seaborn", "ggplot", "dark_background", "bmh"])
        self._plot_style.setToolTip("Estilo dos gráficos matplotlib")
        viz_layout.addRow("Estilo Gráfico:", self._plot_style)

        # Anti-aliasing
        self._antialiasing = QCheckBox("Anti-aliasing")
        self._antialiasing.setChecked(True)
        self._antialiasing.setToolTip("Suavização de linhas nos gráficos")
        viz_layout.addRow(self._antialiasing)

        # DPI do gráfico
        self._plot_dpi = QSpinBox()
        self._plot_dpi.setRange(72, 300)
        self._plot_dpi.setValue(100)
        self._plot_dpi.setToolTip("Resolução dos gráficos (DPI)")
        viz_layout.addRow("DPI:", self._plot_dpi)

        layout.addWidget(viz_group)

        # === PERFORMANCE ===
        perf_group = QGroupBox("⚡ Performance")
        perf_layout = QFormLayout(perf_group)

        # Limite de renderização direta
        self._direct_render_limit = QSpinBox()
        self._direct_render_limit.setRange(1000, 1000000)
        self._direct_render_limit.setValue(10000)
        self._direct_render_limit.setToolTip("Pontos máximos para renderização direta sem decimação")
        perf_layout.addRow("Render Direto:", self._direct_render_limit)

        # Pontos alvo para display
        self._target_display_points = QSpinBox()
        self._target_display_points.setRange(1000, 50000)
        self._target_display_points.setValue(5000)
        self._target_display_points.setToolTip("Número alvo de pontos após decimação")
        perf_layout.addRow("Pontos Alvo:", self._target_display_points)

        # Método de decimação
        self._decimation_method = self._create_combo_box()
        self._decimation_method.addItems(["MINMAX", "LTTB", "RANDOM", "EVERY_NTH"])
        self._decimation_method.setToolTip("Algoritmo de decimação para grandes volumes")
        perf_layout.addRow("Decimação:", self._decimation_method)

        # Multi-threading
        self._use_threading = QCheckBox("Multi-threading")
        self._use_threading.setChecked(True)
        self._use_threading.setToolTip("Usar threads para operações pesadas")
        perf_layout.addRow(self._use_threading)

        layout.addWidget(perf_group)

        # === DADOS ===
        data_group = QGroupBox("📁 Dados")
        data_layout = QFormLayout(data_group)

        # Formato de data padrão
        self._date_format = QComboBox()
        self._date_format.addItems([
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "ISO 8601"
        ])
        self._date_format.setToolTip("Formato padrão para exibição de datas")
        data_layout.addRow("Formato Data:", self._date_format)

        # Precisão numérica
        self._numeric_precision = QSpinBox()
        self._numeric_precision.setRange(1, 15)
        self._numeric_precision.setValue(6)
        self._numeric_precision.setToolTip("Casas decimais para exibição de números")
        data_layout.addRow("Precisão:", self._numeric_precision)

        # Auto-detectar tipos
        self._auto_detect_types = QCheckBox("Auto-detectar tipos")
        self._auto_detect_types.setChecked(True)
        self._auto_detect_types.setToolTip("Detectar automaticamente tipos de dados ao carregar")
        data_layout.addRow(self._auto_detect_types)

        layout.addWidget(data_group)

        # === BOTÕES ===
        btn_layout = QHBoxLayout()

        apply_btn = QPushButton("✅ Aplicar")
        apply_btn.setToolTip("Aplicar configurações")
        apply_btn.clicked.connect(self._apply_settings)
        btn_layout.addWidget(apply_btn)

        reset_btn = QPushButton("🔄 Restaurar Padrões")
        reset_btn.setToolTip("Restaurar todas as configurações para os valores padrão")
        reset_btn.clicked.connect(self._reset_settings)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)

        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "⚙️")

    # === HANDLERS DE STREAMING ===

    def _start_streaming(self):
        """Inicia streaming de dados"""
        self._stream_status.setText("▶️ Streaming")
        self._stream_status.setStyleSheet("font-weight: bold; color: #28a745;")
        logger.info("streaming_started")
        QMessageBox.information(self, "Streaming", 
            "Streaming iniciado.\n\n"
            "Para conectar a uma fonte de dados em tempo real,\n"
            "implemente a integração com seu sistema de aquisição.")

    def _pause_streaming(self):
        """Pausa streaming"""
        self._stream_status.setText("⏸️ Pausado")
        self._stream_status.setStyleSheet("font-weight: bold; color: #ffc107;")
        logger.info("streaming_paused")

    def _stop_streaming(self):
        """Para streaming"""
        self._stream_status.setText("⏹️ Parado")
        self._stream_status.setStyleSheet("font-weight: bold; color: #6c757d;")
        logger.info("streaming_stopped")

    # === HANDLERS DE CONFIGURAÇÃO ===

    def _apply_settings(self):
        """Aplica configurações"""
        logger.info("settings_applied")
        QMessageBox.information(self, "Configurações",
            "Configurações aplicadas com sucesso!\n\n"
            "Algumas configurações podem requerer reinício da aplicação.")

    def _reset_settings(self):
        """Restaura configurações padrão"""
        # Visualização
        self._theme_combo.setCurrentIndex(0)
        self._plot_style.setCurrentIndex(0)
        self._antialiasing.setChecked(True)
        self._plot_dpi.setValue(100)

        # Performance
        self._direct_render_limit.setValue(10000)
        self._target_display_points.setValue(5000)
        self._decimation_method.setCurrentIndex(0)
        self._use_threading.setChecked(True)

        # Dados
        self._date_format.setCurrentIndex(0)
        self._numeric_precision.setValue(6)
        self._auto_detect_types.setChecked(True)

        logger.info("settings_reset")
        QMessageBox.information(self, "Configurações",
            "Configurações restauradas para os valores padrão.")

    def _create_history_tab(self):
        """Tab de histórico de operações"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        # Lista de histórico
        self._history_list = QListWidget()
        self._history_list.setToolTip("Histórico das últimas operações")
        self._history_list.itemDoubleClicked.connect(self._replay_operation)
        layout.addWidget(self._history_list)

        # Botões
        btn_layout = QHBoxLayout()

        clear_btn = QPushButton("🗑️ Limpar")
        clear_btn.setObjectName("secondary")
        clear_btn.setToolTip("Limpar histórico")
        clear_btn.clicked.connect(self._clear_history)
        btn_layout.addWidget(clear_btn)

        replay_btn = QPushButton("🔄 Repetir")
        replay_btn.setToolTip("Repetir operação selecionada")
        replay_btn.clicked.connect(self._replay_selected)
        btn_layout.addWidget(replay_btn)

        layout.addLayout(btn_layout)

        self._tabs.addTab(tab, "📜")

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Apenas uma conexão para dataset_changed
        self.session_state.dataset_changed.connect(self._update_series_selector)
        self.session_state.operation_finished.connect(self._on_operation_finished)

    @pyqtSlot(str)
    def _update_series_selector(self, dataset_id: str):
        """Atualiza o combobox de seleção de série com as séries do dataset atual"""
        try:
            self._series_combo.clear()
            
            if not dataset_id:
                self._series_combo.addItem("(Nenhum dataset carregado)")
                self._series_combo.setEnabled(False)
                return
                
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or not dataset.series:
                self._series_combo.addItem("(Nenhuma série disponível)")
                self._series_combo.setEnabled(False)
                return
                
            # Adicionar séries ao combobox
            for series_id, series in dataset.series.items():
                # Usar nome do dataset + nome da série para melhor identificação
                display_name = f"{dataset_id} / {series.name if series.name else series_id}"
                n_points = len(series.values) if series.values is not None else 0
                self._series_combo.addItem(f"{display_name} ({n_points:,} pts)", series_id)
                
            self._series_combo.setEnabled(True)
        except Exception as e:
            logger.exception("_update_series_selector_failed", error=str(e))

    @pyqtSlot(str, bool)
    def _on_operation_finished(self, operation: str, success: bool):
        """Callback quando operação termina"""
        if self._history:
            self._history[-1].success = success
            self._update_history_display()

    def _add_to_history(self, operation: str, params: dict[str, Any]):
        """Adiciona operação ao histórico"""
        item = OperationHistoryItem(operation, params)
        self._history.append(item)

        if len(self._history) > self._max_history:
            self._history.pop(0)

        self._update_history_display()

    def _update_history_display(self):
        """Atualiza visualização do histórico"""
        self._history_list.clear()

        for item in reversed(self._history):
            icon = "✅" if item.success else "❌"
            text = f"{icon} {item.timestamp.strftime('%H:%M:%S')} - {item.operation}"

            list_item = QListWidgetItem(text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)

            if not item.success:
                list_item.setForeground(QColor("#dc3545"))

            self._history_list.addItem(list_item)

    # === HANDLERS DE INTERPOLAÇÃO ===

    def _preview_interpolation(self):
        """Preview de interpolação com visualização gráfica"""

        params = self._get_interpolation_params()
        logger.info(f"interpolation_preview_requested: {params}")

        # Obter dados da série selecionada
        series_data = self._get_selected_series_data()

        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        # Mostrar preview dialog
        dialog = OperationPreviewDialog("interpolation", params, series_data, self)

        if dialog.exec():
            # Se usuário clicou "Aplicar", executar operação
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("interpolation", params)
                self.operation_requested.emit("interpolation", params)
                logger.info(f"interpolation_applied_from_preview: {params}")

    def _apply_interpolation(self):
        """Aplica interpolação"""
        params = self._get_interpolation_params()
        self._add_to_history("interpolation", params)
        self.operation_requested.emit("interpolation", params)
        logger.info(f"interpolation_requested: {params}")

    def _get_interpolation_params(self) -> dict[str, Any]:
        """Coleta parâmetros de interpolação"""
        return {
            "method": self._interp_method.currentText(),
            "num_points": self._interp_points.value(),
            "smoothing": self._interp_smooth.value(),
            "degree": self._interp_degree.value(),
            "extrapolate": self._interp_extrapolate.isChecked(),
        }

    # === HANDLERS DE CÁLCULOS ===

    def _preview_derivative(self):
        """Preview de derivada com visualização gráfica"""

        order = self._deriv_order.currentIndex() + 1
        params = {
            "order": order,
            "method": self._deriv_method.currentText(),
            "window_length": self._deriv_window.value(),
            "pre_smooth": self._deriv_smooth.isChecked(),
        }
        logger.info(f"derivative_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("derivative", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history(f"derivative_{order}order", params)
                self.operation_requested.emit("derivative", params)

    def _preview_integral(self):
        """Preview de integral com visualização gráfica"""
        params = {"method": self._integ_method.currentText()}
        logger.info(f"integral_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("integral", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("integral", params)
                self.operation_requested.emit("integral", params)

    def _preview_smoothing(self):
        """Preview de suavização com visualização gráfica"""
        params = {
            "method": self._smooth_method.currentText(),
            "window": self._smooth_window.value(),
            "sigma": self._smooth_sigma.value(),
        }
        logger.info(f"smoothing_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("smoothing", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("smoothing", params)
                self.operation_requested.emit("smoothing", params)

    def _preview_remove_outliers(self):
        """Preview de remoção de outliers com visualização gráfica"""
        params = {
            "method": self._outlier_method.currentText(),
            "threshold": self._outlier_threshold.value(),
        }
        logger.info(f"outlier_removal_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("remove_outliers", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("remove_outliers", params)
                self.operation_requested.emit("remove_outliers", params)

    def _calculate_derivative(self):
        """Calcula derivada"""
        order = self._deriv_order.currentIndex() + 1
        params = {
            "order": order,
            "method": self._deriv_method.currentText(),
            "window_length": self._deriv_window.value(),
            "pre_smooth": self._deriv_smooth.isChecked(),
        }
        self._add_to_history(f"derivative_{order}order", params)
        self.operation_requested.emit("derivative", params)
        logger.info(f"derivative_requested: {params}")

    def _calculate_integral(self):
        """Calcula integral"""
        params = {"method": self._integ_method.currentText()}
        self._add_to_history("integral", params)
        self.operation_requested.emit("integral", params)
        logger.info(f"integral_requested: {params}")

    def _calculate_area(self):
        """Calcula área"""
        area_type = self._area_type.currentText()
        params = {"type": "under_curve" if "sob" in area_type.lower() else "between_curves"}
        self._add_to_history("area", params)
        self.operation_requested.emit("area", params)
        logger.info(f"area_requested: {params}")

    # === HANDLERS DE FILTROS ===

    def _apply_smoothing(self):
        """Aplica suavização"""
        params = {
            "method": self._smooth_method.currentText(),
            "window": self._smooth_window.value(),
            "sigma": self._smooth_sigma.value(),
        }
        self._add_to_history("smoothing", params)
        self.operation_requested.emit("smoothing", params)
        logger.info(f"smoothing_requested: {params}")

    def _remove_outliers(self):
        """Remove outliers"""
        params = {
            "method": self._outlier_method.currentText(),
            "threshold": self._outlier_threshold.value(),
        }
        self._add_to_history("remove_outliers", params)
        self.operation_requested.emit("remove_outliers", params)
        logger.info(f"outlier_removal_requested: {params}")

    # === HANDLERS DE ANÁLISE AVANÇADA ===

    def _compute_fft(self):
        """Compute FFT analysis"""
        window = self._fft_window.currentText()
        if window == "none":
            window = None

        params = {
            "window": window,
            "detrend": self._fft_detrend.isChecked(),
        }

        logger.info("fft_requested", params=params)
        self._add_to_history("fft", params)
        self.operation_requested.emit("fft", params)

    def _compute_correlation(self):
        """Compute correlation analysis"""
        params = {
            "mode": self._corr_mode.currentText(),
            "normalize": self._corr_normalize.isChecked(),
        }

        logger.info("correlation_requested", params=params)
        self._add_to_history("correlation", params)
        self.operation_requested.emit("correlation", params)

    def _on_filter_type_changed(self, filter_type: str):
        """Handle filter type change to show/hide cutoff fields"""
        is_band = filter_type in ("bandpass", "bandstop")

        self._filter_cutoff_high.setVisible(is_band)
        self._filter_cutoff_high_label.setVisible(is_band)

        if is_band:
            self._filter_cutoff_label.setText("Low Cutoff (Hz):")
        else:
            self._filter_cutoff_label.setText("Cutoff (Hz):")

    def _apply_filter(self):
        """Apply digital filter to signal"""
        filter_type = self._filter_type.currentText()

        params = {
            "filter_type": filter_type,
            "filter_order": self._filter_order.value(),
            "method": self._filter_method.currentText(),
        }

        # Add cutoff frequencies based on filter type
        if filter_type in ("bandpass", "bandstop"):
            params["cutoff_frequency"] = (
                self._filter_cutoff.value(),
                self._filter_cutoff_high.value()
            )
        else:
            params["cutoff_frequency"] = self._filter_cutoff.value()

        logger.info("filter_requested", params=params)
        self._add_to_history(f"{filter_type}_filter", params)
        self.operation_requested.emit("filter", params)

    def _preview_filter(self):
        """Preview digital filter effects"""
        filter_type = self._filter_type.currentText()

        params = {
            "filter_type": filter_type,
            "filter_order": self._filter_order.value(),
            "method": self._filter_method.currentText(),
        }

        if filter_type in ("bandpass", "bandstop"):
            params["cutoff_frequency"] = (
                self._filter_cutoff.value(),
                self._filter_cutoff_high.value()
            )
        else:
            params["cutoff_frequency"] = self._filter_cutoff.value()

        logger.info(f"filter_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("filter", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history(f"{filter_type}_filter", params)
                self.operation_requested.emit("filter", params)

    # === HANDLERS DE EXPORT ===

    def _export_data(self):
        """Exporta dados"""
        format_map = {
            "CSV": "csv",
            "Excel (.xlsx)": "xlsx",
            "Parquet": "parquet",
            "HDF5": "hdf5",
            "JSON": "json",
        }

        format_text = self._export_format.currentText()
        params = {
            "format": format_map.get(format_text, "csv"),
            "include_metadata": self._export_metadata.isChecked(),
            "include_timestamps": self._export_timestamps.isChecked(),
            "include_interp_flags": self._export_interp_flags.isChecked(),
            "selected_only": self._export_selected_only.isChecked(),
        }

        self._add_to_history("export_data", params)
        self.export_requested.emit(params["format"], params)
        logger.info(f"export_data_requested: {params}")

    def _export_session(self):
        """Exporta sessão"""
        self.export_requested.emit("session", {"type": "session"})
        logger.info("export_session_requested")

    def _export_plot(self):
        """Exporta gráfico"""
        self.export_requested.emit("image", {"type": "plot"})
        logger.info("export_plot_requested")

    # === HANDLERS DE HISTÓRICO ===

    def _clear_history(self):
        """Limpa histórico"""
        self._history.clear()
        self._history_list.clear()
        logger.info("history_cleared")

    def _replay_selected(self):
        """Repete operação selecionada"""
        current = self._history_list.currentItem()
        if current:
            self._replay_operation(current)

    def _replay_operation(self, item: QListWidgetItem):
        """Repete uma operação do histórico"""
        history_item = item.data(Qt.ItemDataRole.UserRole)
        if history_item:
            logger.info(f"replaying_operation: {history_item.operation}, params={history_item.params}")
            self.operation_requested.emit(history_item.operation, history_item.params)

    # === MÉTODOS PÚBLICOS PARA DIÁLOGOS ===

    def show_interpolation_dialog(self):
        """Mostra diálogo de interpolação expandido"""
        self._tabs.setCurrentIndex(0)
        logger.debug("interpolation_dialog_shown")

    def show_derivative_dialog(self):
        """Mostra diálogo de derivada"""
        self._tabs.setCurrentIndex(1)
        logger.debug("derivative_dialog_shown")

    def show_integral_dialog(self):
        """Mostra diálogo de integral"""
        self._tabs.setCurrentIndex(1)
        logger.debug("integral_dialog_shown")

    def show_export_dialog(self):
        """Mostra diálogo de exportação"""
        self._tabs.setCurrentIndex(3)
        logger.debug("export_dialog_shown")

    # === MÉTODOS DE DADOS ===

    def _get_selected_series_data(self):
        """
        Obtém dados da série selecionada para preview

        Returns:
            numpy.ndarray ou None se não houver seleção
        """
        import numpy as np

        # Obter série selecionada do combobox
        if not hasattr(self, '_series_combo') or self._series_combo.count() == 0:
            logger.debug("No series selector available")
            return None
            
        series_id = self._series_combo.currentData()
        if not series_id:
            logger.debug("No series selected in combo")
            return None
            
        # Obter dados do SessionState
        if self.session_state and self.session_state.current_dataset:
            dataset = self.session_state.get_dataset(self.session_state.current_dataset)
            if dataset and series_id in dataset.series:
                series = dataset.series[series_id]
                if hasattr(series, 'values') and series.values is not None:
                    logger.debug(f"Got series data: {series_id}, {len(series.values)} points")
                    return series.values
                    
        logger.debug("No series data available")
        return None

    def set_data(self, data):
        """
        Define os dados para preview

        Args:
            data: numpy.ndarray ou pandas.DataFrame
        """
        self.session_state._loaded_data = data
        logger.debug("data_set_for_preview")
