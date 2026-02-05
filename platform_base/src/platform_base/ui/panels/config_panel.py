"""
ConfigPanel - Painel de configurações da aplicação

Características:
- Configurações de visualização
- Preferências de usuário
- Opções de performance
- Temas e aparência
- Persistência via QSettings

Autor: Platform Base Team
Versão: 2.0.0
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QSettings, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
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

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class ColorButton(QPushButton):
    """Botão para seleção de cor"""

    color_changed = pyqtSignal(str)  # Hex color

    def __init__(self, color: str = "#0d6efd", parent: QWidget | None = None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(32, 32)
        self._update_style()
        self.clicked.connect(self._pick_color)

    def _update_style(self):
        """Atualiza estilo com a cor atual"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid #dee2e6;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #0d6efd;
            }}
        """)

    def _pick_color(self):
        """Abre diálogo de seleção de cor"""
        from PyQt6.QtGui import QColor

        color = QColorDialog.getColor(QColor(self._color), self, "Selecionar Cor")
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.color_changed.emit(self._color)

    def get_color(self) -> str:
        """Retorna cor atual em hex"""
        return self._color

    def set_color(self, color: str):
        """Define cor atual"""
        self._color = color
        self._update_style()


class ConfigPanel(QWidget, UiLoaderMixin):
    """
    Painel de configurações da aplicação

    Signals:
        config_changed: Emitido quando qualquer configuração muda
        theme_changed: Emitido quando tema muda
        performance_changed: Emitido quando config de performance muda
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "configPanel.ui"

    config_changed = pyqtSignal(str, object)  # key, value
    theme_changed = pyqtSignal(str)  # theme name
    performance_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._settings = QSettings("PlatformBase", "Desktop")
        self._config: dict[str, Any] = {}

        # Carregar interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()
        
        self._load_settings()
        self._connect_signals()

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Tabs principais
        self.tabs = self.findChild(QTabWidget, "configTabs")
        
        # Botões de ação
        reset_btn = self.findChild(QPushButton, "resetBtn")
        apply_btn = self.findChild(QPushButton, "applyBtn")
        
        if reset_btn:
            reset_btn.clicked.connect(self._reset_defaults)
        if apply_btn:
            apply_btn.clicked.connect(self._apply_settings)

    def _connect_signals(self):
        """Conecta signals para detecção de mudanças"""
        # Conecta todos os widgets para emitir config_changed
        self._theme_combo.currentTextChanged.connect(
            lambda v: self._on_config_change("theme", v),
        )
        self._show_grid.stateChanged.connect(
            lambda v: self._on_config_change("show_grid", bool(v)),
        )
        self._show_legend.stateChanged.connect(
            lambda v: self._on_config_change("show_legend", bool(v)),
        )

    def _on_config_change(self, key: str, value: Any):
        """Handler para mudança de configuração"""
        self._config[key] = value
        self.config_changed.emit(key, value)

    def _load_settings(self):
        """Carrega configurações salvas"""
        # Visualização
        self._theme_combo.setCurrentText(
            self._settings.value("viz/theme", "Claro"),
        )
        self._line_width.setValue(
            float(self._settings.value("viz/line_width", 2.0)),
        )
        self._marker_size.setValue(
            int(self._settings.value("viz/marker_size", 3)),
        )
        self._show_grid.setChecked(
            self._settings.value("viz/show_grid", True, type=bool),
        )
        self._show_legend.setChecked(
            self._settings.value("viz/show_legend", True, type=bool),
        )

        # Performance
        self._direct_limit.setValue(
            int(self._settings.value("perf/direct_limit", 10000)),
        )
        self._target_points.setValue(
            int(self._settings.value("perf/target_points", 5000)),
        )
        self._cache_enabled.setChecked(
            self._settings.value("perf/cache_enabled", True, type=bool),
        )

        # Geral
        self._default_encoding.setCurrentText(
            self._settings.value("general/encoding", "auto"),
        )
        self._undo_limit.setValue(
            int(self._settings.value("general/undo_limit", 100)),
        )

        logger.info("settings_loaded")

    def _apply_settings(self):
        """Salva configurações"""
        # Visualização
        self._settings.setValue("viz/theme", self._theme_combo.currentText())
        self._settings.setValue("viz/line_width", self._line_width.value())
        self._settings.setValue("viz/marker_size", self._marker_size.value())
        self._settings.setValue("viz/show_grid", self._show_grid.isChecked())
        self._settings.setValue("viz/show_legend", self._show_legend.isChecked())
        self._settings.setValue("viz/antialiasing", self._antialiasing.isChecked())
        self._settings.setValue("viz/font_size", self._font_size.value())

        # Performance
        self._settings.setValue("perf/direct_limit", self._direct_limit.value())
        self._settings.setValue("perf/target_points", self._target_points.value())
        self._settings.setValue("perf/decimation_method", self._decimation_method.currentIndex())
        self._settings.setValue("perf/cache_enabled", self._cache_enabled.isChecked())
        self._settings.setValue("perf/cache_size", self._cache_size.value())
        self._settings.setValue("perf/chunk_size", self._chunk_size.value())
        self._settings.setValue("perf/preload_chunks", self._preload_chunks.value())

        # Geral
        self._settings.setValue("general/encoding", self._default_encoding.currentText())
        self._settings.setValue("general/auto_backup", self._auto_backup.isChecked())
        self._settings.setValue("general/recent_files_limit", self._recent_files_limit.value())
        self._settings.setValue("general/undo_limit", self._undo_limit.value())
        self._settings.setValue("general/save_session", self._save_session.isChecked())
        self._settings.setValue("general/show_notifications", self._show_notifications.isChecked())

        self._settings.sync()

        # Emite signals
        self.theme_changed.emit(self._theme_combo.currentText())
        self.performance_changed.emit()

        logger.info("settings_saved")

    def _reset_defaults(self):
        """Restaura configurações padrão"""
        # Visualização
        self._theme_combo.setCurrentText("Claro")
        self._line_width.setValue(2.0)
        self._marker_size.setValue(3)
        self._show_grid.setChecked(True)
        self._show_legend.setChecked(True)
        self._antialiasing.setChecked(True)
        self._font_size.setValue(12)
        self._toolbar_icons.setCurrentText("Médio")

        # Performance
        self._direct_limit.setValue(10000)
        self._target_points.setValue(5000)
        self._decimation_method.setCurrentIndex(0)
        self._cache_enabled.setChecked(True)
        self._cache_size.setValue(100)
        self._chunk_size.setValue(100000)
        self._preload_chunks.setValue(2)

        # Geral
        self._default_encoding.setCurrentText("auto")
        self._auto_backup.setChecked(True)
        self._recent_files_limit.setValue(10)
        self._undo_limit.setValue(100)
        self._save_session.setChecked(True)
        self._show_notifications.setChecked(True)
        self._play_sounds.setChecked(False)

        logger.info("settings_reset_to_defaults")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return self._settings.value(key, default)

    def set_config(self, key: str, value: Any):
        """Define valor de configuração"""
        self._settings.setValue(key, value)
        self._settings.sync()


# Exports
__all__ = [
    "ColorButton",
    "ConfigPanel",
]
