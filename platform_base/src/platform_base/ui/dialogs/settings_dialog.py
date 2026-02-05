"""
Settings Dialog - Configurações da aplicação

Dialog completo para gerenciar preferências do usuário:
- Aparência (tema, cores, fontes)
- Visualização (crosshair, grid, legenda padrão)
- Performance (downsampling, buffer size)
- Caminhos (diretório padrão)
- Comportamento (streaming, saída)

Interface carregada de: desktop/ui_files/settingsDialog.ui
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PyQt6.QtCore import QSettings, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFontComboBox,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class AppSettings:
    """Estrutura de configurações da aplicação"""

    # Aparência
    theme: str = "light"  # light, dark, system
    font_family: str = "Segoe UI"
    font_size: int = 10
    accent_color: str = "#0d6efd"

    # Visualização
    default_grid: bool = True
    default_legend: bool = True
    default_crosshair: bool = False
    auto_zoom_fit: bool = True
    plot_line_width: float = 2.0
    marker_size: int = 3

    # Performance
    lttb_threshold: int = 10000  # Pontos para ativar downsampling
    max_render_points: int = 100000
    buffer_size_mb: int = 512
    opengl_enabled: bool = False

    # Caminhos
    default_data_dir: str = ""
    default_export_dir: str = ""
    recent_files_max: int = 10

    # Comportamento
    confirm_on_exit: bool = True
    auto_save_layout: bool = True
    remember_window_size: bool = True
    check_updates: bool = False

    # Streaming
    default_fps: int = 30
    default_window_size: int = 1000

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário"""
        return {
            "theme": self.theme,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "accent_color": self.accent_color,
            "default_grid": self.default_grid,
            "default_legend": self.default_legend,
            "default_crosshair": self.default_crosshair,
            "auto_zoom_fit": self.auto_zoom_fit,
            "plot_line_width": self.plot_line_width,
            "marker_size": self.marker_size,
            "lttb_threshold": self.lttb_threshold,
            "max_render_points": self.max_render_points,
            "buffer_size_mb": self.buffer_size_mb,
            "opengl_enabled": self.opengl_enabled,
            "default_data_dir": self.default_data_dir,
            "default_export_dir": self.default_export_dir,
            "recent_files_max": self.recent_files_max,
            "confirm_on_exit": self.confirm_on_exit,
            "auto_save_layout": self.auto_save_layout,
            "remember_window_size": self.remember_window_size,
            "check_updates": self.check_updates,
            "default_fps": self.default_fps,
            "default_window_size": self.default_window_size,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppSettings:
        """Cria a partir de dicionário"""
        settings = cls()
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        return settings


class SettingsDialog(QDialog, UiLoaderMixin):
    """
    Diálogo de configurações da aplicação

    Recursos:
    - Abas organizadas por categoria
    - Persistência via QSettings
    - Preview de alterações
    - Reset para padrões
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """
    
    # Arquivo .ui que define a interface
    UI_FILE = "settingsDialog.ui"

    # Signals
    settings_changed = pyqtSignal(object)  # AppSettings
    theme_changed = pyqtSignal(str)

    SETTINGS_ORG = "TRANSPETRO"
    SETTINGS_APP = "PlatformBase"

    def __init__(self, parent: QWidget | None = None, current_settings: AppSettings | None = None):
        super().__init__(parent)

        # Carregar interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        
        # Carregar configurações atuais ou padrões
        self._original_settings = current_settings or self._load_settings()
        self._current_settings = AppSettings(**self._original_settings.to_dict())

        self._setup_ui_from_file()
        self._load_values()
        self._setup_connections()
        self._apply_dialog_style()

        logger.debug("settings_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Tab Widget
        self._tabs = self.findChild(QWidget, "settingsTabs")
        
        # === Aba Aparência ===
        self._theme_combo = self.findChild(QComboBox, "themeCombo")
        self._accent_btn = self.findChild(QPushButton, "accentColorBtn")
        self._font_combo = self.findChild(QFontComboBox, "fontCombo")
        self._font_size_spin = self.findChild(QSpinBox, "fontSizeSpin")
        
        # === Aba Visualização ===
        self._grid_check = self.findChild(QCheckBox, "gridCheck")
        self._legend_check = self.findChild(QCheckBox, "legendCheck")
        self._crosshair_check = self.findChild(QCheckBox, "crosshairCheck")
        self._autozoom_check = self.findChild(QCheckBox, "autozoomCheck")
        self._line_width_spin = self.findChild(QDoubleSpinBox, "lineWidthSpin")
        self._marker_size_spin = self.findChild(QSpinBox, "markerSizeSpin")
        
        # === Aba Performance ===
        self._lttb_spin = self.findChild(QSpinBox, "lttbSpin")
        self._max_points_spin = self.findChild(QSpinBox, "maxPointsSpin")
        self._buffer_spin = self.findChild(QSpinBox, "bufferSpin")
        self._opengl_check = self.findChild(QCheckBox, "openglCheck")
        
        # === Aba Caminhos ===
        self._data_dir_edit = self.findChild(QLineEdit, "dataDirEdit")
        self._data_dir_btn = self.findChild(QPushButton, "dataDirBtn")
        self._export_dir_edit = self.findChild(QLineEdit, "exportDirEdit")
        self._export_dir_btn = self.findChild(QPushButton, "exportDirBtn")
        self._recent_max_spin = self.findChild(QSpinBox, "recentMaxSpin")
        self._clear_recent_btn = self.findChild(QPushButton, "clearRecentBtn")
        
        # === Aba Comportamento ===
        self._confirm_exit_check = self.findChild(QCheckBox, "confirmExitCheck")
        self._auto_save_layout_check = self.findChild(QCheckBox, "autoSaveLayoutCheck")
        self._remember_size_check = self.findChild(QCheckBox, "rememberSizeCheck")
        self._check_updates_check = self.findChild(QCheckBox, "checkUpdatesCheck")
        self._fps_spin = self.findChild(QSpinBox, "fpsSpin")
        self._window_size_spin = self.findChild(QSpinBox, "windowSizeSpin")
        
        # === Botões ===
        self._reset_btn = self.findChild(QPushButton, "resetBtn")
        self._cancel_btn = self.findChild(QPushButton, "cancelBtn")
        self._apply_btn = self.findChild(QPushButton, "applyBtn")
        self._ok_btn = self.findChild(QPushButton, "okBtn")
        
        logger.debug("settings_dialog_ui_loaded_from_file")

    def _setup_connections(self):
        """Configura conexões de signals"""
        # Botão de cor de destaque
        if self._accent_btn:
            self._accent_btn.clicked.connect(self._choose_accent_color)
        
        # Notificar mudança de tema
        if self._theme_combo:
            self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        
        # Botões de diretório
        if self._data_dir_btn:
            self._data_dir_btn.clicked.connect(lambda: self._choose_directory(self._data_dir_edit))
        if self._export_dir_btn:
            self._export_dir_btn.clicked.connect(lambda: self._choose_directory(self._export_dir_edit))
        
        # Limpar recentes
        if self._clear_recent_btn:
            self._clear_recent_btn.clicked.connect(self._clear_recent_files)
        
        # Botões de ação
        if self._reset_btn:
            self._reset_btn.clicked.connect(self._reset_to_defaults)
        if self._apply_btn:
            self._apply_btn.clicked.connect(self._apply_settings)
        if self._ok_btn:
            self._ok_btn.clicked.connect(self._accept_and_save)

    def _load_values(self):
        """Carrega valores nas widgets"""
        s = self._current_settings

        # Aparência
        if self._theme_combo:
            theme_map = {"light": 0, "dark": 1, "system": 2}
            self._theme_combo.setCurrentIndex(theme_map.get(s.theme, 0))
        self._update_accent_button(s.accent_color)
        if self._font_combo:
            self._font_combo.setCurrentFont(QFont(s.font_family))
        if self._font_size_spin:
            self._font_size_spin.setValue(s.font_size)

        # Visualização
        if self._grid_check:
            self._grid_check.setChecked(s.default_grid)
        if self._legend_check:
            self._legend_check.setChecked(s.default_legend)
        if self._crosshair_check:
            self._crosshair_check.setChecked(s.default_crosshair)
        if self._autozoom_check:
            self._autozoom_check.setChecked(s.auto_zoom_fit)
        if self._line_width_spin:
            self._line_width_spin.setValue(s.plot_line_width)
        if self._marker_size_spin:
            self._marker_size_spin.setValue(s.marker_size)

        # Performance
        if self._lttb_spin:
            self._lttb_spin.setValue(s.lttb_threshold)
        if self._max_points_spin:
            self._max_points_spin.setValue(s.max_render_points)
        if self._buffer_spin:
            self._buffer_spin.setValue(s.buffer_size_mb)
        if self._opengl_check:
            self._opengl_check.setChecked(s.opengl_enabled)

        # Caminhos
        if self._data_dir_edit:
            self._data_dir_edit.setText(s.default_data_dir)
        if self._export_dir_edit:
            self._export_dir_edit.setText(s.default_export_dir)
        if self._recent_max_spin:
            self._recent_max_spin.setValue(s.recent_files_max)

        # Comportamento
        if self._confirm_exit_check:
            self._confirm_exit_check.setChecked(s.confirm_on_exit)
        if self._auto_save_layout_check:
            self._auto_save_layout_check.setChecked(s.auto_save_layout)
        if self._remember_size_check:
            self._remember_size_check.setChecked(s.remember_window_size)
        if self._check_updates_check:
            self._check_updates_check.setChecked(s.check_updates)
        if self._fps_spin:
            self._fps_spin.setValue(s.default_fps)
        if self._window_size_spin:
            self._window_size_spin.setValue(s.default_window_size)

    def _collect_values(self) -> AppSettings:
        """Coleta valores das widgets"""
        theme_map = {0: "light", 1: "dark", 2: "system"}

        return AppSettings(
            # Aparência
            theme=theme_map.get(self._theme_combo.currentIndex() if self._theme_combo else 0, "light"),
            font_family=self._font_combo.currentFont().family() if self._font_combo else "Segoe UI",
            font_size=self._font_size_spin.value() if self._font_size_spin else 10,
            accent_color=self._current_settings.accent_color,

            # Visualização
            default_grid=self._grid_check.isChecked() if self._grid_check else True,
            default_legend=self._legend_check.isChecked() if self._legend_check else True,
            default_crosshair=self._crosshair_check.isChecked() if self._crosshair_check else False,
            auto_zoom_fit=self._autozoom_check.isChecked() if self._autozoom_check else True,
            plot_line_width=self._line_width_spin.value() if self._line_width_spin else 2.0,
            marker_size=self._marker_size_spin.value() if self._marker_size_spin else 3,

            # Performance
            lttb_threshold=self._lttb_spin.value() if self._lttb_spin else 10000,
            max_render_points=self._max_points_spin.value() if self._max_points_spin else 100000,
            buffer_size_mb=self._buffer_spin.value() if self._buffer_spin else 512,
            opengl_enabled=self._opengl_check.isChecked() if self._opengl_check else False,

            # Caminhos
            default_data_dir=self._data_dir_edit.text() if self._data_dir_edit else "",
            default_export_dir=self._export_dir_edit.text() if self._export_dir_edit else "",
            recent_files_max=self._recent_max_spin.value() if self._recent_max_spin else 10,

            # Comportamento
            confirm_on_exit=self._confirm_exit_check.isChecked() if self._confirm_exit_check else True,
            auto_save_layout=self._auto_save_layout_check.isChecked() if self._auto_save_layout_check else True,
            remember_window_size=self._remember_size_check.isChecked() if self._remember_size_check else True,
            check_updates=self._check_updates_check.isChecked() if self._check_updates_check else False,
            default_fps=self._fps_spin.value() if self._fps_spin else 30,
            default_window_size=self._window_size_spin.value() if self._window_size_spin else 1000,
        )

    def _choose_accent_color(self):
        """Abre diálogo de seleção de cor"""
        current = QColor(self._current_settings.accent_color)
        color = QColorDialog.getColor(current, self, "Escolher Cor de Destaque")

        if color.isValid():
            self._current_settings.accent_color = color.name()
            self._update_accent_button(color.name())

    def _update_accent_button(self, color: str):
        """Atualiza visual do botão de cor"""
        if self._accent_btn:
            self._accent_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    border-color: #0d6efd;
                }}
            """)

    def _choose_directory(self, line_edit: QLineEdit):
        """Abre diálogo de seleção de diretório"""
        if not line_edit:
            return
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Diretório",
            line_edit.text() or "",
        )
        if directory:
            line_edit.setText(directory)

    def _clear_recent_files(self):
        """Limpa lista de arquivos recentes"""
        reply = QMessageBox.question(
            self,
            "Limpar Recentes",
            "Deseja limpar a lista de arquivos recentes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
            settings.remove("recent_files")
            QMessageBox.information(self, "Sucesso", "Lista de recentes limpa!")

    def _reset_to_defaults(self):
        """Restaura configurações padrão"""
        reply = QMessageBox.question(
            self,
            "Restaurar Padrões",
            "Deseja restaurar todas as configurações para os valores padrão?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._current_settings = AppSettings()
            self._load_values()

    def _on_theme_changed(self, index: int):
        """Handler para mudança de tema"""
        theme_map = {0: "light", 1: "dark", 2: "system"}
        theme = theme_map.get(index, "light")
        self.theme_changed.emit(theme)

    def _apply_settings(self):
        """Aplica configurações sem fechar"""
        self._current_settings = self._collect_values()
        self._save_settings(self._current_settings)
        self.settings_changed.emit(self._current_settings)
        logger.info("Settings applied")

    def _accept_and_save(self):
        """Aceita e salva configurações"""
        self._apply_settings()
        self.accept()

    def _save_settings(self, settings: AppSettings):
        """Salva configurações via QSettings"""
        qsettings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)

        for key, value in settings.to_dict().items():
            qsettings.setValue(f"settings/{key}", value)

        qsettings.sync()

    def _load_settings(self) -> AppSettings:
        """Carrega configurações via QSettings"""
        qsettings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        default_settings = AppSettings()
        data = {}

        for key in default_settings.to_dict():
            value = qsettings.value(f"settings/{key}")
            if value is not None:
                # Converter tipos
                default_value = getattr(default_settings, key)
                if isinstance(default_value, bool):
                    data[key] = value == "true" if isinstance(value, str) else bool(value)
                elif isinstance(default_value, int):
                    data[key] = int(value)
                elif isinstance(default_value, float):
                    data[key] = float(value)
                else:
                    data[key] = value

        return AppSettings.from_dict(data)

    def _apply_dialog_style(self):
        """Aplica estilos ao diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #0d6efd;
            }
            QCheckBox {
                spacing: 8px;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
                padding: 6px 10px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: #ffffff;
                min-height: 24px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border-color: #0d6efd;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: #ffffff;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #0d6efd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:default {
                background-color: #0d6efd;
                color: white;
                border-color: #0d6efd;
            }
            QPushButton:default:hover {
                background-color: #0b5ed7;
            }
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 12px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 20px;
                margin-right: 4px;
                border-radius: 6px 6px 0 0;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
                color: #0d6efd;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)

    def get_settings(self) -> AppSettings:
        """Retorna as configurações atuais"""
        return self._collect_values()


def show_settings_dialog(parent: QWidget | None = None, current_settings: AppSettings | None = None) -> AppSettings | None:
    """
    Função de conveniência para mostrar o diálogo de configurações

    Args:
        parent: Widget pai
        current_settings: Configurações atuais (opcional)

    Returns:
        AppSettings se aceito, None se cancelado
    """
    dialog = SettingsDialog(parent, current_settings)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_settings()

    return None


def load_app_settings() -> AppSettings:
    """
    Carrega configurações da aplicação do QSettings

    Returns:
        AppSettings com as configurações salvas ou padrões
    """
    qsettings = QSettings(SettingsDialog.SETTINGS_ORG, SettingsDialog.SETTINGS_APP)
    default_settings = AppSettings()
    data = {}

    for key in default_settings.to_dict():
        value = qsettings.value(f"settings/{key}")
        if value is not None:
            default_value = getattr(default_settings, key)
            if isinstance(default_value, bool):
                data[key] = value == "true" if isinstance(value, str) else bool(value)
            elif isinstance(default_value, int):
                data[key] = int(value)
            elif isinstance(default_value, float):
                data[key] = float(value)
            else:
                data[key] = value

    return AppSettings.from_dict(data)
