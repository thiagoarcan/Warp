"""
Keyboard Shortcuts System for Platform Base

Provides customizable keyboard shortcuts with persistence.

Features:
- Default shortcuts for all main actions
- User-customizable bindings
- Conflict detection
- Settings persistence
- Shortcut hints in tooltips

Category 3.4 - Keyboard Shortcuts
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QObject, QSettings, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


class ShortcutCategory(Enum):
    """Categories of shortcuts."""
    FILE = auto()
    EDIT = auto()
    VIEW = auto()
    NAVIGATION = auto()
    ANALYSIS = auto()
    PLAYBACK = auto()
    SELECTION = auto()
    HELP = auto()


@dataclass
class ShortcutBinding:
    """Represents a keyboard shortcut binding."""
    action_id: str
    category: ShortcutCategory
    description: str
    default_key: str  # e.g., "Ctrl+S"
    current_key: str | None = None  # None = use default
    action: QAction | None = None
    callback: Any = None

    @property
    def key_sequence(self) -> str:
        """Get effective key sequence."""
        return self.current_key or self.default_key

    def reset_to_default(self):
        """Reset to default key binding."""
        self.current_key = None


# Default shortcuts
DEFAULT_SHORTCUTS: dict[str, dict] = {
    # File operations
    "file.new": {
        "category": ShortcutCategory.FILE,
        "description": "Nova sessão",
        "default_key": "Ctrl+N",
    },
    "file.open": {
        "category": ShortcutCategory.FILE,
        "description": "Abrir arquivo",
        "default_key": "Ctrl+O",
    },
    "file.save": {
        "category": ShortcutCategory.FILE,
        "description": "Salvar sessão",
        "default_key": "Ctrl+S",
    },
    "file.save_as": {
        "category": ShortcutCategory.FILE,
        "description": "Salvar como",
        "default_key": "Ctrl+Shift+S",
    },
    "file.export": {
        "category": ShortcutCategory.FILE,
        "description": "Exportar dados",
        "default_key": "Ctrl+E",
    },
    "file.close": {
        "category": ShortcutCategory.FILE,
        "description": "Fechar",
        "default_key": "Ctrl+W",
    },
    "file.quit": {
        "category": ShortcutCategory.FILE,
        "description": "Sair",
        "default_key": "Ctrl+Q",
    },

    # Edit operations
    "edit.undo": {
        "category": ShortcutCategory.EDIT,
        "description": "Desfazer",
        "default_key": "Ctrl+Z",
    },
    "edit.redo": {
        "category": ShortcutCategory.EDIT,
        "description": "Refazer",
        "default_key": "Ctrl+Y",
    },
    "edit.cut": {
        "category": ShortcutCategory.EDIT,
        "description": "Recortar",
        "default_key": "Ctrl+X",
    },
    "edit.copy": {
        "category": ShortcutCategory.EDIT,
        "description": "Copiar",
        "default_key": "Ctrl+C",
    },
    "edit.paste": {
        "category": ShortcutCategory.EDIT,
        "description": "Colar",
        "default_key": "Ctrl+V",
    },
    "edit.delete": {
        "category": ShortcutCategory.EDIT,
        "description": "Deletar",
        "default_key": "Delete",
    },
    "edit.duplicate": {
        "category": ShortcutCategory.EDIT,
        "description": "Duplicar série",
        "default_key": "Ctrl+D",
    },
    "edit.preferences": {
        "category": ShortcutCategory.EDIT,
        "description": "Preferências",
        "default_key": "Ctrl+,",
    },

    # View operations
    "view.zoom_in": {
        "category": ShortcutCategory.VIEW,
        "description": "Aumentar zoom",
        "default_key": "Ctrl++",
    },
    "view.zoom_out": {
        "category": ShortcutCategory.VIEW,
        "description": "Diminuir zoom",
        "default_key": "Ctrl+-",
    },
    "view.zoom_fit": {
        "category": ShortcutCategory.VIEW,
        "description": "Ajustar à janela",
        "default_key": "Ctrl+0",
    },
    "view.fullscreen": {
        "category": ShortcutCategory.VIEW,
        "description": "Tela cheia",
        "default_key": "F11",
    },
    "view.toggle_grid": {
        "category": ShortcutCategory.VIEW,
        "description": "Mostrar/ocultar grade",
        "default_key": "G",
    },
    "view.toggle_legend": {
        "category": ShortcutCategory.VIEW,
        "description": "Mostrar/ocultar legenda",
        "default_key": "L",
    },
    "view.refresh": {
        "category": ShortcutCategory.VIEW,
        "description": "Atualizar",
        "default_key": "F5",
    },

    # Navigation
    "nav.go_to_start": {
        "category": ShortcutCategory.NAVIGATION,
        "description": "Ir para início",
        "default_key": "Home",
    },
    "nav.go_to_end": {
        "category": ShortcutCategory.NAVIGATION,
        "description": "Ir para fim",
        "default_key": "End",
    },
    "nav.pan_left": {
        "category": ShortcutCategory.NAVIGATION,
        "description": "Mover esquerda",
        "default_key": "Left",
    },
    "nav.pan_right": {
        "category": ShortcutCategory.NAVIGATION,
        "description": "Mover direita",
        "default_key": "Right",
    },

    # Analysis
    "analysis.derivative": {
        "category": ShortcutCategory.ANALYSIS,
        "description": "Calcular derivada",
        "default_key": "Alt+D",
    },
    "analysis.integral": {
        "category": ShortcutCategory.ANALYSIS,
        "description": "Calcular integral",
        "default_key": "Alt+I",
    },
    "analysis.statistics": {
        "category": ShortcutCategory.ANALYSIS,
        "description": "Estatísticas",
        "default_key": "Alt+S",
    },
    "analysis.filter": {
        "category": ShortcutCategory.ANALYSIS,
        "description": "Aplicar filtro",
        "default_key": "Alt+F",
    },

    # Playback (streaming)
    "playback.play_pause": {
        "category": ShortcutCategory.PLAYBACK,
        "description": "Play/Pause",
        "default_key": "Space",
    },
    "playback.stop": {
        "category": ShortcutCategory.PLAYBACK,
        "description": "Parar",
        "default_key": "Escape",
    },
    "playback.step_forward": {
        "category": ShortcutCategory.PLAYBACK,
        "description": "Avançar 1 segundo",
        "default_key": ".",
    },
    "playback.step_backward": {
        "category": ShortcutCategory.PLAYBACK,
        "description": "Voltar 1 segundo",
        "default_key": ",",
    },
    "playback.speed_up": {
        "category": ShortcutCategory.PLAYBACK,
        "description": "Aumentar velocidade",
        "default_key": "]",
    },
    "playback.speed_down": {
        "category": ShortcutCategory.PLAYBACK,
        "description": "Diminuir velocidade",
        "default_key": "[",
    },

    # Selection
    "select.all": {
        "category": ShortcutCategory.SELECTION,
        "description": "Selecionar tudo",
        "default_key": "Ctrl+A",
    },
    "select.none": {
        "category": ShortcutCategory.SELECTION,
        "description": "Limpar seleção",
        "default_key": "Ctrl+Shift+A",
    },
    "select.invert": {
        "category": ShortcutCategory.SELECTION,
        "description": "Inverter seleção",
        "default_key": "Ctrl+I",
    },

    # Help
    "help.documentation": {
        "category": ShortcutCategory.HELP,
        "description": "Documentação",
        "default_key": "F1",
    },
    "help.shortcuts": {
        "category": ShortcutCategory.HELP,
        "description": "Lista de atalhos",
        "default_key": "Ctrl+/",
    },
    "help.whats_this": {
        "category": ShortcutCategory.HELP,
        "description": "O que é isto?",
        "default_key": "Shift+F1",
    },
}


class ShortcutManager(QObject):
    """
    Manages keyboard shortcuts with customization support.
    
    Provides:
    - Registration of shortcuts
    - Conflict detection
    - Persistence via QSettings
    - Binding to QActions and callbacks
    """

    # Singleton instance
    _instance: ShortcutManager | None = None

    # Signals
    shortcut_changed = pyqtSignal(str, str)  # action_id, new_key
    shortcut_triggered = pyqtSignal(str)  # action_id

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True

        self._bindings: dict[str, ShortcutBinding] = {}
        self._shortcuts: dict[str, QShortcut] = {}
        self._parent_widget: QWidget | None = None

        # Load default shortcuts
        self._load_defaults()

        # Load user customizations
        self._load_settings()

        logger.debug("shortcut_manager_initialized", shortcuts=len(self._bindings))

    def _load_defaults(self):
        """Load default shortcut definitions."""
        for action_id, config in DEFAULT_SHORTCUTS.items():
            binding = ShortcutBinding(
                action_id=action_id,
                category=config["category"],
                description=config["description"],
                default_key=config["default_key"],
            )
            self._bindings[action_id] = binding

    def _load_settings(self):
        """Load user-customized shortcuts from settings."""
        settings = QSettings("PlatformBase", "Shortcuts")

        for action_id, binding in self._bindings.items():
            custom_key = settings.value(f"shortcuts/{action_id}", None)
            if custom_key:
                binding.current_key = custom_key

    def _save_settings(self):
        """Save user-customized shortcuts to settings."""
        settings = QSettings("PlatformBase", "Shortcuts")

        for action_id, binding in self._bindings.items():
            if binding.current_key:
                settings.setValue(f"shortcuts/{action_id}", binding.current_key)
            else:
                settings.remove(f"shortcuts/{action_id}")

    def set_parent_widget(self, widget: QWidget):
        """Set parent widget for QShortcuts."""
        self._parent_widget = widget
        self._create_shortcuts()

    def _create_shortcuts(self):
        """Create QShortcut objects for all bindings."""
        if self._parent_widget is None:
            return

        # Clear existing shortcuts
        for shortcut in self._shortcuts.values():
            shortcut.deleteLater()
        self._shortcuts.clear()

        # Create new shortcuts
        for action_id, binding in self._bindings.items():
            shortcut = QShortcut(
                QKeySequence(binding.key_sequence),
                self._parent_widget,
            )
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

            # Connect to callback if set
            if binding.callback:
                shortcut.activated.connect(binding.callback)

            # Connect generic signal
            shortcut.activated.connect(
                lambda aid=action_id: self.shortcut_triggered.emit(aid),
            )

            self._shortcuts[action_id] = shortcut

    def register_callback(self, action_id: str, callback: Callable):
        """
        Register callback for a shortcut.
        
        Args:
            action_id: Shortcut action ID
            callback: Function to call when triggered
        """
        if action_id not in self._bindings:
            logger.warning("unknown_shortcut_action", action_id=action_id)
            return

        self._bindings[action_id].callback = callback

        # Update shortcut if exists
        if action_id in self._shortcuts:
            self._shortcuts[action_id].activated.connect(callback)

    def bind_action(self, action_id: str, action: QAction):
        """
        Bind shortcut to a QAction.
        
        Args:
            action_id: Shortcut action ID
            action: QAction to bind
        """
        if action_id not in self._bindings:
            logger.warning("unknown_shortcut_action", action_id=action_id)
            return

        binding = self._bindings[action_id]
        binding.action = action
        action.setShortcut(QKeySequence(binding.key_sequence))

    def set_shortcut(self, action_id: str, key: str) -> bool:
        """
        Set custom shortcut for an action.
        
        Args:
            action_id: Action to modify
            key: New key sequence (e.g., "Ctrl+Shift+N")
            
        Returns:
            True if successful, False if conflict
        """
        # Check for conflicts
        conflict = self.check_conflict(key, exclude=action_id)
        if conflict:
            logger.warning("shortcut_conflict", key=key, conflicting_action=conflict)
            return False

        binding = self._bindings.get(action_id)
        if binding is None:
            return False

        # Update binding
        binding.current_key = key

        # Update QAction if bound
        if binding.action:
            binding.action.setShortcut(QKeySequence(key))

        # Update QShortcut
        if action_id in self._shortcuts:
            self._shortcuts[action_id].setKey(QKeySequence(key))

        # Save and emit
        self._save_settings()
        self.shortcut_changed.emit(action_id, key)

        logger.info("shortcut_changed", action_id=action_id, key=key)
        return True

    def reset_shortcut(self, action_id: str):
        """Reset shortcut to default."""
        binding = self._bindings.get(action_id)
        if binding is None:
            return

        binding.reset_to_default()

        # Update QAction if bound
        if binding.action:
            binding.action.setShortcut(QKeySequence(binding.default_key))

        # Update QShortcut
        if action_id in self._shortcuts:
            self._shortcuts[action_id].setKey(QKeySequence(binding.default_key))

        self._save_settings()
        self.shortcut_changed.emit(action_id, binding.default_key)

    def reset_all(self):
        """Reset all shortcuts to defaults."""
        for action_id in self._bindings:
            self.reset_shortcut(action_id)

    def check_conflict(self, key: str, exclude: str | None = None) -> str | None:
        """
        Check if key sequence conflicts with existing shortcuts.
        
        Args:
            key: Key sequence to check
            exclude: Action ID to exclude from check
            
        Returns:
            Conflicting action ID or None
        """
        for action_id, binding in self._bindings.items():
            if action_id == exclude:
                continue
            if binding.key_sequence.lower() == key.lower():
                return action_id
        return None

    def get_binding(self, action_id: str) -> ShortcutBinding | None:
        """Get binding for action ID."""
        return self._bindings.get(action_id)

    def get_bindings_by_category(
        self,
        category: ShortcutCategory,
    ) -> list[ShortcutBinding]:
        """Get all bindings in a category."""
        return [b for b in self._bindings.values() if b.category == category]

    def get_all_bindings(self) -> dict[str, ShortcutBinding]:
        """Get all bindings."""
        return self._bindings.copy()

    def format_tooltip_with_shortcut(
        self,
        tooltip: str,
        action_id: str,
    ) -> str:
        """
        Format tooltip to include shortcut hint.
        
        Args:
            tooltip: Base tooltip text
            action_id: Action ID to get shortcut for
            
        Returns:
            Tooltip with shortcut hint
        """
        binding = self._bindings.get(action_id)
        if binding:
            return f"{tooltip} ({binding.key_sequence})"
        return tooltip


class ShortcutsDialog(QDialog):
    """
    Dialog for viewing and customizing keyboard shortcuts.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWindowTitle(tr("keyboard_shortcuts"))
        self.setMinimumSize(600, 500)

        self._manager = ShortcutManager()
        self._pending_changes: dict[str, str] = {}

        self._setup_ui()
        self._load_shortcuts()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(tr("search") + ":"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(tr("search_shortcuts"))
        self._search_edit.textChanged.connect(self._filter_shortcuts)
        search_layout.addWidget(self._search_edit)
        layout.addLayout(search_layout)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels([
            tr("action"),
            tr("description"),
            tr("shortcut"),
            tr("default"),
        ])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch,
        )
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows,
        )
        self._table.cellDoubleClicked.connect(self._edit_shortcut)
        layout.addWidget(self._table)

        # Buttons
        button_layout = QHBoxLayout()

        reset_btn = QPushButton(tr("reset_selected"))
        reset_btn.clicked.connect(self._reset_selected)
        button_layout.addWidget(reset_btn)

        reset_all_btn = QPushButton(tr("reset_all"))
        reset_all_btn.clicked.connect(self._reset_all)
        button_layout.addWidget(reset_all_btn)

        button_layout.addStretch()

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply,
        )
        button_box.accepted.connect(self._apply_and_close)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._apply_changes,
        )
        button_layout.addWidget(button_box)

        layout.addLayout(button_layout)

    def _load_shortcuts(self):
        """Load shortcuts into table."""
        bindings = self._manager.get_all_bindings()
        self._table.setRowCount(len(bindings))

        for row, (action_id, binding) in enumerate(sorted(bindings.items())):
            # Action ID
            id_item = QTableWidgetItem(action_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 0, id_item)

            # Description
            desc_item = QTableWidgetItem(binding.description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 1, desc_item)

            # Current shortcut
            key_item = QTableWidgetItem(binding.key_sequence)
            key_item.setFlags(key_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 2, key_item)

            # Default
            default_item = QTableWidgetItem(binding.default_key)
            default_item.setFlags(default_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 3, default_item)

    def _filter_shortcuts(self, text: str):
        """Filter shortcuts by search text."""
        text = text.lower()
        for row in range(self._table.rowCount()):
            show = False
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                if item and text in item.text().lower():
                    show = True
                    break
            self._table.setRowHidden(row, not show)

    def _edit_shortcut(self, row: int, col: int):
        """Open shortcut edit dialog."""
        if col != 2:  # Only edit shortcut column
            return

        action_id = self._table.item(row, 0).text()
        current_key = self._table.item(row, 2).text()

        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("edit_shortcut"))
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(tr("press_new_shortcut")))

        key_edit = QKeySequenceEdit(QKeySequence(current_key))
        layout.addWidget(key_edit)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_key = key_edit.keySequence().toString()
            if new_key:
                # Check conflict
                conflict = self._manager.check_conflict(new_key, exclude=action_id)
                if conflict:
                    QMessageBox.warning(
                        self,
                        tr("conflict"),
                        tr("shortcut_already_used").format(conflict),
                    )
                    return

                # Store pending change
                self._pending_changes[action_id] = new_key
                self._table.item(row, 2).setText(new_key)

    def _reset_selected(self):
        """Reset selected shortcut to default."""
        current = self._table.currentRow()
        if current < 0:
            return

        action_id = self._table.item(current, 0).text()
        default_key = self._table.item(current, 3).text()

        self._pending_changes[action_id] = default_key
        self._table.item(current, 2).setText(default_key)

    def _reset_all(self):
        """Reset all shortcuts to defaults."""
        reply = QMessageBox.question(
            self,
            tr("confirm"),
            tr("reset_all_shortcuts_confirm"),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for row in range(self._table.rowCount()):
            action_id = self._table.item(row, 0).text()
            default_key = self._table.item(row, 3).text()
            self._pending_changes[action_id] = default_key
            self._table.item(row, 2).setText(default_key)

    def _apply_changes(self):
        """Apply pending changes."""
        for action_id, new_key in self._pending_changes.items():
            binding = self._manager.get_binding(action_id)
            if binding and new_key == binding.default_key:
                self._manager.reset_shortcut(action_id)
            else:
                self._manager.set_shortcut(action_id, new_key)

        self._pending_changes.clear()

    def _apply_and_close(self):
        """Apply changes and close dialog."""
        self._apply_changes()
        self.accept()


def get_shortcut_manager() -> ShortcutManager:
    """Get the global ShortcutManager instance."""
    return ShortcutManager()


__all__ = [
    "DEFAULT_SHORTCUTS",
    "ShortcutBinding",
    "ShortcutCategory",
    "ShortcutManager",
    "ShortcutsDialog",
    "get_shortcut_manager",
]
