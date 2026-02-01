"""
Tooltip System for Platform Base

Provides comprehensive tooltip support with shortcuts integration.

Features:
- Consistent tooltips across all UI elements
- Shortcut hints in tooltips
- Rich tooltips with HTML support
- Delay and duration configuration
- Contextual help integration

Category 3.3 - Tooltips
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PyQt6.QtCore import QEvent, QObject, QPoint, Qt, QTimer
from PyQt6.QtGui import QEnterEvent
from PyQt6.QtWidgets import QApplication, QLabel, QToolTip, QWidget

from platform_base.utils.i18n import tr
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.ui.shortcuts import ShortcutManager

logger = get_logger(__name__)


@dataclass
class TooltipConfig:
    """Tooltip configuration."""
    show_delay_ms: int = 500
    hide_delay_ms: int = 5000
    show_shortcuts: bool = True
    rich_text: bool = True


# Tooltip definitions for all UI elements
TOOLTIPS: dict[str, dict[str, str]] = {
    # File toolbar buttons
    "btn_new": {
        "tooltip": "Criar nova sessão",
        "shortcut": "file.new",
    },
    "btn_open": {
        "tooltip": "Abrir arquivo de dados",
        "shortcut": "file.open",
    },
    "btn_save": {
        "tooltip": "Salvar sessão atual",
        "shortcut": "file.save",
    },
    "btn_export": {
        "tooltip": "Exportar dados ou gráfico",
        "shortcut": "file.export",
    },
    
    # Edit toolbar buttons
    "btn_undo": {
        "tooltip": "Desfazer última ação",
        "shortcut": "edit.undo",
    },
    "btn_redo": {
        "tooltip": "Refazer ação desfeita",
        "shortcut": "edit.redo",
    },
    "btn_copy": {
        "tooltip": "Copiar seleção",
        "shortcut": "edit.copy",
    },
    "btn_paste": {
        "tooltip": "Colar da área de transferência",
        "shortcut": "edit.paste",
    },
    "btn_delete": {
        "tooltip": "Deletar série selecionada",
        "shortcut": "edit.delete",
    },
    "btn_duplicate": {
        "tooltip": "Duplicar série selecionada",
        "shortcut": "edit.duplicate",
    },
    
    # View toolbar buttons
    "btn_zoom_in": {
        "tooltip": "Aumentar zoom do gráfico",
        "shortcut": "view.zoom_in",
    },
    "btn_zoom_out": {
        "tooltip": "Diminuir zoom do gráfico",
        "shortcut": "view.zoom_out",
    },
    "btn_zoom_fit": {
        "tooltip": "Ajustar zoom para mostrar todos os dados",
        "shortcut": "view.zoom_fit",
    },
    "btn_fullscreen": {
        "tooltip": "Alternar modo tela cheia",
        "shortcut": "view.fullscreen",
    },
    "btn_grid": {
        "tooltip": "Mostrar/ocultar grade do gráfico",
        "shortcut": "view.toggle_grid",
    },
    "btn_legend": {
        "tooltip": "Mostrar/ocultar legenda",
        "shortcut": "view.toggle_legend",
    },
    "btn_refresh": {
        "tooltip": "Atualizar visualização",
        "shortcut": "view.refresh",
    },
    
    # Playback controls
    "btn_play": {
        "tooltip": "Iniciar reprodução dos dados",
        "shortcut": "playback.play_pause",
    },
    "btn_pause": {
        "tooltip": "Pausar reprodução",
        "shortcut": "playback.play_pause",
    },
    "btn_stop": {
        "tooltip": "Parar reprodução e voltar ao início",
        "shortcut": "playback.stop",
    },
    "btn_step_forward": {
        "tooltip": "Avançar 1 segundo",
        "shortcut": "playback.step_forward",
    },
    "btn_step_backward": {
        "tooltip": "Voltar 1 segundo",
        "shortcut": "playback.step_backward",
    },
    "slider_speed": {
        "tooltip": "Ajustar velocidade de reprodução (0.25x - 16x)",
    },
    "slider_position": {
        "tooltip": "Posição atual na linha do tempo (arraste para navegar)",
    },
    
    # Analysis controls
    "btn_derivative": {
        "tooltip": "Calcular derivada da série selecionada",
        "shortcut": "analysis.derivative",
    },
    "btn_integral": {
        "tooltip": "Calcular integral da série selecionada",
        "shortcut": "analysis.integral",
    },
    "btn_statistics": {
        "tooltip": "Exibir estatísticas da série (média, desvio, etc.)",
        "shortcut": "analysis.statistics",
    },
    "btn_filter": {
        "tooltip": "Aplicar filtro à série (passa-baixa, passa-alta, etc.)",
        "shortcut": "analysis.filter",
    },
    "combo_filter_type": {
        "tooltip": "Tipo de filtro a aplicar",
    },
    "spin_cutoff": {
        "tooltip": "Frequência de corte do filtro em Hz",
    },
    
    # Selection controls
    "btn_select_all": {
        "tooltip": "Selecionar todos os pontos da série",
        "shortcut": "select.all",
    },
    "btn_select_none": {
        "tooltip": "Limpar seleção atual",
        "shortcut": "select.none",
    },
    "btn_select_invert": {
        "tooltip": "Inverter seleção atual",
        "shortcut": "select.invert",
    },
    
    # Data panel
    "tree_datasets": {
        "tooltip": "Lista de conjuntos de dados carregados\\nDuplo-clique para plotar\\nArraste para o gráfico",
    },
    "check_series": {
        "tooltip": "Marcar para mostrar no gráfico\\nDesmarcar para ocultar",
    },
    "btn_remove_dataset": {
        "tooltip": "Remover conjunto de dados selecionado",
    },
    "btn_rename_series": {
        "tooltip": "Renomear série selecionada (duplo-clique)",
    },
    
    # Config panel
    "combo_interpolation": {
        "tooltip": "Método de interpolação para cálculos\\n- Linear: interpolação linear simples\\n- Cubic: spline cúbica (mais suave)\\n- Zero: mantém valor anterior",
    },
    "spin_decimation": {
        "tooltip": "Fator de decimação para visualização\\nValores maiores = menos pontos = mais rápido",
    },
    "check_auto_decimation": {
        "tooltip": "Ajustar decimação automaticamente baseado no zoom",
    },
    "combo_theme": {
        "tooltip": "Tema visual da aplicação (claro, escuro, sistema)",
    },
    "combo_language": {
        "tooltip": "Idioma da interface",
    },
    
    # Results panel
    "table_results": {
        "tooltip": "Resultados de cálculos e análises\\nDuplo-clique para copiar valor",
    },
    "btn_export_results": {
        "tooltip": "Exportar resultados para CSV",
    },
    "btn_clear_results": {
        "tooltip": "Limpar todos os resultados",
    },
    
    # 3D view
    "btn_3d_reset_camera": {
        "tooltip": "Resetar posição da câmera para vista padrão",
    },
    "btn_3d_screenshot": {
        "tooltip": "Capturar imagem da visualização 3D",
    },
    "combo_colormap": {
        "tooltip": "Mapa de cores para visualização 3D",
    },
    
    # Status bar
    "label_memory": {
        "tooltip": "Uso de memória da aplicação\\nClique para detalhes",
    },
    "label_status": {
        "tooltip": "Status atual da operação",
    },
    "progress_bar": {
        "tooltip": "Progresso da operação atual\\nClique para cancelar",
    },
}


class TooltipManager:
    """
    Manages tooltips for the application.
    
    Provides:
    - Automatic tooltip application
    - Shortcut hints
    - Rich text tooltips
    - Centralized configuration
    """
    
    _instance: TooltipManager | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config = TooltipConfig()
        self._shortcut_manager: ShortcutManager | None = None
        
        logger.debug("tooltip_manager_initialized")
    
    def set_shortcut_manager(self, manager: ShortcutManager):
        """Set shortcut manager for tooltip hints."""
        self._shortcut_manager = manager
    
    def get_tooltip(self, widget_id: str) -> str:
        """
        Get formatted tooltip for a widget.
        
        Args:
            widget_id: Widget identifier
            
        Returns:
            Formatted tooltip string
        """
        tooltip_def = TOOLTIPS.get(widget_id)
        if tooltip_def is None:
            return ""
        
        tooltip = tooltip_def.get("tooltip", "")
        
        # Add shortcut hint if available
        if self._config.show_shortcuts and self._shortcut_manager:
            shortcut_id = tooltip_def.get("shortcut")
            if shortcut_id:
                binding = self._shortcut_manager.get_binding(shortcut_id)
                if binding:
                    shortcut_hint = f" ({binding.key_sequence})"
                    tooltip += shortcut_hint
        
        # Format as rich text if enabled
        if self._config.rich_text and "\n" in tooltip:
            tooltip = tooltip.replace("\n", "<br>")
        
        return tooltip
    
    def apply_tooltip(self, widget: QWidget, widget_id: str):
        """
        Apply tooltip to a widget.
        
        Args:
            widget: Widget to apply tooltip to
            widget_id: Widget identifier for tooltip lookup
        """
        tooltip = self.get_tooltip(widget_id)
        if tooltip:
            widget.setToolTip(tooltip)
    
    def apply_all_tooltips(self, parent: QWidget, mappings: dict[str, QWidget]):
        """
        Apply tooltips to multiple widgets.
        
        Args:
            parent: Parent widget (for context)
            mappings: Dict of widget_id -> widget
        """
        for widget_id, widget in mappings.items():
            self.apply_tooltip(widget, widget_id)
    
    def register_tooltip(self, widget_id: str, tooltip: str, shortcut: str | None = None):
        """
        Register a custom tooltip.
        
        Args:
            widget_id: Widget identifier
            tooltip: Tooltip text
            shortcut: Optional shortcut action ID
        """
        TOOLTIPS[widget_id] = {
            "tooltip": tooltip,
        }
        if shortcut:
            TOOLTIPS[widget_id]["shortcut"] = shortcut
    
    @property
    def config(self) -> TooltipConfig:
        """Get tooltip configuration."""
        return self._config


class RichTooltip(QLabel):
    """
    Rich tooltip widget with extended features.
    
    Supports:
    - HTML content
    - Images
    - Delayed show/hide
    - Position adjustment
    """
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, Qt.WindowType.ToolTip)
        
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setStyleSheet("""
            QLabel {
                background-color: #FFFFCC;
                border: 1px solid #808080;
                padding: 4px;
                font-size: 12px;
            }
        """)
        
        self._show_timer = QTimer(self)
        self._hide_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._hide_timer.setSingleShot(True)
        
        self._show_timer.timeout.connect(self._do_show)
        self._hide_timer.timeout.connect(self.hide)
        
        self._pending_text = ""
        self._pending_pos = QPoint()
    
    def show_tooltip(
        self,
        text: str,
        pos: QPoint,
        delay_ms: int = 500,
        duration_ms: int = 5000,
    ):
        """
        Show tooltip with delay.
        
        Args:
            text: Tooltip text (can be HTML)
            pos: Global position to show at
            delay_ms: Delay before showing
            duration_ms: Duration before auto-hide
        """
        self._pending_text = text
        self._pending_pos = pos
        
        self._hide_timer.stop()
        self._show_timer.start(delay_ms)
        
        if duration_ms > 0:
            self._hide_timer.start(delay_ms + duration_ms)
    
    def _do_show(self):
        """Actually show the tooltip."""
        self.setText(self._pending_text)
        self.adjustSize()
        
        # Adjust position to stay on screen
        pos = self._adjust_position(self._pending_pos)
        self.move(pos)
        self.show()
    
    def _adjust_position(self, pos: QPoint) -> QPoint:
        """Adjust position to keep tooltip on screen."""
        screen = QApplication.screenAt(pos)
        if screen is None:
            screen = QApplication.primaryScreen()
        
        screen_rect = screen.availableGeometry()
        
        x = pos.x()
        y = pos.y() + 20  # Offset below cursor
        
        # Adjust horizontal
        if x + self.width() > screen_rect.right():
            x = screen_rect.right() - self.width()
        if x < screen_rect.left():
            x = screen_rect.left()
        
        # Adjust vertical
        if y + self.height() > screen_rect.bottom():
            y = pos.y() - self.height() - 5  # Show above cursor
        if y < screen_rect.top():
            y = screen_rect.top()
        
        return QPoint(x, y)
    
    def cancel(self):
        """Cancel pending tooltip."""
        self._show_timer.stop()
        self._hide_timer.stop()
        self.hide()


class TooltipEventFilter(QObject):
    """
    Event filter for automatic tooltip management.
    
    Installs on parent widget to handle tooltip events
    for all child widgets.
    """
    
    def __init__(
        self,
        tooltip_manager: TooltipManager,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._manager = tooltip_manager
        self._rich_tooltip = RichTooltip()
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle tooltip events."""
        if not isinstance(obj, QWidget):
            return False
        
        if event.type() == QEvent.Type.ToolTip:
            # Check if we have rich tooltip for this widget
            widget_name = obj.objectName()
            if widget_name and widget_name in TOOLTIPS:
                tooltip_def = TOOLTIPS[widget_name]
                tooltip = tooltip_def.get("tooltip", "")
                
                # Use rich tooltip if multiline
                if "\n" in tooltip or "<" in tooltip:
                    enter_event = event
                    if isinstance(enter_event, QEnterEvent):
                        pos = enter_event.globalPosition().toPoint()
                    else:
                        pos = obj.mapToGlobal(QPoint(0, 0))
                    
                    formatted = self._manager.get_tooltip(widget_name)
                    self._rich_tooltip.show_tooltip(formatted, pos)
                    return True
        
        elif event.type() == QEvent.Type.Leave:
            self._rich_tooltip.cancel()
        
        return False


def apply_standard_tooltips(window: QWidget):
    """
    Apply standard tooltips to a main window.
    
    Finds widgets by object name and applies appropriate tooltips.
    
    Args:
        window: Main window widget
    """
    manager = TooltipManager()
    
    # Find all widgets with object names matching our tooltips
    for widget_id in TOOLTIPS:
        widget = window.findChild(QWidget, widget_id)
        if widget:
            manager.apply_tooltip(widget, widget_id)
    
    logger.debug("standard_tooltips_applied", count=len(TOOLTIPS))


def get_tooltip_manager() -> TooltipManager:
    """Get the global TooltipManager instance."""
    return TooltipManager()


__all__ = [
    "RichTooltip",
    "TOOLTIPS",
    "TooltipConfig",
    "TooltipEventFilter",
    "TooltipManager",
    "apply_standard_tooltips",
    "get_tooltip_manager",
]
