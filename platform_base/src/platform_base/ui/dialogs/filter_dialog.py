"""
FilterDialog - Diálogo de configuração de filtros

Filtros disponíveis:
- Butterworth (low-pass, high-pass, band-pass)
- Remoção de outliers (IQR, Z-score, MAD)
- Rolling window

Interface carregada de: desktop/ui_files/filterDialog.ui
Todos os widgets são definidos no arquivo .ui - NENHUMA CRIAÇÃO PROGRAMÁTICA.
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
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
    
    Interface 100% carregada do arquivo .ui via UiLoaderMixin.
    Nenhum widget é criado programaticamente.
    """
    
    # Arquivo .ui que define a interface completa
    UI_FILE = "filterDialog.ui"

    # Sinal emitido quando filtro é aplicado
    filter_applied = pyqtSignal(dict)  # config

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(
                f"Falha ao carregar arquivo UI: {self.UI_FILE}. "
                "Verifique se existe em desktop/ui_files/"
            )
        
        # Busca referências aos widgets do .ui
        self._setup_ui_from_file()
        
        # Configura conexões de sinais
        self._setup_connections()
        
        # Inicializa estados dos widgets
        self._initialize_widget_states()

        logger.debug("filter_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Busca referências a todos os widgets definidos no arquivo .ui"""
        
        # === Widgets principais ===
        self._tabs = self.findChild(QTabWidget, "filterTabWidget")
        self._button_box = self.findChild(QDialogButtonBox, "buttonBox")
        self._preview_button = self.findChild(QPushButton, "previewButton")
        
        # === Widgets da aba Butterworth ===
        self._butter_type = self.findChild(QComboBox, "butterTypeCombo")
        self._butter_order = self.findChild(QSpinBox, "butterOrderSpin")
        self._butter_cutoff_low = self.findChild(QDoubleSpinBox, "butterCutoffLowSpin")
        self._butter_cutoff_high = self.findChild(QDoubleSpinBox, "butterCutoffHighSpin")
        self._butter_fs = self.findChild(QDoubleSpinBox, "butterFsSpin")
        self._butter_auto_fs = self.findChild(QCheckBox, "butterAutoFsCheck")
        self._butter_padlen = self.findChild(QSpinBox, "butterPadlenSpin")
        self._butter_forward_backward = self.findChild(QCheckBox, "butterFiltfiltCheck")
        
        # === Widgets da aba Outliers ===
        self._outlier_method = self.findChild(QComboBox, "outlierMethodCombo")
        self._outlier_threshold = self.findChild(QDoubleSpinBox, "outlierThresholdSpin")
        self._outlier_lower = self.findChild(QDoubleSpinBox, "outlierLowerSpin")
        self._outlier_upper = self.findChild(QDoubleSpinBox, "outlierUpperSpin")
        self._outlier_action = self.findChild(QComboBox, "outlierActionCombo")
        self._outlier_window = self.findChild(QSpinBox, "outlierWindowSpin")
        
        # === Widgets da aba Rolling ===
        self._rolling_type = self.findChild(QComboBox, "rollingTypeCombo")
        self._rolling_window = self.findChild(QSpinBox, "rollingWindowSpin")
        self._rolling_min_periods = self.findChild(QSpinBox, "rollingMinPeriodsSpin")
        self._rolling_center = self.findChild(QCheckBox, "rollingCenterCheck")
        self._rolling_quantile = self.findChild(QDoubleSpinBox, "rollingQuantileSpin")
        self._rolling_win_type = self.findChild(QComboBox, "rollingWinTypeCombo")
        self._rolling_std = self.findChild(QDoubleSpinBox, "rollingStdSpin")
        
        # Validação: todos os widgets essenciais devem existir
        self._validate_widgets()
        
        logger.debug("filter_dialog_ui_widgets_loaded")

    def _validate_widgets(self):
        """Valida que todos os widgets essenciais foram encontrados no .ui"""
        required_widgets = {
            # Principais
            "filterTabWidget": self._tabs,
            "buttonBox": self._button_box,
            # Butterworth
            "butterTypeCombo": self._butter_type,
            "butterOrderSpin": self._butter_order,
            "butterCutoffLowSpin": self._butter_cutoff_low,
            "butterCutoffHighSpin": self._butter_cutoff_high,
            "butterFsSpin": self._butter_fs,
            "butterAutoFsCheck": self._butter_auto_fs,
            "butterPadlenSpin": self._butter_padlen,
            "butterFiltfiltCheck": self._butter_forward_backward,
            # Outliers
            "outlierMethodCombo": self._outlier_method,
            "outlierThresholdSpin": self._outlier_threshold,
            "outlierLowerSpin": self._outlier_lower,
            "outlierUpperSpin": self._outlier_upper,
            "outlierActionCombo": self._outlier_action,
            "outlierWindowSpin": self._outlier_window,
            # Rolling
            "rollingTypeCombo": self._rolling_type,
            "rollingWindowSpin": self._rolling_window,
            "rollingMinPeriodsSpin": self._rolling_min_periods,
            "rollingCenterCheck": self._rolling_center,
            "rollingQuantileSpin": self._rolling_quantile,
            "rollingWinTypeCombo": self._rolling_win_type,
            "rollingStdSpin": self._rolling_std,
        }
        
        missing = [name for name, widget in required_widgets.items() if widget is None]
        
        if missing:
            raise RuntimeError(
                f"Widgets ausentes no arquivo .ui: {', '.join(missing)}. "
                f"Verifique se {self.UI_FILE} está completo."
            )

    def _setup_connections(self):
        """Configura conexões de sinais entre widgets"""
        # === Conexões da aba Butterworth ===
        self._butter_type.currentTextChanged.connect(self._on_butter_type_changed)
        self._butter_auto_fs.toggled.connect(
            lambda checked: self._butter_fs.setEnabled(not checked)
        )
        
        # === Conexões da aba Outliers ===
        self._outlier_method.currentTextChanged.connect(self._on_outlier_method_changed)
        
        # === Conexões da aba Rolling ===
        self._rolling_type.currentTextChanged.connect(self._on_rolling_type_changed)
        
        # === Conexões dos botões ===
        if self._button_box:
            self._button_box.accepted.connect(self._apply_filter)
            self._button_box.rejected.connect(self.reject)
        
        if self._preview_button:
            self._preview_button.clicked.connect(self._preview_filter)

    def _initialize_widget_states(self):
        """Inicializa estados dos widgets baseados nos valores atuais"""
        # Inicializar estado Butterworth
        self._on_butter_type_changed(self._butter_type.currentText())
        
        # Inicializar estado Outliers
        self._on_outlier_method_changed(self._outlier_method.currentText())
        
        # Inicializar estado Rolling
        self._on_rolling_type_changed(self._rolling_type.currentText())
        
        # Inicializar estado de auto-detecção de taxa de amostragem
        if self._butter_auto_fs.isChecked():
            self._butter_fs.setEnabled(False)

    def _on_butter_type_changed(self, filter_type: str):
        """Handler para mudança de tipo de filtro Butterworth"""
        # Filtros de banda precisam de ambas as frequências de corte
        self._butter_cutoff_high.setEnabled(True)

        if filter_type == "lowpass":
            self._butter_cutoff_low.setToolTip("Frequência de corte (máxima permitida)")
            self._butter_cutoff_high.setEnabled(False)
        elif filter_type == "highpass":
            self._butter_cutoff_low.setToolTip("Frequência de corte (mínima permitida)")
            self._butter_cutoff_high.setEnabled(False)
        elif filter_type == "bandpass":
            self._butter_cutoff_low.setToolTip("Frequência inferior da banda passante")
            self._butter_cutoff_high.setToolTip("Frequência superior da banda passante")
        elif filter_type == "bandstop":
            self._butter_cutoff_low.setToolTip("Frequência inferior da banda bloqueada")
            self._butter_cutoff_high.setToolTip("Frequência superior da banda bloqueada")

    def _on_outlier_method_changed(self, method: str):
        """Handler para mudança de método de detecção de outliers"""
        is_percentile = method == "percentile"
        
        # Habilita/desabilita campos de percentil
        self._outlier_lower.setEnabled(is_percentile)
        self._outlier_upper.setEnabled(is_percentile)
        self._outlier_threshold.setEnabled(not is_percentile)

        # Ajusta valor e tooltip do threshold conforme método
        if method == "iqr":
            self._outlier_threshold.setValue(1.5)
            self._outlier_threshold.setToolTip(
                "Multiplicador do IQR (padrão: 1.5)\n"
                "Outliers: valores fora de [Q1-k*IQR, Q3+k*IQR]"
            )
        elif method == "zscore":
            self._outlier_threshold.setValue(3.0)
            self._outlier_threshold.setToolTip(
                "Número de desvios padrão (padrão: 3.0)\n"
                "Outliers: valores a mais de k desvios da média"
            )
        elif method == "mad":
            self._outlier_threshold.setValue(3.5)
            self._outlier_threshold.setToolTip(
                "Multiplicador do MAD (padrão: 3.5)\n"
                "MAD = Median Absolute Deviation"
            )
        elif method == "percentile":
            self._outlier_threshold.setToolTip("Não usado para método percentile")

    def _on_rolling_type_changed(self, rolling_type: str):
        """Handler para mudança de tipo de operação rolling"""
        is_quantile = rolling_type == "quantile"
        self._rolling_quantile.setEnabled(is_quantile)
        
        if is_quantile:
            self._rolling_quantile.setToolTip(
                "Valor do quantil a calcular (0.0 a 1.0)\n"
                "0.5 = mediana, 0.25 = 1º quartil, 0.75 = 3º quartil"
            )

    def _get_filter_config(self) -> dict[str, Any]:
        """Obtém configuração do filtro baseada na aba ativa"""
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
        else:  # Rolling (tab index 2)
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
        logger.debug("filter_preview_requested", config=config)

    def _apply_filter(self):
        """Aplica o filtro e fecha o diálogo"""
        config = self._get_filter_config()
        config["preview"] = False
        self.filter_applied.emit(config)
        logger.debug("filter_applied", config=config)
        self.accept()

    def get_config(self) -> dict[str, Any] | None:
        """
        Retorna configuração do filtro se diálogo foi aceito
        
        Returns:
            dict com configuração do filtro ou None se cancelado
        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_filter_config()
        return None
    
    def set_config(self, config: dict[str, Any]):
        """
        Define configuração do diálogo a partir de um dict
        
        Args:
            config: Dicionário com configuração do filtro
        """
        filter_type = config.get("type", "butterworth")
        
        if filter_type == "butterworth":
            self._tabs.setCurrentIndex(0)
            if "filter_type" in config:
                self._butter_type.setCurrentText(config["filter_type"])
            if "order" in config:
                self._butter_order.setValue(config["order"])
            if "cutoff_low" in config:
                self._butter_cutoff_low.setValue(config["cutoff_low"])
            if "cutoff_high" in config:
                self._butter_cutoff_high.setValue(config["cutoff_high"])
            if "auto_fs" in config:
                self._butter_auto_fs.setChecked(config["auto_fs"])
            if "fs" in config and config["fs"] is not None:
                self._butter_fs.setValue(config["fs"])
            if "padlen" in config:
                self._butter_padlen.setValue(config["padlen"])
            if "filtfilt" in config:
                self._butter_forward_backward.setChecked(config["filtfilt"])
                
        elif filter_type == "outliers":
            self._tabs.setCurrentIndex(1)
            if "method" in config:
                self._outlier_method.setCurrentText(config["method"])
            if "threshold" in config:
                self._outlier_threshold.setValue(config["threshold"])
            if "lower_percentile" in config:
                self._outlier_lower.setValue(config["lower_percentile"])
            if "upper_percentile" in config:
                self._outlier_upper.setValue(config["upper_percentile"])
            if "action" in config:
                self._outlier_action.setCurrentText(config["action"])
            if "window" in config:
                self._outlier_window.setValue(config["window"])
                
        elif filter_type == "rolling":
            self._tabs.setCurrentIndex(2)
            if "operation" in config:
                self._rolling_type.setCurrentText(config["operation"])
            if "window" in config:
                self._rolling_window.setValue(config["window"])
            if "min_periods" in config:
                self._rolling_min_periods.setValue(config["min_periods"])
            if "center" in config:
                self._rolling_center.setChecked(config["center"])
            if "quantile" in config:
                self._rolling_quantile.setValue(config["quantile"])
            if "win_type" in config:
                self._rolling_win_type.setCurrentText(config["win_type"])
            if "std" in config:
                self._rolling_std.setValue(config["std"])
        
        logger.debug("filter_config_loaded", filter_type=filter_type)


def show_filter_dialog(parent: QWidget | None = None) -> dict[str, Any] | None:
    """
    Função de conveniência para mostrar o diálogo de filtro

    Args:
        parent: Widget pai do diálogo
        
    Returns:
        Dicionário com configuração do filtro ou None se cancelado
    """
    dialog = FilterDialog(parent)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_config()

    return None
