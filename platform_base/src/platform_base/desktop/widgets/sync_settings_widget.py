"""
SyncSettingsWidget - Widget de configuração de sincronização

Fornece controles para configurar métodos de sincronização de séries temporais.

Interface carregada de: desktop/ui_files/syncSettingsWidget.ui
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class SyncSettingsWidget(QWidget, UiLoaderMixin):
    """Widget para configuração de parâmetros de sincronização."""

    UI_FILE = "syncSettingsWidget.ui"

    # Signals
    settings_changed = pyqtSignal(dict)

    def __init__(
        self,
        session_state: SessionState | None = None,
        signal_hub: SignalHub | None = None,
        parent: QWidget | None = None,
    ):
        """
        Inicializa o SyncSettingsWidget.

        Args:
            session_state: Estado da sessão (opcional)
            signal_hub: Hub de sinais (opcional)
            parent: Widget pai
        """
        super().__init__(parent)

        self.session_state = session_state
        self.signal_hub = signal_hub

        # Inicializar widgets
        self.sync_method_combo: QComboBox | None = None
        self.target_freq_spin: QDoubleSpinBox | None = None
        self.resample_method_combo: QComboBox | None = None

        # Carregar interface
        if not self._load_ui():
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()

        logger.debug("sync_settings_widget_initialized")

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Obter widgets do arquivo .ui
        self.sync_method_combo = self.findChild(QComboBox, "syncMethodCombo")
        self.target_freq_spin = self.findChild(QDoubleSpinBox, "targetFreqSpin")
        self.resample_method_combo = self.findChild(QComboBox, "resampleMethodCombo")

        # Conectar sinais
        if self.sync_method_combo:
            self.sync_method_combo.currentTextChanged.connect(self._emit_settings)

        if self.target_freq_spin:
            self.target_freq_spin.valueChanged.connect(self._emit_settings)

        if self.resample_method_combo:
            self.resample_method_combo.currentTextChanged.connect(self._emit_settings)

        logger.debug("sync_settings_ui_loaded_from_file")

    def _setup_ui_fallback(self):
        """Cria interface programaticamente como fallback."""
        layout = QFormLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Método de sincronização
        self.sync_method_combo = QComboBox()
        self.sync_method_combo.addItems([
            "common_grid_interpolate",
            "kalman_align",
            "dtw_align",
        ])
        self.sync_method_combo.currentTextChanged.connect(self._emit_settings)
        layout.addRow("Method:", self.sync_method_combo)

        # Frequência alvo
        self.target_freq_spin = QDoubleSpinBox()
        self.target_freq_spin.setRange(0.001, 1000.0)
        self.target_freq_spin.setValue(1.0)
        self.target_freq_spin.setSuffix(" Hz")
        self.target_freq_spin.setDecimals(3)
        self.target_freq_spin.valueChanged.connect(self._emit_settings)
        layout.addRow("Target Frequency:", self.target_freq_spin)

        # Método de reamostragem
        self.resample_method_combo = QComboBox()
        self.resample_method_combo.addItems(["linear", "cubic", "nearest"])
        self.resample_method_combo.currentTextChanged.connect(self._emit_settings)
        layout.addRow("Resample Method:", self.resample_method_combo)

        logger.debug("sync_settings_ui_created_fallback")

    def _emit_settings(self):
        """Emite sinal com configurações atualizadas."""
        self.settings_changed.emit(self.get_settings())

    def get_settings(self) -> dict[str, Any]:
        """
        Retorna as configurações atuais.

        Returns:
            Dicionário com as configurações de sincronização
        """
        return {
            "method": self.sync_method_combo.currentText() if self.sync_method_combo else "",
            "target_frequency": self.target_freq_spin.value() if self.target_freq_spin else 1.0,
            "resample_method": self.resample_method_combo.currentText() if self.resample_method_combo else "linear",
        }

    def set_settings(self, settings: dict[str, Any]):
        """
        Define as configurações.

        Args:
            settings: Dicionário com as configurações
        """
        if self.sync_method_combo and "method" in settings:
            index = self.sync_method_combo.findText(settings["method"])
            if index >= 0:
                self.sync_method_combo.setCurrentIndex(index)

        if self.target_freq_spin and "target_frequency" in settings:
            self.target_freq_spin.setValue(settings["target_frequency"])

        if self.resample_method_combo and "resample_method" in settings:
            index = self.resample_method_combo.findText(settings["resample_method"])
            if index >= 0:
                self.resample_method_combo.setCurrentIndex(index)

    def get_method(self) -> str:
        """Retorna o método de sincronização selecionado."""
        return self.sync_method_combo.currentText() if self.sync_method_combo else ""

    def get_target_frequency(self) -> float:
        """Retorna a frequência alvo."""
        return self.target_freq_spin.value() if self.target_freq_spin else 1.0

    def get_resample_method(self) -> str:
        """Retorna o método de reamostragem."""
        return self.resample_method_combo.currentText() if self.resample_method_combo else "linear"
