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

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
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
            QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
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

        # Tab widget principal
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(self._tabs, stretch=1)

        # Criar tabs
        self._create_interpolation_tab()
        self._create_calculus_tab()
        self._create_filters_tab()
        self._create_export_tab()
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

        self._interp_method = QComboBox()
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

        self._deriv_order = QComboBox()
        self._deriv_order.addItems(["1ª Ordem", "2ª Ordem", "3ª Ordem"])
        self._deriv_order.setToolTip("Ordem da derivada")
        deriv_layout.addRow("Ordem:", self._deriv_order)

        self._deriv_method = QComboBox()
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
        deriv_btn.clicked.connect(self._calculate_derivative)

        deriv_preview_btn = QPushButton("👁️ Preview")
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

        self._integ_method = QComboBox()
        self._integ_method.addItems(["trapezoid", "simpson", "cumulative"])
        self._integ_method.setToolTip("Método de integração numérica")
        integ_layout.addRow("Método:", self._integ_method)

        integ_btn = QPushButton("📊 Calcular Integral")
        integ_btn.clicked.connect(self._calculate_integral)

        integ_preview_btn = QPushButton("👁️ Preview")
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

        self._area_type = QComboBox()
        self._area_type.addItems(["Área sob a curva", "Área entre curvas"])
        self._area_type.setToolTip("Tipo de cálculo de área")
        area_layout.addRow("Tipo:", self._area_type)

        area_btn = QPushButton("📊 Calcular Área")
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

        self._smooth_method = QComboBox()
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
        smooth_btn.clicked.connect(self._apply_smoothing)

        smooth_preview_btn = QPushButton("👁️ Preview")
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

        self._outlier_method = QComboBox()
        self._outlier_method.addItems(["zscore", "iqr", "mad"])
        self._outlier_method.setToolTip("Método de detecção de outliers")
        outlier_layout.addRow("Método:", self._outlier_method)

        self._outlier_threshold = QDoubleSpinBox()
        self._outlier_threshold.setRange(1.0, 10.0)
        self._outlier_threshold.setValue(3.0)
        self._outlier_threshold.setToolTip("Limiar para detecção (ex: 3 sigmas)")
        outlier_layout.addRow("Limiar:", self._outlier_threshold)

        outlier_btn = QPushButton("🚫 Remover Outliers")
        outlier_btn.clicked.connect(self._remove_outliers)

        outlier_preview_btn = QPushButton("👁️ Preview")
        outlier_preview_btn.setObjectName("secondary")
        outlier_preview_btn.clicked.connect(self._preview_remove_outliers)

        outlier_btn_layout = QHBoxLayout()
        outlier_btn_layout.addWidget(outlier_preview_btn)
        outlier_btn_layout.addWidget(outlier_btn)
        outlier_layout.addRow(outlier_btn_layout)

        layout.addWidget(outlier_group)
        layout.addStretch()

        tab.setWidget(content)
        self._tabs.addTab(tab, "🎚️")

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

        self._export_format = QComboBox()
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
        self.session_state.dataset_changed.connect(self._on_dataset_changed)
        self.session_state.operation_finished.connect(self._on_operation_finished)

    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Callback quando dataset muda"""
        logger.debug(f"operations_panel_dataset_changed: {dataset_id}")

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

        # Tentar obter dados do SessionState
        if self.session_state:
            # Verificar se há dados carregados
            loaded_data = getattr(self.session_state, "_loaded_data", None)

            if loaded_data is not None:
                # Se for DataFrame pandas
                if hasattr(loaded_data, "iloc"):
                    # Pegar primeira coluna numérica
                    for col in loaded_data.columns:
                        if loaded_data[col].dtype in ("float64", "float32", "int64", "int32"):
                            return loaded_data[col].values

                # Se for array numpy
                if isinstance(loaded_data, np.ndarray):
                    return loaded_data if loaded_data.ndim == 1 else loaded_data[:, 0]

            # Se não houver dados carregados, gerar dados de exemplo para demonstração
            logger.debug("No data loaded, generating sample data for preview")

        # Gerar dados de exemplo (senóide com ruído)
        x = np.linspace(0, 10, 500)
        return np.sin(x) + 0.2 * np.random.randn(len(x))

    def set_data(self, data):
        """
        Define os dados para preview

        Args:
            data: numpy.ndarray ou pandas.DataFrame
        """
        self.session_state._loaded_data = data
        logger.debug("data_set_for_preview")
