"""
SmoothingDialog - Diálogo de configuração de suavização

Métodos disponíveis:
- Gaussian: Suavização com kernel Gaussiano
- Moving Average: Média móvel simples/ponderada
- Savitzky-Golay: Suavização polinomial
- Exponential: Suavização exponencial
- Median: Filtro mediana

Interface carregada de: desktop/ui_files/smoothingDialog.ui
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
    QGroupBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class SmoothingDialog(QDialog, UiLoaderMixin):
    """
    Diálogo para configuração de suavização de dados

    Métodos suportados:
    - Gaussian: Filtro Gaussiano
    - Moving Average: Média móvel
    - Savitzky-Golay: Suavização polinomial local
    - Exponential: Suavização exponencial
    - Median: Filtro mediana
    
    Interface 100% carregada do arquivo .ui via UiLoaderMixin.
    Nenhum widget é criado programaticamente.
    """
    
    # Arquivo .ui que define a interface completa
    UI_FILE = "smoothingDialog.ui"

    # Sinal emitido quando suavização é aplicada
    smoothing_applied = pyqtSignal(dict)  # config

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

        logger.debug("smoothing_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Busca referências a todos os widgets definidos no arquivo .ui"""
        
        # === Widgets de método ===
        self._method = self.findChild(QComboBox, "methodCombo")
        
        # === Widgets de parâmetros gerais ===
        self._window = self.findChild(QSpinBox, "windowSpin")
        self._window_slider = self.findChild(QSlider, "windowSlider")
        self._sigma = self.findChild(QDoubleSpinBox, "sigmaSpin")
        self._sigma_slider = self.findChild(QSlider, "sigmaSlider")
        self._boundary_mode = self.findChild(QComboBox, "boundaryModeCombo")
        self._preserve_nan = self.findChild(QCheckBox, "preserveNanCheck")
        
        # === Widgets Savitzky-Golay ===
        self._savgol_group = self.findChild(QGroupBox, "savgolGroup")
        self._polyorder = self.findChild(QSpinBox, "polyorderSpin")
        self._deriv = self.findChild(QSpinBox, "derivSpin")
        self._delta = self.findChild(QDoubleSpinBox, "deltaSpin")
        
        # === Widgets Exponencial ===
        self._exp_group = self.findChild(QGroupBox, "expGroup")
        self._alpha = self.findChild(QDoubleSpinBox, "alphaSpin")
        self._adjust = self.findChild(QCheckBox, "adjustCheck")
        
        # === Botões ===
        self._button_box = self.findChild(QDialogButtonBox, "buttonBox")
        self._preview_button = self.findChild(QPushButton, "previewButton")
        
        # Validação: todos os widgets essenciais devem existir
        self._validate_widgets()
        
        logger.debug("smoothing_dialog_ui_widgets_loaded")

    def _validate_widgets(self):
        """Valida que todos os widgets essenciais foram encontrados no .ui"""
        required_widgets = {
            # Método
            "methodCombo": self._method,
            # Parâmetros gerais
            "windowSpin": self._window,
            "windowSlider": self._window_slider,
            "sigmaSpin": self._sigma,
            "sigmaSlider": self._sigma_slider,
            "boundaryModeCombo": self._boundary_mode,
            "preserveNanCheck": self._preserve_nan,
            # Savitzky-Golay
            "savgolGroup": self._savgol_group,
            "polyorderSpin": self._polyorder,
            "derivSpin": self._deriv,
            "deltaSpin": self._delta,
            # Exponencial
            "expGroup": self._exp_group,
            "alphaSpin": self._alpha,
            "adjustCheck": self._adjust,
            # Botões
            "buttonBox": self._button_box,
        }
        
        missing = [name for name, widget in required_widgets.items() if widget is None]
        
        if missing:
            raise RuntimeError(
                f"Widgets ausentes no arquivo .ui: {', '.join(missing)}. "
                f"Verifique se {self.UI_FILE} está completo."
            )

    def _setup_connections(self):
        """Configura conexões de sinais entre widgets"""
        # === Sincronização de sliders ===
        self._window_slider.valueChanged.connect(self._on_window_slider_changed)
        self._window.valueChanged.connect(self._window_slider.setValue)

        self._sigma_slider.valueChanged.connect(self._on_sigma_slider_changed)
        self._sigma.valueChanged.connect(lambda v: self._sigma_slider.setValue(int(v * 10)))
        
        # === Mudança de método ===
        self._method.currentTextChanged.connect(self._on_method_changed)
        
        # === Validação Savitzky-Golay ===
        self._window.valueChanged.connect(self._validate_polyorder)
        
        # === Botões ===
        if self._button_box:
            self._button_box.accepted.connect(self._apply_smoothing)
            self._button_box.rejected.connect(self.reject)
        
        if self._preview_button:
            self._preview_button.clicked.connect(self._preview_smoothing)

    def _initialize_widget_states(self):
        """Inicializa estados dos widgets baseados nos valores atuais"""
        # Inicializar visibilidade de grupos
        self._on_method_changed(self._method.currentText())
        
        # Sincronizar sliders com spinboxes
        self._window_slider.setValue(self._window.value())
        self._sigma_slider.setValue(int(self._sigma.value() * 10))

    def _on_window_slider_changed(self, value: int):
        """Handler para slider de janela - garante valor ímpar"""
        if value % 2 == 0:
            value += 1
        self._window.setValue(value)

    def _on_sigma_slider_changed(self, value: int):
        """Handler para slider de sigma"""
        self._sigma.setValue(value / 10.0)

    def _on_method_changed(self, method: str):
        """Handler para mudança de método de suavização"""
        # Mostrar/ocultar grupos específicos
        self._savgol_group.setVisible(method == "savitzky_golay")
        self._exp_group.setVisible(method == "exponential")

        # Habilitar/desabilitar sigma (apenas para gaussian)
        is_gaussian = method == "gaussian"
        self._sigma.setEnabled(is_gaussian)
        self._sigma_slider.setEnabled(is_gaussian)

        # Ajustar janela padrão conforme método
        if method == "gaussian":
            self._window.setValue(7)
        elif method == "moving_average":
            self._window.setValue(5)
        elif method == "savitzky_golay":
            self._window.setValue(11)
            self._validate_polyorder()
        elif method == "median":
            self._window.setValue(3)
        elif method == "exponential":
            self._window.setValue(5)

    def _validate_polyorder(self):
        """Garante que polyorder < window para Savitzky-Golay"""
        if self._method.currentText() == "savitzky_golay":
            max_order = self._window.value() - 1
            self._polyorder.setMaximum(max_order)
            if self._polyorder.value() >= max_order:
                self._polyorder.setValue(max(1, max_order - 1))

    def _get_smoothing_config(self) -> dict[str, Any]:
        """Obtém configuração de suavização baseada nos widgets"""
        method = self._method.currentText()

        config = {
            "method": method,
            "window": self._window.value(),
            "preserve_nan": self._preserve_nan.isChecked(),
            "boundary_mode": self._boundary_mode.currentText(),
        }

        # Parâmetros específicos por método
        if method == "gaussian":
            config["sigma"] = self._sigma.value()
        elif method == "savitzky_golay":
            config["polyorder"] = self._polyorder.value()
            config["deriv"] = self._deriv.value()
            config["delta"] = self._delta.value()
        elif method == "exponential":
            config["alpha"] = self._alpha.value()
            config["adjust"] = self._adjust.isChecked()

        return config

    def _preview_smoothing(self):
        """Preview da suavização (emite sinal com preview=True)"""
        config = self._get_smoothing_config()
        config["preview"] = True
        self.smoothing_applied.emit(config)
        logger.debug("smoothing_preview_requested", config=config)

    def _apply_smoothing(self):
        """Aplica suavização e fecha o diálogo"""
        config = self._get_smoothing_config()
        config["preview"] = False
        self.smoothing_applied.emit(config)
        logger.debug("smoothing_applied", config=config)
        self.accept()

    def get_config(self) -> dict[str, Any] | None:
        """
        Retorna configuração de suavização se diálogo foi aceito
        
        Returns:
            dict com configuração ou None se cancelado
        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_smoothing_config()
        return None
    
    def set_config(self, config: dict[str, Any]):
        """
        Define configuração do diálogo a partir de um dict
        
        Args:
            config: Dicionário com configuração de suavização
        """
        if "method" in config:
            self._method.setCurrentText(config["method"])
        if "window" in config:
            self._window.setValue(config["window"])
        if "preserve_nan" in config:
            self._preserve_nan.setChecked(config["preserve_nan"])
        if "boundary_mode" in config:
            self._boundary_mode.setCurrentText(config["boundary_mode"])
        
        # Parâmetros específicos
        if "sigma" in config:
            self._sigma.setValue(config["sigma"])
        if "polyorder" in config:
            self._polyorder.setValue(config["polyorder"])
        if "deriv" in config:
            self._deriv.setValue(config["deriv"])
        if "delta" in config:
            self._delta.setValue(config["delta"])
        if "alpha" in config:
            self._alpha.setValue(config["alpha"])
        if "adjust" in config:
            self._adjust.setChecked(config["adjust"])
        
        logger.debug("smoothing_config_loaded", method=config.get("method"))


def show_smoothing_dialog(parent: QWidget | None = None) -> dict[str, Any] | None:
    """
    Função de conveniência para mostrar o diálogo de suavização

    Args:
        parent: Widget pai do diálogo
        
    Returns:
        Dicionário com configuração ou None se cancelado
    """
    dialog = SmoothingDialog(parent)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_config()

    return None
