"""
FilterDialog - Diálogo de configuração de filtros

Filtros disponíveis:
- Butterworth (low-pass, high-pass, band-pass)
- Remoção de outliers (IQR, Z-score, MAD)
- Rolling window

Interface carregada de: desktop/ui_files/filterDialog.ui
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class FilterDialog(QDialog, UiLoaderMixin):
    """
    Diálogo para configuração de filtros de dados

    Tipos de filtros:
    - Butterworth: Filtro de frequência (passa-baixa, passa-alta, passa-banda)
    - Outliers: Remoção de valores atípicos
    - Rolling: Filtros baseados em janela móvel
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """
    
    # Arquivo .ui que define a interface
    UI_FILE = "desktop/ui_files/filterDialog.ui"

    filter_applied = pyqtSignal(dict)  # config

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Tenta carregar do arquivo .ui, senão usa fallback
        if not self._load_ui():
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()
        
        self._setup_connections()

        logger.debug("filter_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Encontra widgets do arquivo .ui
        self.content_widget = self.findChild(QWidget, "contentWidget")
        self.button_box = self.findChild(QDialogButtonBox, "buttonBox")
        
        # Se o contentWidget existe mas está vazio, preenche programaticamente
        if self.content_widget:
            content_layout = self.content_widget.layout()
            if content_layout and content_layout.count() == 0:
                # UI está vazio, criar conteúdo programaticamente
                self._create_content_widgets(content_layout)
        
        logger.debug("filter_dialog_ui_loaded_from_file")

    def _create_content_widgets(self, layout: QVBoxLayout):
        """Cria widgets de conteúdo quando o .ui está vazio"""
        # Header
        header = QLabel("🔧 Configurar Filtro de Dados")
        header.setFont(QFont("", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #0d6efd; padding: 10px;")
        layout.addWidget(header)

        # Tabs para tipos de filtro
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Criar tabs
        self._create_butterworth_tab()
        self._create_outliers_tab()
        self._create_rolling_tab()

    def _setup_ui_fallback(self):
        """Configura interface do diálogo (fallback programático)"""
        self.setWindowTitle("🔧 Configurar Filtro")
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 2px 8px;
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton[objectName="secondary"] {
                background-color: #6c757d;
            }
            QPushButton[objectName="success"] {
                background-color: #198754;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                min-width: 150px;
            }
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
        """)

        # Header
        header = QLabel("🔧 Configurar Filtro de Dados")
        header.setFont(QFont("", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #0d6efd; padding: 10px;")
        layout.addWidget(header)

        # Tabs para tipos de filtro
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Criar tabs
        self._create_butterworth_tab()
        self._create_outliers_tab()
        self._create_rolling_tab()

        # Botões de ação
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self._preview_filter)
        btn_layout.addWidget(preview_btn)

        apply_btn = QPushButton("✅ Aplicar Filtro")
        apply_btn.setObjectName("success")
        apply_btn.clicked.connect(self._apply_filter)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

    def _create_butterworth_tab(self):
        """Tab de filtro Butterworth"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Tipo de filtro
        type_group = QGroupBox("📊 Tipo de Filtro")
        type_layout = QFormLayout(type_group)

        self._butter_type = QComboBox()
        self._butter_type.addItems(["lowpass", "highpass", "bandpass", "bandstop"])
        self._butter_type.setToolTip(
            "Tipo de filtro Butterworth:\n"
            "• lowpass: Permite frequências baixas\n"
            "• highpass: Permite frequências altas\n"
            "• bandpass: Permite faixa de frequências\n"
            "• bandstop: Bloqueia faixa de frequências",
        )
        type_layout.addRow("Tipo:", self._butter_type)

        layout.addWidget(type_group)

        # Parâmetros
        params_group = QGroupBox("🔧 Parâmetros")
        params_layout = QFormLayout(params_group)

        self._butter_order = QSpinBox()
        self._butter_order.setRange(1, 10)
        self._butter_order.setValue(4)
        self._butter_order.setToolTip(
            "Ordem do filtro (1-10).\n"
            "Ordens maiores = corte mais abrupto.",
        )
        params_layout.addRow("Ordem:", self._butter_order)

        self._butter_cutoff_low = QDoubleSpinBox()
        self._butter_cutoff_low.setRange(0.001, 1000.0)
        self._butter_cutoff_low.setValue(1.0)
        self._butter_cutoff_low.setDecimals(3)
        self._butter_cutoff_low.setSuffix(" Hz")
        self._butter_cutoff_low.setToolTip(
            "Frequência de corte inferior.\n"
            "Para lowpass: frequência máxima permitida.\n"
            "Para bandpass/bandstop: limite inferior da banda.",
        )
        params_layout.addRow("Freq. Corte (baixa):", self._butter_cutoff_low)

        self._butter_cutoff_high = QDoubleSpinBox()
        self._butter_cutoff_high.setRange(0.001, 1000.0)
        self._butter_cutoff_high.setValue(10.0)
        self._butter_cutoff_high.setDecimals(3)
        self._butter_cutoff_high.setSuffix(" Hz")
        self._butter_cutoff_high.setToolTip(
            "Frequência de corte superior.\n"
            "Para highpass: frequência mínima permitida.\n"
            "Para bandpass/bandstop: limite superior da banda.",
        )
        params_layout.addRow("Freq. Corte (alta):", self._butter_cutoff_high)

        self._butter_fs = QDoubleSpinBox()
        self._butter_fs.setRange(0.1, 10000.0)
        self._butter_fs.setValue(100.0)
        self._butter_fs.setDecimals(1)
        self._butter_fs.setSuffix(" Hz")
        self._butter_fs.setToolTip(
            "Taxa de amostragem dos dados.\n"
            "Se não souber, deixe em 'auto' para estimar.",
        )
        params_layout.addRow("Taxa Amostragem:", self._butter_fs)

        self._butter_auto_fs = QCheckBox("Auto-detectar taxa")
        self._butter_auto_fs.setChecked(True)
        self._butter_auto_fs.setToolTip(
            "Estima taxa de amostragem automaticamente\n"
            "a partir dos timestamps dos dados.",
        )
        self._butter_auto_fs.toggled.connect(
            lambda checked: self._butter_fs.setEnabled(not checked),
        )
        params_layout.addRow(self._butter_auto_fs)

        layout.addWidget(params_group)

        # Opções avançadas
        adv_group = QGroupBox("⚙️ Opções Avançadas")
        adv_layout = QFormLayout(adv_group)

        self._butter_padlen = QSpinBox()
        self._butter_padlen.setRange(0, 1000)
        self._butter_padlen.setValue(0)
        self._butter_padlen.setToolTip(
            "Padding nas bordas para evitar artefatos.\n"
            "0 = automático.",
        )
        adv_layout.addRow("Padding:", self._butter_padlen)

        self._butter_forward_backward = QCheckBox("Filtfilt (zero-phase)")
        self._butter_forward_backward.setChecked(True)
        self._butter_forward_backward.setToolTip(
            "Aplicar filtro bidirecionalmente.\n"
            "Elimina defasagem, duplica ordem efetiva.",
        )
        adv_layout.addRow(self._butter_forward_backward)

        layout.addWidget(adv_group)
        layout.addStretch()

        self._tabs.addTab(tab, "📈 Butterworth")

    def _create_outliers_tab(self):
        """Tab de remoção de outliers"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Método
        method_group = QGroupBox("📊 Método de Detecção")
        method_layout = QFormLayout(method_group)

        self._outlier_method = QComboBox()
        self._outlier_method.addItems(["iqr", "zscore", "mad", "percentile"])
        self._outlier_method.setToolTip(
            "Método para detectar outliers:\n"
            "• IQR: Intervalo interquartil (Q1-1.5*IQR, Q3+1.5*IQR)\n"
            "• Z-Score: Desvios padrão da média\n"
            "• MAD: Median Absolute Deviation\n"
            "• Percentile: Remove extremos por percentil",
        )
        method_layout.addRow("Método:", self._outlier_method)

        layout.addWidget(method_group)

        # Parâmetros
        params_group = QGroupBox("🔧 Parâmetros")
        params_layout = QFormLayout(params_group)

        self._outlier_threshold = QDoubleSpinBox()
        self._outlier_threshold.setRange(0.5, 10.0)
        self._outlier_threshold.setValue(1.5)
        self._outlier_threshold.setDecimals(2)
        self._outlier_threshold.setToolTip(
            "Limiar para detecção:\n"
            "• IQR: Multiplicador (padrão 1.5)\n"
            "• Z-Score: Número de desvios (padrão 3)\n"
            "• MAD: Multiplicador (padrão 3.5)\n"
            "• Percentile: Percentagem a cortar",
        )
        params_layout.addRow("Limiar:", self._outlier_threshold)

        self._outlier_lower = QDoubleSpinBox()
        self._outlier_lower.setRange(0.0, 50.0)
        self._outlier_lower.setValue(5.0)
        self._outlier_lower.setDecimals(1)
        self._outlier_lower.setSuffix(" %")
        self._outlier_lower.setToolTip(
            "Percentil inferior (para método percentile).\n"
            "Valores abaixo deste percentil são removidos.",
        )
        params_layout.addRow("Percentil Inferior:", self._outlier_lower)

        self._outlier_upper = QDoubleSpinBox()
        self._outlier_upper.setRange(50.0, 100.0)
        self._outlier_upper.setValue(95.0)
        self._outlier_upper.setDecimals(1)
        self._outlier_upper.setSuffix(" %")
        self._outlier_upper.setToolTip(
            "Percentil superior (para método percentile).\n"
            "Valores acima deste percentil são removidos.",
        )
        params_layout.addRow("Percentil Superior:", self._outlier_upper)

        layout.addWidget(params_group)

        # Tratamento
        treatment_group = QGroupBox("🔄 Tratamento dos Outliers")
        treatment_layout = QFormLayout(treatment_group)

        self._outlier_action = QComboBox()
        self._outlier_action.addItems(["remove", "replace_nan", "replace_mean", "replace_median", "interpolate"])
        self._outlier_action.setToolTip(
            "O que fazer com outliers detectados:\n"
            "• remove: Remover pontos\n"
            "• replace_nan: Substituir por NaN\n"
            "• replace_mean: Substituir pela média\n"
            "• replace_median: Substituir pela mediana\n"
            "• interpolate: Interpolar valores",
        )
        treatment_layout.addRow("Ação:", self._outlier_action)

        self._outlier_window = QSpinBox()
        self._outlier_window.setRange(1, 100)
        self._outlier_window.setValue(10)
        self._outlier_window.setToolTip(
            "Janela para cálculo local de estatísticas.\n"
            "1 = estatísticas globais.",
        )
        treatment_layout.addRow("Janela Local:", self._outlier_window)

        layout.addWidget(treatment_group)
        layout.addStretch()

        self._tabs.addTab(tab, "🚫 Outliers")

    def _create_rolling_tab(self):
        """Tab de filtros rolling window"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Tipo de operação
        type_group = QGroupBox("📊 Operação Rolling")
        type_layout = QFormLayout(type_group)

        self._rolling_type = QComboBox()
        self._rolling_type.addItems([
            "mean", "median", "std", "var",
            "min", "max", "sum", "count", "quantile",
        ])
        self._rolling_type.setToolTip(
            "Operação a aplicar na janela móvel:\n"
            "• mean: Média móvel\n"
            "• median: Mediana móvel\n"
            "• std: Desvio padrão móvel\n"
            "• var: Variância móvel\n"
            "• min/max: Mínimo/máximo móvel\n"
            "• sum: Soma móvel\n"
            "• count: Contagem de valores válidos\n"
            "• quantile: Quantil específico",
        )
        type_layout.addRow("Tipo:", self._rolling_type)

        layout.addWidget(type_group)

        # Parâmetros
        params_group = QGroupBox("🔧 Parâmetros")
        params_layout = QFormLayout(params_group)

        self._rolling_window = QSpinBox()
        self._rolling_window.setRange(2, 1000)
        self._rolling_window.setValue(5)
        self._rolling_window.setToolTip(
            "Tamanho da janela móvel em pontos.\n"
            "Valores maiores = mais suavização.",
        )
        params_layout.addRow("Janela:", self._rolling_window)

        self._rolling_min_periods = QSpinBox()
        self._rolling_min_periods.setRange(1, 100)
        self._rolling_min_periods.setValue(1)
        self._rolling_min_periods.setToolTip(
            "Número mínimo de pontos necessários.\n"
            "Se a janela tiver menos pontos, retorna NaN.",
        )
        params_layout.addRow("Min. Períodos:", self._rolling_min_periods)

        self._rolling_center = QCheckBox("Centralizar janela")
        self._rolling_center.setChecked(False)
        self._rolling_center.setToolTip(
            "Se marcado, o resultado é alinhado ao centro da janela.\n"
            "Caso contrário, alinhado à direita.",
        )
        params_layout.addRow(self._rolling_center)

        self._rolling_quantile = QDoubleSpinBox()
        self._rolling_quantile.setRange(0.0, 1.0)
        self._rolling_quantile.setValue(0.5)
        self._rolling_quantile.setDecimals(2)
        self._rolling_quantile.setSingleStep(0.05)
        self._rolling_quantile.setToolTip(
            "Valor do quantil (para tipo 'quantile').\n"
            "0.5 = mediana, 0.25 = 1º quartil, etc.",
        )
        params_layout.addRow("Quantil:", self._rolling_quantile)

        layout.addWidget(params_group)

        # Opções
        options_group = QGroupBox("⚙️ Opções")
        options_layout = QFormLayout(options_group)

        self._rolling_win_type = QComboBox()
        self._rolling_win_type.addItems([
            "boxcar", "triang", "blackman", "hamming", "bartlett",
            "parzen", "bohman", "blackmanharris", "nuttall", "barthann",
            "kaiser", "gaussian", "exponential",
        ])
        self._rolling_win_type.setCurrentText("boxcar")
        self._rolling_win_type.setToolTip(
            "Tipo de janela para ponderação:\n"
            "• boxcar: Uniforme (padrão)\n"
            "• gaussian: Gaussiana\n"
            "• exponential: Exponencial\n"
            "• E outros tipos de janela de sinal",
        )
        options_layout.addRow("Tipo Janela:", self._rolling_win_type)

        self._rolling_std = QDoubleSpinBox()
        self._rolling_std.setRange(0.1, 10.0)
        self._rolling_std.setValue(1.0)
        self._rolling_std.setDecimals(2)
        self._rolling_std.setToolTip(
            "Desvio padrão para janela gaussiana.",
        )
        options_layout.addRow("Sigma (Gaussian):", self._rolling_std)

        layout.addWidget(options_group)
        layout.addStretch()

        self._tabs.addTab(tab, "📏 Rolling")

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Habilitar/desabilitar campos conforme seleção
        self._butter_type.currentTextChanged.connect(self._on_butter_type_changed)
        self._outlier_method.currentTextChanged.connect(self._on_outlier_method_changed)
        self._rolling_type.currentTextChanged.connect(self._on_rolling_type_changed)

        # Inicializar estados
        self._on_butter_type_changed(self._butter_type.currentText())
        self._on_outlier_method_changed(self._outlier_method.currentText())
        self._on_rolling_type_changed(self._rolling_type.currentText())

    def _on_butter_type_changed(self, filter_type: str):
        """Handler para mudança de tipo Butterworth"""
        # Band filters need both cutoffs
        self._butter_cutoff_high.setEnabled(True)

        if filter_type == "lowpass":
            self._butter_cutoff_low.setToolTip("Frequência de corte (máxima permitida)")
            self._butter_cutoff_high.setEnabled(False)
        elif filter_type == "highpass":
            self._butter_cutoff_low.setToolTip("Frequência de corte (mínima permitida)")
            self._butter_cutoff_high.setEnabled(False)

    def _on_outlier_method_changed(self, method: str):
        """Handler para mudança de método de outliers"""
        is_percentile = method == "percentile"
        self._outlier_lower.setEnabled(is_percentile)
        self._outlier_upper.setEnabled(is_percentile)
        self._outlier_threshold.setEnabled(not is_percentile)

        # Ajustar tooltip do threshold
        if method == "iqr":
            self._outlier_threshold.setValue(1.5)
            self._outlier_threshold.setToolTip("Multiplicador do IQR (padrão: 1.5)")
        elif method == "zscore":
            self._outlier_threshold.setValue(3.0)
            self._outlier_threshold.setToolTip("Número de desvios padrão (padrão: 3.0)")
        elif method == "mad":
            self._outlier_threshold.setValue(3.5)
            self._outlier_threshold.setToolTip("Multiplicador do MAD (padrão: 3.5)")

    def _on_rolling_type_changed(self, rolling_type: str):
        """Handler para mudança de tipo rolling"""
        is_quantile = rolling_type == "quantile"
        self._rolling_quantile.setEnabled(is_quantile)

    def _get_filter_config(self) -> dict[str, Any]:
        """Obtém configuração do filtro baseada na tab ativa"""
        current_tab = self._tabs.currentIndex()

        if current_tab == 0:  # Butterworth
            config = {
                "type": "butterworth",
                "filter_type": self._butter_type.currentText(),
                "order": self._butter_order.value(),
                "cutoff_low": self._butter_cutoff_low.value(),
                "cutoff_high": self._butter_cutoff_high.value(),
                "auto_fs": self._butter_auto_fs.isChecked(),
                "fs": self._butter_fs.value() if not self._butter_auto_fs.isChecked() else None,
                "padlen": self._butter_padlen.value(),
                "filtfilt": self._butter_forward_backward.isChecked(),
            }
        elif current_tab == 1:  # Outliers
            config = {
                "type": "outliers",
                "method": self._outlier_method.currentText(),
                "threshold": self._outlier_threshold.value(),
                "lower_percentile": self._outlier_lower.value(),
                "upper_percentile": self._outlier_upper.value(),
                "action": self._outlier_action.currentText(),
                "window": self._outlier_window.value(),
            }
        else:  # Rolling
            config = {
                "type": "rolling",
                "operation": self._rolling_type.currentText(),
                "window": self._rolling_window.value(),
                "min_periods": self._rolling_min_periods.value(),
                "center": self._rolling_center.isChecked(),
                "quantile": self._rolling_quantile.value(),
                "win_type": self._rolling_win_type.currentText(),
                "std": self._rolling_std.value(),
            }

        return config

    def _preview_filter(self):
        """Preview do filtro (emite sinal com preview=True)"""
        config = self._get_filter_config()
        config["preview"] = True
        self.filter_applied.emit(config)

    def _apply_filter(self):
        """Aplica o filtro e fecha o diálogo"""
        config = self._get_filter_config()
        config["preview"] = False
        self.filter_applied.emit(config)
        self.accept()

    def get_config(self) -> dict[str, Any] | None:
        """Retorna configuração se diálogo foi aceito"""
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_filter_config()
        return None


def show_filter_dialog(parent: QWidget | None = None) -> dict[str, Any] | None:
    """
    Conveniência para mostrar diálogo de filtro

    Returns:
        Configuração do filtro ou None se cancelado
    """
    dialog = FilterDialog(parent)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_config()

    return None
