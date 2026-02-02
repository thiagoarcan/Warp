"""
Accessibility (a11y) module for Platform Base.

Implements keyboard navigation, screen reader support, high contrast mode,
and other accessibility features following WCAG 2.1 AA guidelines.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QKeySequence, QPalette, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QDockWidget,
    QMainWindow,
    QToolBar,
    QWidget,
)


# QAccessible is in QtGui on some versions, QtWidgets on others
# Try to import from both locations
try:
    from PyQt6.QtGui import QAccessible, QAccessibleEvent
    HAS_QACCESSIBLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import QAccessible, QAccessibleEvent
        HAS_QACCESSIBLE = True
    except ImportError:
        # Create stub classes if QAccessible is not available
        HAS_QACCESSIBLE = False

        class QAccessible:
            """Stub class when QAccessible is not available."""
            class Event:
                NameChanged = 0
                ValueChanged = 1
                DescriptionChanged = 2
                StateChanged = 3

            @staticmethod
            def updateAccessibility(event):
                pass

        class QAccessibleEvent:
            """Stub class when QAccessibleEvent is not available."""
            def __init__(self, widget, event_type):
                self.widget = widget
                self.event_type = event_type


logger = logging.getLogger(__name__)


class ContrastMode(Enum):
    """Available contrast modes."""
    NORMAL = auto()
    HIGH_CONTRAST = auto()
    HIGH_CONTRAST_DARK = auto()


@dataclass
class AccessibilityConfig:
    """Configuration for accessibility features."""

    # Keyboard navigation
    enable_keyboard_navigation: bool = True
    tab_order_logical: bool = True
    show_focus_indicators: bool = True
    focus_indicator_width: int = 2
    focus_indicator_color: str = "#0078D4"  # Blue

    # Screen reader support
    enable_screen_reader: bool = True
    announce_on_focus: bool = True
    verbose_descriptions: bool = False

    # Visual accessibility
    contrast_mode: ContrastMode = ContrastMode.NORMAL
    minimum_contrast_ratio: float = 4.5  # WCAG AA

    # Zoom
    enable_ui_zoom: bool = True
    zoom_level: float = 1.0  # 100%
    min_zoom: float = 1.0
    max_zoom: float = 2.0

    # Audio feedback
    enable_audio_feedback: bool = False

    # Skip links
    enable_skip_links: bool = True


@dataclass
class ShortcutDefinition:
    """Definition of a keyboard shortcut."""
    key_sequence: str
    action_name: str
    description: str
    category: str = "General"
    enabled: bool = True
    context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut


class AccessibleWidget(QObject):
    """
    Wrapper to add accessibility features to any widget.
    
    Provides accessible name, description, role, and state information
    for screen readers.
    """

    def __init__(
        self,
        widget: QWidget,
        accessible_name: str,
        accessible_description: str = "",
        role: str | None = None,
    ):
        super().__init__(widget)
        self.widget = widget
        self._accessible_name = accessible_name
        self._accessible_description = accessible_description
        self._role = role

        # Set accessible properties
        widget.setAccessibleName(accessible_name)
        if accessible_description:
            widget.setAccessibleDescription(accessible_description)

        # Ensure widget can receive focus
        if not widget.focusPolicy():
            widget.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def update_description(self, description: str) -> None:
        """Update the accessible description."""
        self._accessible_description = description
        self.widget.setAccessibleDescription(description)

    def announce(self, message: str, priority: int = 0) -> None:
        """
        Announce a message to screen readers.
        
        Args:
            message: Message to announce
            priority: 0=polite, 1=assertive
        """
        # Create accessible event
        event = QAccessibleEvent(
            self.widget,
            QAccessible.Event.Alert if priority else QAccessible.Event.NameChanged,
        )
        QAccessible.updateAccessibility(event)
        logger.debug(f"Accessibility announcement: {message}")


class KeyboardNavigationManager(QObject):
    """
    Manages keyboard navigation throughout the application.
    
    Implements logical tab order, skip links, and focus management.
    """

    # Signals
    focus_changed = pyqtSignal(QWidget)  # Emitted when focus changes
    navigation_region_changed = pyqtSignal(str)  # Emitted when region changes

    def __init__(self, main_window: QMainWindow, config: AccessibilityConfig):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config

        # Navigation regions in logical order
        self._regions: list[tuple[str, QWidget]] = []
        self._current_region_index: int = 0

        # Focus history for back navigation
        self._focus_history: list[QWidget] = []
        self._max_history: int = 50

        # Skip link shortcuts
        self._skip_shortcuts: list[QShortcut] = []

        # Setup
        self._setup_focus_tracking()
        self._setup_skip_links()

    def register_region(self, name: str, widget: QWidget) -> None:
        """
        Register a navigation region.
        
        Regions are navigated in order using F6/Shift+F6.
        
        Args:
            name: Human-readable region name
            widget: Widget representing the region
        """
        self._regions.append((name, widget))
        logger.debug(f"Registered navigation region: {name}")

    def _setup_focus_tracking(self) -> None:
        """Setup focus change tracking."""
        app = QApplication.instance()
        if app:
            app.focusChanged.connect(self._on_focus_changed)

    def _on_focus_changed(
        self, old_widget: QWidget | None, new_widget: QWidget | None,
    ) -> None:
        """Handle focus change events."""
        if new_widget is None:
            return

        # Add to history
        if old_widget and old_widget != new_widget:
            self._focus_history.append(old_widget)
            if len(self._focus_history) > self._max_history:
                self._focus_history.pop(0)

        # Emit signal
        self.focus_changed.emit(new_widget)

        # Update current region
        self._update_current_region(new_widget)

        # Announce if configured
        if self.config.announce_on_focus:
            self._announce_widget(new_widget)

    def _update_current_region(self, widget: QWidget) -> None:
        """Update current region based on focused widget."""
        for i, (name, region_widget) in enumerate(self._regions):
            if self._is_child_of(widget, region_widget):
                if i != self._current_region_index:
                    self._current_region_index = i
                    self.navigation_region_changed.emit(name)
                break

    def _is_child_of(self, widget: QWidget, parent: QWidget) -> bool:
        """Check if widget is a child of parent."""
        current = widget
        while current:
            if current == parent:
                return True
            current = current.parent()
        return False

    def _announce_widget(self, widget: QWidget) -> None:
        """Announce widget to screen reader."""
        name = widget.accessibleName() or widget.objectName() or widget.__class__.__name__
        logger.debug(f"Focus: {name}")

    def _setup_skip_links(self) -> None:
        """Setup skip link shortcuts."""
        if not self.config.enable_skip_links:
            return

        # F6 - Next region
        shortcut = QShortcut(QKeySequence("F6"), self.main_window)
        shortcut.activated.connect(self._navigate_next_region)
        self._skip_shortcuts.append(shortcut)

        # Shift+F6 - Previous region
        shortcut = QShortcut(QKeySequence("Shift+F6"), self.main_window)
        shortcut.activated.connect(self._navigate_previous_region)
        self._skip_shortcuts.append(shortcut)

        # Alt+1-9 - Jump to specific region
        for i in range(min(9, len(self._regions))):
            shortcut = QShortcut(QKeySequence(f"Alt+{i+1}"), self.main_window)
            shortcut.activated.connect(lambda idx=i: self._navigate_to_region(idx))
            self._skip_shortcuts.append(shortcut)

    def _navigate_next_region(self) -> None:
        """Navigate to next region."""
        if not self._regions:
            return
        self._current_region_index = (self._current_region_index + 1) % len(self._regions)
        self._focus_region(self._current_region_index)

    def _navigate_previous_region(self) -> None:
        """Navigate to previous region."""
        if not self._regions:
            return
        self._current_region_index = (self._current_region_index - 1) % len(self._regions)
        self._focus_region(self._current_region_index)

    def _navigate_to_region(self, index: int) -> None:
        """Navigate to specific region by index."""
        if 0 <= index < len(self._regions):
            self._current_region_index = index
            self._focus_region(index)

    def _focus_region(self, index: int) -> None:
        """Focus the first focusable widget in a region."""
        if not self._regions:
            return

        name, widget = self._regions[index]

        # Find first focusable child
        focusable = self._find_first_focusable(widget)
        if focusable:
            focusable.setFocus()
            self.navigation_region_changed.emit(name)
            logger.debug(f"Navigated to region: {name}")

    def _find_first_focusable(self, widget: QWidget) -> QWidget | None:
        """Find the first focusable widget."""
        if widget.focusPolicy() not in (Qt.FocusPolicy.NoFocus,):
            return widget

        for child in widget.findChildren(QWidget):
            if child.focusPolicy() not in (Qt.FocusPolicy.NoFocus,):
                if child.isVisible() and child.isEnabled():
                    return child

        return None

    def navigate_back(self) -> bool:
        """Navigate to previously focused widget."""
        if self._focus_history:
            widget = self._focus_history.pop()
            if widget.isVisible() and widget.isEnabled():
                widget.setFocus()
                return True
        return False


class ShortcutManager(QObject):
    """
    Manages all keyboard shortcuts in the application.
    
    Provides registration, customization, and conflict detection.
    """

    # Signals
    shortcut_activated = pyqtSignal(str)  # Emitted with action name
    shortcut_conflict = pyqtSignal(str, str)  # key, existing action

    # Default shortcuts
    DEFAULT_SHORTCUTS = [
        # File operations
        ShortcutDefinition("Ctrl+O", "file_open", "Abrir arquivo", "Arquivo"),
        ShortcutDefinition("Ctrl+S", "file_save", "Salvar sessão", "Arquivo"),
        ShortcutDefinition("Ctrl+Shift+S", "file_save_as", "Salvar como", "Arquivo"),
        ShortcutDefinition("Ctrl+E", "file_export", "Exportar dados", "Arquivo"),
        ShortcutDefinition("Ctrl+W", "file_close", "Fechar arquivo", "Arquivo"),
        ShortcutDefinition("Ctrl+Q", "app_quit", "Sair", "Arquivo"),

        # Edit operations
        ShortcutDefinition("Ctrl+Z", "edit_undo", "Desfazer", "Editar"),
        ShortcutDefinition("Ctrl+Y", "edit_redo", "Refazer", "Editar"),
        ShortcutDefinition("Ctrl+Shift+Z", "edit_redo", "Refazer (alt)", "Editar"),
        ShortcutDefinition("Ctrl+A", "edit_select_all", "Selecionar tudo", "Editar"),
        ShortcutDefinition("Ctrl+Shift+A", "edit_deselect_all", "Desselecionar tudo", "Editar"),
        ShortcutDefinition("Ctrl+C", "edit_copy", "Copiar", "Editar"),
        ShortcutDefinition("Ctrl+V", "edit_paste", "Colar", "Editar"),
        ShortcutDefinition("Delete", "edit_delete", "Excluir seleção", "Editar"),
        ShortcutDefinition("Ctrl+D", "edit_duplicate", "Duplicar série", "Editar"),

        # View operations
        ShortcutDefinition("F11", "view_fullscreen", "Tela cheia", "Visualizar"),
        ShortcutDefinition("Ctrl+0", "view_zoom_reset", "Zoom 100%", "Visualizar"),
        ShortcutDefinition("Ctrl++", "view_zoom_in", "Aumentar zoom", "Visualizar"),
        ShortcutDefinition("Ctrl+-", "view_zoom_out", "Diminuir zoom", "Visualizar"),
        ShortcutDefinition("G", "view_toggle_grid", "Alternar grade", "Visualizar"),
        ShortcutDefinition("L", "view_toggle_legend", "Alternar legenda", "Visualizar"),
        ShortcutDefinition("Ctrl+L", "view_toggle_log", "Alternar painel de log", "Visualizar"),

        # Streaming
        ShortcutDefinition("Space", "stream_play_pause", "Play/Pause", "Streaming"),
        ShortcutDefinition("S", "stream_stop", "Parar", "Streaming"),
        ShortcutDefinition("Left", "stream_backward", "Retroceder 1s", "Streaming"),
        ShortcutDefinition("Right", "stream_forward", "Avançar 1s", "Streaming"),
        ShortcutDefinition("Shift+Left", "stream_backward_10", "Retroceder 10s", "Streaming"),
        ShortcutDefinition("Shift+Right", "stream_forward_10", "Avançar 10s", "Streaming"),
        ShortcutDefinition("Home", "stream_start", "Ir para início", "Streaming"),
        ShortcutDefinition("End", "stream_end", "Ir para fim", "Streaming"),

        # Navigation
        ShortcutDefinition("F6", "nav_next_region", "Próxima região", "Navegação"),
        ShortcutDefinition("Shift+F6", "nav_prev_region", "Região anterior", "Navegação"),
        ShortcutDefinition("Escape", "nav_clear_selection", "Limpar seleção", "Navegação"),
        ShortcutDefinition("F5", "nav_refresh", "Atualizar dados", "Navegação"),

        # Help
        ShortcutDefinition("F1", "help_context", "Ajuda contextual", "Ajuda"),
        ShortcutDefinition("Shift+F1", "help_whats_this", "O que é isto?", "Ajuda"),
        ShortcutDefinition("Ctrl+?", "help_shortcuts", "Lista de atalhos", "Ajuda"),
    ]

    def __init__(self, main_window: QMainWindow):
        super().__init__(main_window)
        self.main_window = main_window

        # Registered shortcuts
        self._shortcuts: dict[str, tuple[ShortcutDefinition, QShortcut]] = {}
        self._action_handlers: dict[str, Callable[[], None]] = {}

        # Initialize default shortcuts
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all default shortcuts."""
        for definition in self.DEFAULT_SHORTCUTS:
            self.register_shortcut(definition)

    def register_shortcut(self, definition: ShortcutDefinition) -> bool:
        """
        Register a keyboard shortcut.
        
        Args:
            definition: Shortcut definition
            
        Returns:
            True if registered successfully, False if conflict
        """
        key = definition.key_sequence

        # Check for conflicts
        if key in self._shortcuts:
            existing = self._shortcuts[key][0]
            self.shortcut_conflict.emit(key, existing.action_name)
            logger.warning(
                f"Shortcut conflict: {key} already assigned to {existing.action_name}",
            )
            return False

        # Create shortcut
        shortcut = QShortcut(QKeySequence(key), self.main_window)
        shortcut.setContext(definition.context)
        shortcut.activated.connect(
            lambda name=definition.action_name: self._on_shortcut_activated(name),
        )
        shortcut.setEnabled(definition.enabled)

        self._shortcuts[key] = (definition, shortcut)
        logger.debug(f"Registered shortcut: {key} -> {definition.action_name}")
        return True

    def register_handler(self, action_name: str, handler: Callable[[], None]) -> None:
        """
        Register a handler for an action.
        
        Args:
            action_name: Name of the action
            handler: Callback function
        """
        self._action_handlers[action_name] = handler
        logger.debug(f"Registered handler for: {action_name}")

    def _on_shortcut_activated(self, action_name: str) -> None:
        """Handle shortcut activation."""
        self.shortcut_activated.emit(action_name)

        if action_name in self._action_handlers:
            try:
                self._action_handlers[action_name]()
            except Exception as e:
                logger.error(f"Error executing action {action_name}: {e}")
        else:
            logger.debug(f"No handler for action: {action_name}")

    def get_shortcut(self, action_name: str) -> str | None:
        """Get the key sequence for an action."""
        for key, (definition, _) in self._shortcuts.items():
            if definition.action_name == action_name:
                return key
        return None

    def get_shortcuts_by_category(self) -> dict[str, list[ShortcutDefinition]]:
        """Get all shortcuts organized by category."""
        result: dict[str, list[ShortcutDefinition]] = {}

        for _, (definition, _) in self._shortcuts.items():
            if definition.category not in result:
                result[definition.category] = []
            result[definition.category].append(definition)

        return result

    def update_shortcut(self, action_name: str, new_key: str) -> bool:
        """
        Update the key sequence for an action.
        
        Args:
            action_name: Name of the action
            new_key: New key sequence
            
        Returns:
            True if updated successfully
        """
        # Find existing
        old_key = None
        for key, (definition, shortcut) in self._shortcuts.items():
            if definition.action_name == action_name:
                old_key = key
                break

        if old_key is None:
            return False

        # Check conflict with new key
        if new_key in self._shortcuts and new_key != old_key:
            return False

        # Update
        definition, shortcut = self._shortcuts.pop(old_key)
        shortcut.setKey(QKeySequence(new_key))
        definition = ShortcutDefinition(
            key_sequence=new_key,
            action_name=definition.action_name,
            description=definition.description,
            category=definition.category,
            enabled=definition.enabled,
            context=definition.context,
        )
        self._shortcuts[new_key] = (definition, shortcut)

        logger.info(f"Updated shortcut: {action_name} from {old_key} to {new_key}")
        return True


