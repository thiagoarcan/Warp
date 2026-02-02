"""
Theme System - Sistema de temas para a aplicação

Features:
- Tema claro e escuro
- Persistência de preferências
- Seguir tema do sistema operacional
- Aplicação em tempo real sem reiniciar
- Cores customizáveis

Category 3.1 - Temas
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum, auto

from PyQt6.QtCore import QObject, QSettings, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class ThemeMode(Enum):
    """Modos de tema disponíveis"""
    LIGHT = auto()
    DARK = auto()
    SYSTEM = auto()  # Segue o tema do OS


@dataclass
class ThemeColors:
    """Definição de cores para um tema"""
    # Cores principais
    background: str = "#FFFFFF"
    foreground: str = "#212529"
    primary: str = "#0D6EFD"
    secondary: str = "#6C757D"

    # Cores de estado
    success: str = "#198754"
    warning: str = "#FFC107"
    error: str = "#DC3545"
    info: str = "#0DCAF0"

    # Cores de superfície
    surface: str = "#F8F9FA"
    surface_variant: str = "#E9ECEF"
    border: str = "#DEE2E6"

    # Cores de texto
    text_primary: str = "#212529"
    text_secondary: str = "#6C757D"
    text_disabled: str = "#ADB5BD"

    # Cores de gráfico
    plot_background: str = "#FFFFFF"
    plot_foreground: str = "#212529"
    plot_grid: str = "#E9ECEF"

    # Palette de séries (para gráficos)
    series_colors: list[str] = field(default_factory=lambda: [
        "#0D6EFD",  # Azul
        "#DC3545",  # Vermelho
        "#198754",  # Verde
        "#FFC107",  # Amarelo
        "#6F42C1",  # Roxo
        "#FD7E14",  # Laranja
        "#20C997",  # Teal
        "#E83E8C",  # Rosa
        "#6610F2",  # Indigo
        "#17A2B8",  # Cyan
    ])


# Tema Claro
LIGHT_THEME = ThemeColors()

# Tema Escuro
DARK_THEME = ThemeColors(
    background="#1E1E1E",
    foreground="#E0E0E0",
    primary="#58A6FF",
    secondary="#8B949E",

    success="#3FB950",
    warning="#D29922",
    error="#F85149",
    info="#58A6FF",

    surface="#252526",
    surface_variant="#2D2D2D",
    border="#404040",

    text_primary="#E0E0E0",
    text_secondary="#8B949E",
    text_disabled="#6E7681",

    plot_background="#1E1E1E",
    plot_foreground="#E0E0E0",
    plot_grid="#404040",

    series_colors=[
        "#58A6FF",  # Azul claro
        "#F85149",  # Vermelho
        "#3FB950",  # Verde
        "#D29922",  # Amarelo
        "#A371F7",  # Roxo
        "#FFA657",  # Laranja
        "#56D4DD",  # Teal
        "#FF7B72",  # Rosa
        "#8B5CF6",  # Indigo
        "#79C0FF",  # Cyan
    ],
)


def get_system_theme() -> ThemeMode:
    """
    Detecta o tema atual do sistema operacional.
    
    Returns:
        ThemeMode.LIGHT ou ThemeMode.DARK
    """
    try:
        # Windows
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return ThemeMode.LIGHT if value else ThemeMode.DARK
    except Exception:
        pass

    try:
        # macOS
        import subprocess
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
        )
        if "Dark" in result.stdout:
            return ThemeMode.DARK
    except Exception:
        pass

    # Default to light
    return ThemeMode.LIGHT


# Singleton global
_theme_manager_instance: ThemeManager | None = None


class ThemeManager(QObject):
    """
    Gerenciador centralizado de temas.
    
    Use get_theme_manager() para obter a instância singleton.
    
    Signals:
        theme_changed: Emitido quando o tema muda
        colors_changed: Emitido quando as cores mudam
    """

    theme_changed = pyqtSignal(ThemeMode)
    colors_changed = pyqtSignal(ThemeColors)

    _instance: ThemeManager | None = None
    _initialized: bool = False

    def __init__(self):
        super().__init__()

        # Estado atual
        self._current_mode = ThemeMode.LIGHT
        self._current_colors = LIGHT_THEME
        self._custom_colors: dict[str, str] = {}

        # Settings para persistência
        self._settings = QSettings("PlatformBase", "Theme")

        # Carrega configurações salvas
        self._load_settings()

        logger.debug("theme_manager_initialized")

    @property
    def current_mode(self) -> ThemeMode:
        """Retorna modo de tema atual."""
        return self._current_mode

    @property
    def colors(self) -> ThemeColors:
        """Retorna cores do tema atual."""
        return self._current_colors

    @property
    def is_dark(self) -> bool:
        """Verifica se o tema atual é escuro."""
        if self._current_mode == ThemeMode.SYSTEM:
            return get_system_theme() == ThemeMode.DARK
        return self._current_mode == ThemeMode.DARK

    def set_theme(self, mode: ThemeMode):
        """
        Define o tema da aplicação.
        
        Args:
            mode: Modo de tema a aplicar
        """
        self._current_mode = mode

        # Determina cores baseado no modo
        if mode == ThemeMode.SYSTEM:
            system_mode = get_system_theme()
            self._current_colors = DARK_THEME if system_mode == ThemeMode.DARK else LIGHT_THEME
        elif mode == ThemeMode.DARK:
            self._current_colors = DARK_THEME
        else:
            self._current_colors = LIGHT_THEME

        # Aplica cores customizadas
        self._apply_custom_colors()

        # Aplica o tema
        self._apply_theme()

        # Salva configuração
        self._save_settings()

        # Emite signals
        self.theme_changed.emit(mode)
        self.colors_changed.emit(self._current_colors)

        logger.info("theme_changed", mode=mode.name, is_dark=self.is_dark)

    def set_custom_color(self, key: str, color: str):
        """
        Define uma cor customizada.
        
        Args:
            key: Nome da propriedade de cor (ex: 'primary')
            color: Valor da cor em hex (ex: '#FF0000')
        """
        self._custom_colors[key] = color
        self._apply_custom_colors()
        self._apply_theme()
        self._save_settings()
        self.colors_changed.emit(self._current_colors)

    def reset_custom_colors(self):
        """Remove todas as cores customizadas."""
        self._custom_colors.clear()
        self.set_theme(self._current_mode)  # Reaplica tema base

    def get_color(self, key: str) -> str:
        """
        Retorna cor do tema atual.
        
        Args:
            key: Nome da propriedade de cor
            
        Returns:
            Valor da cor em hex
        """
        return getattr(self._current_colors, key, "#000000")

    def get_qcolor(self, key: str) -> QColor:
        """
        Retorna QColor do tema atual.
        
        Args:
            key: Nome da propriedade de cor
            
        Returns:
            QColor object
        """
        return QColor(self.get_color(key))

    def _apply_custom_colors(self):
        """Aplica cores customizadas ao tema atual."""
        for key, color in self._custom_colors.items():
            if hasattr(self._current_colors, key):
                setattr(self._current_colors, key, color)

    def _apply_theme(self):
        """Aplica o tema à aplicação."""
        app = QApplication.instance()
        if not app:
            return

        # Cria paleta
        palette = self._create_palette()
        app.setPalette(palette)

        # Aplica stylesheet global
        stylesheet = self._create_stylesheet()
        app.setStyleSheet(stylesheet)

        logger.debug("theme_applied")

    def _create_palette(self) -> QPalette:
        """Cria QPalette baseada no tema atual."""
        colors = self._current_colors
        palette = QPalette()

        # Window
        palette.setColor(QPalette.ColorRole.Window, QColor(colors.background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.foreground))

        # Base (input fields, lists)
        palette.setColor(QPalette.ColorRole.Base, QColor(colors.surface))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.surface_variant))

        # Text
        palette.setColor(QPalette.ColorRole.Text, QColor(colors.text_primary))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(colors.text_disabled))

        # Button
        palette.setColor(QPalette.ColorRole.Button, QColor(colors.surface))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.text_primary))

        # Highlight (selection)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.primary))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

        # Disabled states
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(colors.text_disabled))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(colors.text_disabled))

        # Links
        palette.setColor(QPalette.ColorRole.Link, QColor(colors.primary))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors.secondary))

        return palette

    def _create_stylesheet(self) -> str:
        """Cria stylesheet CSS baseada no tema atual."""
        colors = self._current_colors

        return f"""
            /* Global */
            QWidget {{
                background-color: {colors.background};
                color: {colors.foreground};
                font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 4px;
                padding: 6px 16px;
                min-height: 24px;
            }}
            
            QPushButton:hover {{
                background-color: {colors.surface_variant};
                border-color: {colors.primary};
            }}
            
            QPushButton:pressed {{
                background-color: {colors.border};
            }}
            
            QPushButton:disabled {{
                color: {colors.text_disabled};
                background-color: {colors.surface};
            }}
            
            /* Primary Button */
            QPushButton[primary="true"] {{
                background-color: {colors.primary};
                color: white;
                border: none;
            }}
            
            QPushButton[primary="true"]:hover {{
                background-color: {self._darken_color(colors.primary, 10)};
            }}
            
            /* Input fields */
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {colors.primary};
            }}
            
            /* ComboBox */
            QComboBox {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }}
            
            QComboBox:hover {{
                border-color: {colors.primary};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            /* Lists and Trees */
            QListView, QTreeView, QTableView {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 4px;
            }}
            
            QListView::item:selected, QTreeView::item:selected, QTableView::item:selected {{
                background-color: {colors.primary};
                color: white;
            }}
            
            QListView::item:hover, QTreeView::item:hover, QTableView::item:hover {{
                background-color: {colors.surface_variant};
            }}
            
            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {colors.border};
                border-radius: 4px;
            }}
            
            QTabBar::tab {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors.background};
                border-bottom: 2px solid {colors.primary};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {colors.surface_variant};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                background-color: {colors.surface};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors.border};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors.secondary};
            }}
            
            QScrollBar:horizontal {{
                background-color: {colors.surface};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {colors.border};
                border-radius: 6px;
                min-width: 30px;
            }}
            
            /* Menu */
            QMenuBar {{
                background-color: {colors.background};
                border-bottom: 1px solid {colors.border};
            }}
            
            QMenuBar::item:selected {{
                background-color: {colors.surface_variant};
            }}
            
            QMenu {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 4px;
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 6px 24px;
                border-radius: 2px;
            }}
            
            QMenu::item:selected {{
                background-color: {colors.primary};
                color: white;
            }}
            
            /* Toolbar */
            QToolBar {{
                background-color: {colors.background};
                border-bottom: 1px solid {colors.border};
                spacing: 4px;
                padding: 4px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }}
            
            QToolButton:hover {{
                background-color: {colors.surface_variant};
            }}
            
            QToolButton:pressed {{
                background-color: {colors.border};
            }}
            
            /* StatusBar */
            QStatusBar {{
                background-color: {colors.surface};
                border-top: 1px solid {colors.border};
            }}
            
            /* DockWidget */
            QDockWidget {{
                titlebar-close-icon: url(none);
                titlebar-normal-icon: url(none);
            }}
            
            QDockWidget::title {{
                background-color: {colors.surface};
                padding: 8px;
                border-bottom: 1px solid {colors.border};
            }}
            
            /* GroupBox */
            QGroupBox {{
                border: 1px solid {colors.border};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {colors.text_secondary};
            }}
            
            /* Slider */
            QSlider::groove:horizontal {{
                height: 6px;
                background-color: {colors.border};
                border-radius: 3px;
            }}
            
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background-color: {colors.primary};
                border-radius: 8px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background-color: {self._darken_color(colors.primary, 10)};
            }}
            
            /* ProgressBar */
            QProgressBar {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 4px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {colors.primary};
                border-radius: 3px;
            }}
            
            /* Checkbox */
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {colors.border};
                border-radius: 3px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors.primary};
                border-color: {colors.primary};
            }}
            
            /* RadioButton */
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {colors.border};
                border-radius: 9px;
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {colors.primary};
                border-color: {colors.primary};
            }}
            
            /* Tooltips */
            QToolTip {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """

    def _darken_color(self, hex_color: str, percent: int) -> str:
        """Escurece uma cor hex por uma porcentagem."""
        color = QColor(hex_color)
        h, s, l, a = color.getHslF()
        l = max(0, l - percent / 100)
        color.setHslF(h, s, l, a)
        return color.name()

    def _lighten_color(self, hex_color: str, percent: int) -> str:
        """Clareia uma cor hex por uma porcentagem."""
        color = QColor(hex_color)
        h, s, l, a = color.getHslF()
        l = min(1, l + percent / 100)
        color.setHslF(h, s, l, a)
        return color.name()

    def _load_settings(self):
        """Carrega configurações salvas."""
        mode_str = self._settings.value("mode", "LIGHT")
        try:
            self._current_mode = ThemeMode[mode_str]
        except KeyError:
            self._current_mode = ThemeMode.LIGHT

        # Carrega cores customizadas
        custom_json = self._settings.value("custom_colors", "{}")
        try:
            self._custom_colors = json.loads(custom_json)
        except json.JSONDecodeError:
            self._custom_colors = {}

        # Aplica tema carregado
        self.set_theme(self._current_mode)

    def _save_settings(self):
        """Salva configurações."""
        self._settings.setValue("mode", self._current_mode.name)
        self._settings.setValue("custom_colors", json.dumps(self._custom_colors))
        self._settings.sync()


def get_theme_manager() -> ThemeManager:
    """Retorna instância singleton do ThemeManager."""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance


def reset_theme_manager():
    """Reseta a instância do ThemeManager (para testes)."""
    global _theme_manager_instance
    _theme_manager_instance = None


def apply_theme(mode: ThemeMode):
    """Aplica um tema à aplicação."""
    get_theme_manager().set_theme(mode)


def get_current_colors() -> ThemeColors:
    """Retorna cores do tema atual."""
    return get_theme_manager().colors


__all__ = [
    "DARK_THEME",
    "LIGHT_THEME",
    "ThemeColors",
    "ThemeManager",
    "ThemeMode",
    "apply_theme",
    "get_current_colors",
    "get_system_theme",
    "get_theme_manager",
]
