"""
SmoothingDialog - Diálogo de configuração de suavização

Métodos disponíveis:
- Gaussian: Suavização com kernel Gaussiano
- Moving Average: Média móvel simples/ponderada
- Savitzky-Golay: Suavização polinomial
- Exponential: Suavização exponencial
- Median: Filtro mediana

Interface carregada de: desktop/ui_files/smoothingDialog.ui
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
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
    QSlider,
    QSpinBox,
    QVBoxLayout,
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
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """
    
    # Arquivo .ui que define a interface
    UI_FILE = "smoothingDialog.ui"

    smoothing_applied = pyqtSignal(dict)  # config

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()
        
        self._setup_connections()

        logger.debug("smoothing_dialog_initialized", ui_loaded=self._ui_loaded)

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
        
        logger.debug("smoothing_dialog_ui_loaded_from_file")

    def _create_content_widgets(self, layout: QVBoxLayout):
        """Cria widgets de conteúdo quando o .ui está vazio"""
        # Header
        header = QLabel("〰️ Configurar Suavização de Dados")
        header.setFont(QFont("", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #0d6efd; padding: 10px;")
        layout.addWidget(header)

        # Método de suavização
        method_group = QGroupBox("📊 Método de Suavização")
        method_layout = QFormLayout(method_group)

        self._method = QComboBox()
        self._method.addItems([
            "gaussian", "moving_average", "savitzky_golay",
            "exponential", "median",
        ])
        method_layout.addRow("Método:", self._method)
        layout.addWidget(method_group)
        
        # Parâmetros serão adicionados via _update_params_visibility

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Sincronizar sliders com spinboxes
        self._window_slider.valueChanged.connect(self._on_window_slider_changed)
        self._window.valueChanged.connect(self._window_slider.setValue)

        self._sigma_slider.valueChanged.connect(self._on_sigma_slider_changed)
        self._sigma.valueChanged.connect(lambda v: self._sigma_slider.setValue(int(v * 10)))

        # Mostrar/ocultar grupos baseado no método
        self._method.currentTextChanged.connect(self._on_method_changed)

        # Inicializar estado
        self._on_method_changed(self._method.currentText())

    def _on_window_slider_changed(self, value: int):
        """Handler para slider de janela"""
        # Garantir valor ímpar
        if value % 2 == 0:
            value += 1
        self._window.setValue(value)

    def _on_sigma_slider_changed(self, value: int):
        """Handler para slider de sigma"""
        self._sigma.setValue(value / 10.0)

    def _on_method_changed(self, method: str):
        """Handler para mudança de método"""
        # Mostrar/ocultar grupos específicos
        self._savgol_group.setVisible(method == "savitzky_golay")
        self._exp_group.setVisible(method == "exponential")

        # Habilitar/desabilitar sigma
        self._sigma.setEnabled(method == "gaussian")
        self._sigma_slider.setEnabled(method == "gaussian")

        # Ajustar janela padrão conforme método
        if method == "gaussian":
            self._window.setValue(7)
        elif method == "moving_average":
            self._window.setValue(5)
        elif method == "savitzky_golay":
            self._window.setValue(11)
        elif method == "median":
            self._window.setValue(3)

        # Validar polyorder < window
        if method == "savitzky_golay":
            self._validate_polyorder()

    def _validate_polyorder(self):
        """Garante que polyorder < window"""
        max_order = self._window.value() - 1
        self._polyorder.setMaximum(max_order)
        if self._polyorder.value() >= max_order:
            self._polyorder.setValue(max_order - 1)

    def _get_smoothing_config(self) -> dict[str, Any]:
        """Obtém configuração de suavização"""
        method = self._method.currentText()

        config = {
            "method": method,
            "window": self._window.value(),
            "preserve_nan": self._preserve_nan.isChecked(),
            "boundary_mode": self._boundary_mode.currentText(),
        }

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
        """Preview da suavização"""
        config = self._get_smoothing_config()
        config["preview"] = True
        self.smoothing_applied.emit(config)

    def _apply_smoothing(self):
        """Aplica suavização e fecha diálogo"""
        config = self._get_smoothing_config()
        config["preview"] = False
        self.smoothing_applied.emit(config)
        self.accept()

    def get_config(self) -> dict[str, Any] | None:
        """Retorna configuração se diálogo foi aceito"""
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_smoothing_config()
        return None


def show_smoothing_dialog(parent: QWidget | None = None) -> dict[str, Any] | None:
    """
    Conveniência para mostrar diálogo de suavização

    Returns:
        Configuração de suavização ou None se cancelado
    """
    dialog = SmoothingDialog(parent)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_config()

    return None