class HighContrastMode:
    """
    Manages high contrast mode for visual accessibility.
    
    Provides color palettes that meet WCAG 2.1 AA contrast requirements.
    """

    # High contrast light palette
    HIGH_CONTRAST_LIGHT = {
        "window": "#FFFFFF",
        "window_text": "#000000",
        "base": "#FFFFFF",
        "alternate_base": "#F0F0F0",
        "text": "#000000",
        "button": "#E0E0E0",
        "button_text": "#000000",
        "highlight": "#0078D4",
        "highlighted_text": "#FFFFFF",
        "link": "#0000EE",
        "link_visited": "#551A8B",
        "disabled_text": "#6D6D6D",
        "border": "#000000",
    }

    # High contrast dark palette
    HIGH_CONTRAST_DARK = {
        "window": "#000000",
        "window_text": "#FFFFFF",
        "base": "#1E1E1E",
        "alternate_base": "#2D2D2D",
        "text": "#FFFFFF",
        "button": "#3C3C3C",
        "button_text": "#FFFFFF",
        "highlight": "#1AEBFF",
        "highlighted_text": "#000000",
        "link": "#3794FF",
        "link_visited": "#C586C0",
        "disabled_text": "#808080",
        "border": "#FFFFFF",
    }

    @classmethod
    def apply(cls, app: QApplication, mode: ContrastMode) -> None:
        """
        Apply a contrast mode to the application.
        
        Args:
            app: QApplication instance
            mode: Contrast mode to apply
        """
        if mode == ContrastMode.NORMAL:
            app.setPalette(app.style().standardPalette())
            return

        palette_data = (
            cls.HIGH_CONTRAST_DARK if mode == ContrastMode.HIGH_CONTRAST_DARK
            else cls.HIGH_CONTRAST_LIGHT
        )

        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, QColor(palette_data["window"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(palette_data["window_text"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(palette_data["base"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(palette_data["alternate_base"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(palette_data["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(palette_data["button"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(palette_data["button_text"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(palette_data["highlight"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(palette_data["highlighted_text"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(palette_data["link"]))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(palette_data["link_visited"]))

        # Disabled colors
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.Text,
            QColor(palette_data["disabled_text"]),
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.WindowText,
            QColor(palette_data["disabled_text"]),
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
            QColor(palette_data["disabled_text"]),
        )

        app.setPalette(palette)
        logger.info(f"Applied contrast mode: {mode.name}")


class UIZoomManager(QObject):
    """
    Manages UI zoom functionality.
    
    Allows scaling the entire interface from 100% to 200%.
    """

    zoom_changed = pyqtSignal(float)  # Emitted with zoom level

    def __init__(
        self,
        main_window: QMainWindow,
        config: AccessibilityConfig,
    ):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config

        self._base_font_size: int = 9
        self._current_zoom: float = config.zoom_level

    def set_zoom(self, level: float) -> None:
        """
        Set the UI zoom level.
        
        Args:
            level: Zoom level (1.0 = 100%, 2.0 = 200%)
        """
        level = max(self.config.min_zoom, min(self.config.max_zoom, level))

        if level == self._current_zoom:
            return

        self._current_zoom = level

        # Scale font
        app = QApplication.instance()
        if app:
            font = app.font()
            font.setPointSize(int(self._base_font_size * level))
            app.setFont(font)

        self.zoom_changed.emit(level)
        logger.info(f"UI zoom set to: {level * 100:.0f}%")

    def zoom_in(self) -> None:
        """Increase zoom by 10%."""
        self.set_zoom(self._current_zoom + 0.1)

    def zoom_out(self) -> None:
        """Decrease zoom by 10%."""
        self.set_zoom(self._current_zoom - 0.1)

    def reset_zoom(self) -> None:
        """Reset zoom to 100%."""
        self.set_zoom(1.0)

    @property
    def current_zoom(self) -> float:
        """Get current zoom level."""
        return self._current_zoom


class GraphDescriptionGenerator:
    """
    Generates text descriptions of graphs for screen readers.
    
    Provides accessible alternatives for visual data representations.
    """

    @staticmethod
    def describe_line_plot(
        series_name: str,
        x_label: str,
        y_label: str,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        point_count: int,
        trend: str | None = None,
    ) -> str:
        """
        Generate description for a line plot.
        
        Args:
            series_name: Name of the data series
            x_label: X-axis label
            y_label: Y-axis label
            x_range: (min, max) X values
            y_range: (min, max) Y values
            point_count: Number of data points
            trend: Optional trend description
            
        Returns:
            Human-readable description
        """
        description = (
            f"Gráfico de linha: {series_name}. "
            f"Eixo X: {x_label}, de {x_range[0]:.2f} a {x_range[1]:.2f}. "
            f"Eixo Y: {y_label}, de {y_range[0]:.2f} a {y_range[1]:.2f}. "
            f"{point_count} pontos de dados."
        )

        if trend:
            description += f" Tendência: {trend}."

        return description

    @staticmethod
    def describe_selection(
        start: float,
        end: float,
        unit: str,
        selected_count: int,
        total_count: int,
    ) -> str:
        """
        Generate description for a data selection.
        
        Args:
            start: Selection start value
            end: Selection end value
            unit: Unit of measurement
            selected_count: Number of selected points
            total_count: Total number of points
            
        Returns:
            Human-readable description
        """
        return (
            f"Seleção: de {start:.2f} a {end:.2f} {unit}. "
            f"{selected_count} de {total_count} pontos selecionados "
            f"({selected_count / total_count * 100:.1f}%)."
        )


class AccessibilityManager(QObject):
    """
    Main accessibility manager that coordinates all accessibility features.
    
    Usage:
        manager = AccessibilityManager(main_window)
        manager.initialize()
    """

    # Signals
    config_changed = pyqtSignal(AccessibilityConfig)

    def __init__(
        self,
        main_window: QMainWindow,
        config: AccessibilityConfig | None = None,
    ):
        super().__init__(main_window)
        self.main_window = main_window
        self.config = config or AccessibilityConfig()

        # Sub-managers
        self.navigation: KeyboardNavigationManager | None = None
        self.shortcuts: ShortcutManager | None = None
        self.zoom: UIZoomManager | None = None

        # Accessible widgets registry
        self._accessible_widgets: dict[int, AccessibleWidget] = {}

    def initialize(self) -> None:
        """Initialize all accessibility features."""
        logger.info("Initializing accessibility features...")

        # Initialize keyboard navigation
        if self.config.enable_keyboard_navigation:
            self.navigation = KeyboardNavigationManager(self.main_window, self.config)
            self._register_navigation_regions()

        # Initialize shortcuts
        self.shortcuts = ShortcutManager(self.main_window)
        self._connect_shortcut_handlers()

        # Initialize zoom
        if self.config.enable_ui_zoom:
            self.zoom = UIZoomManager(self.main_window, self.config)

        # Apply contrast mode
        app = QApplication.instance()
        if app and self.config.contrast_mode != ContrastMode.NORMAL:
            HighContrastMode.apply(app, self.config.contrast_mode)

        # Setup focus indicators
        if self.config.show_focus_indicators:
            self._setup_focus_indicators()

        logger.info("Accessibility features initialized")

    def _register_navigation_regions(self) -> None:
        """Register navigation regions from main window."""
        if not self.navigation:
            return

        # Find standard regions
        regions = [
            ("Menu", self.main_window.menuBar()),
            ("Toolbar", self.main_window.findChild(QToolBar)),
            ("Status Bar", self.main_window.statusBar()),
        ]

        # Find dock widgets
        for dock in self.main_window.findChildren(QDockWidget):
            regions.append((dock.windowTitle() or dock.objectName(), dock))

        # Register found regions
        for name, widget in regions:
            if widget:
                self.navigation.register_region(name, widget)

    def _connect_shortcut_handlers(self) -> None:
        """Connect shortcut handlers to actions."""
        if not self.shortcuts:
            return

        # Connect to zoom manager
        if self.zoom:
            self.shortcuts.register_handler("view_zoom_in", self.zoom.zoom_in)
            self.shortcuts.register_handler("view_zoom_out", self.zoom.zoom_out)
            self.shortcuts.register_handler("view_zoom_reset", self.zoom.reset_zoom)

        # Connect to navigation
        if self.navigation:
            self.shortcuts.register_handler("nav_next_region", self.navigation._navigate_next_region)
            self.shortcuts.register_handler("nav_prev_region", self.navigation._navigate_previous_region)

    def _setup_focus_indicators(self) -> None:
        """Setup global focus indicator style."""
        app = QApplication.instance()
        if not app:
            return

        color = self.config.focus_indicator_color
        width = self.config.focus_indicator_width

        # Apply focus style via stylesheet
        focus_style = f"""
            *:focus {{
                outline: {width}px solid {color};
                outline-offset: 2px;
            }}
            QPushButton:focus, QLineEdit:focus, QComboBox:focus,
            QSpinBox:focus, QDoubleSpinBox:focus, QSlider:focus,
            QCheckBox:focus, QRadioButton:focus {{
                border: {width}px solid {color};
            }}
        """

        current_style = app.styleSheet() or ""
        app.setStyleSheet(current_style + focus_style)

    def make_accessible(
        self,
        widget: QWidget,
        name: str,
        description: str = "",
    ) -> AccessibleWidget:
        """
        Make a widget accessible with proper labels.
        
        Args:
            widget: Widget to make accessible
            name: Accessible name
            description: Accessible description
            
        Returns:
            AccessibleWidget wrapper
        """
        accessible = AccessibleWidget(widget, name, description)
        self._accessible_widgets[id(widget)] = accessible
        return accessible

    def set_contrast_mode(self, mode: ContrastMode) -> None:
        """
        Set the contrast mode.
        
        Args:
            mode: Contrast mode to apply
        """
        self.config.contrast_mode = mode
        app = QApplication.instance()
        if app:
            HighContrastMode.apply(app, mode)
        self.config_changed.emit(self.config)

    def get_shortcuts_documentation(self) -> str:
        """
        Get formatted documentation of all shortcuts.
        
        Returns:
            Markdown-formatted documentation
        """
        if not self.shortcuts:
            return "Atalhos não configurados."

        lines = ["# Atalhos de Teclado\n"]

        for category, shortcuts in self.shortcuts.get_shortcuts_by_category().items():
            lines.append(f"\n## {category}\n")
            lines.append("| Atalho | Ação |")
            lines.append("|--------|------|")

            for shortcut in sorted(shortcuts, key=lambda s: s.key_sequence):
                lines.append(f"| `{shortcut.key_sequence}` | {shortcut.description} |")

        return "\n".join(lines)


# Convenience function
def setup_accessibility(main_window: QMainWindow) -> AccessibilityManager:
    """
    Setup accessibility for a main window.
    
    Args:
        main_window: Main application window
        
    Returns:
        Configured AccessibilityManager
    """
    manager = AccessibilityManager(main_window)
    manager.initialize()
    return manager


__all__ = [
    "AccessibilityConfig",
    "AccessibilityManager",
    "AccessibleWidget",
    "ContrastMode",
    "GraphDescriptionGenerator",
    "HighContrastMode",
    "KeyboardNavigationManager",
    "ShortcutDefinition",
    "ShortcutManager",
    "UIZoomManager",
    "setup_accessibility",
]
