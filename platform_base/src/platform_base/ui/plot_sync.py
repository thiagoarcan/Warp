"""
Plot Synchronization - Sincronização temporal entre múltiplos plots

Permite sincronizar:
- Zoom (mesma escala X)
- Pan (movimento conjunto)
- Crosshair (mesma posição X)
- Seleção de região (mesma região X)
"""

from __future__ import annotations

from typing import Any
from weakref import WeakSet

from PyQt6.QtCore import QMutex, QMutexLocker, QObject, pyqtSignal

from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class PlotSyncManager(QObject):
    """
    Gerenciador de sincronização entre plots

    Características:
    - Sincronização de zoom X/Y
    - Sincronização de pan
    - Sincronização de crosshair
    - Grupos de sincronização independentes
    """

    # Signals de sincronização
    xlim_changed = pyqtSignal(str, float, float)  # group_id, xmin, xmax
    ylim_changed = pyqtSignal(str, float, float)  # group_id, ymin, ymax
    crosshair_moved = pyqtSignal(str, float, float)  # group_id, x, y
    region_selected = pyqtSignal(str, float, float, float, float)  # group_id, x1, x2, y1, y2

    _instance: PlotSyncManager | None = None
    _initialized: bool = False
    _mutex = QMutex()

    def __new__(cls):
        """Singleton pattern"""
        with QMutexLocker(cls._mutex):
            if cls._instance is None:
                cls._instance = object.__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True

        # Grupos de sincronização: group_id -> set de widgets
        self._groups: dict[str, WeakSet] = {}

        # Configuração por grupo
        self._group_config: dict[str, dict[str, bool]] = {}

        # Estado atual por grupo
        self._group_state: dict[str, dict[str, Any]] = {}

        # Lock para operações thread-safe
        self._lock = QMutex()

        # Flag para evitar loops de sincronização
        self._updating = False

        logger.debug("PlotSyncManager initialized")

    def create_group(self, group_id: str, sync_x: bool = True, sync_y: bool = False,
                     sync_crosshair: bool = True, sync_region: bool = True) -> None:
        """
        Cria um novo grupo de sincronização

        Args:
            group_id: Identificador único do grupo
            sync_x: Sincronizar eixo X (zoom/pan)
            sync_y: Sincronizar eixo Y (zoom/pan)
            sync_crosshair: Sincronizar crosshair
            sync_region: Sincronizar seleção de região
        """
        with QMutexLocker(self._lock):
            if group_id in self._groups:
                logger.warning(f"Sync group already exists: {group_id}")
                return

            self._groups[group_id] = WeakSet()
            self._group_config[group_id] = {
                "sync_x": sync_x,
                "sync_y": sync_y,
                "sync_crosshair": sync_crosshair,
                "sync_region": sync_region,
            }
            self._group_state[group_id] = {
                "xlim": None,
                "ylim": None,
                "crosshair": None,
                "region": None,
            }

            logger.info(f"Sync group created: {group_id}")

    def delete_group(self, group_id: str) -> None:
        """Remove um grupo de sincronização"""
        with QMutexLocker(self._lock):
            if group_id in self._groups:
                del self._groups[group_id]
                del self._group_config[group_id]
                del self._group_state[group_id]
                logger.info(f"Sync group deleted: {group_id}")

    def add_to_group(self, group_id: str, widget) -> bool:
        """
        Adiciona um widget a um grupo de sincronização

        Args:
            group_id: ID do grupo
            widget: Widget de plot (MatplotlibWidget)

        Returns:
            True se adicionado com sucesso
        """
        with QMutexLocker(self._lock):
            if group_id not in self._groups:
                self.create_group(group_id)

            self._groups[group_id].add(widget)

            # Conectar signals do widget
            self._connect_widget(group_id, widget)

            logger.debug(f"Widget added to sync group: {group_id}")
            return True

    def remove_from_group(self, group_id: str, widget) -> None:
        """Remove um widget de um grupo de sincronização"""
        with QMutexLocker(self._lock):
            if group_id in self._groups:
                self._groups[group_id].discard(widget)
                logger.debug(f"Widget removed from sync group: {group_id}")

    def _connect_widget(self, group_id: str, widget):
        """Conecta signals do widget para sincronização"""
        try:
            # Verificar se widget tem os métodos necessários
            if hasattr(widget, "figure") and hasattr(widget, "canvas"):
                # Conectar eventos matplotlib
                widget.canvas.mpl_connect("xlim_changed",
                    lambda event: self._on_xlim_changed(group_id, event))
                widget.canvas.mpl_connect("ylim_changed",
                    lambda event: self._on_ylim_changed(group_id, event))

            # Conectar signals PyQt se existirem
            if hasattr(widget, "coordinates_changed"):
                widget.coordinates_changed.connect(
                    lambda x, y: self._on_crosshair_moved(group_id, x, y))

            if hasattr(widget, "region_selected"):
                widget.region_selected.connect(
                    lambda x1, x2, y1, y2: self._on_region_selected(group_id, x1, x2, y1, y2))

        except Exception as e:
            logger.exception(f"Error connecting widget: {e}")

    def _on_xlim_changed(self, group_id: str, event):
        """Handler para mudança de limites X"""
        if self._updating:
            return

        try:
            ax = event
            if hasattr(ax, "get_xlim"):
                xlim = ax.get_xlim()
                self._sync_xlim(group_id, xlim[0], xlim[1], source=ax)
        except Exception as e:
            logger.exception(f"xlim_changed error: {e}")

    def _on_ylim_changed(self, group_id: str, event):
        """Handler para mudança de limites Y"""
        if self._updating:
            return

        try:
            ax = event
            if hasattr(ax, "get_ylim"):
                ylim = ax.get_ylim()
                self._sync_ylim(group_id, ylim[0], ylim[1], source=ax)
        except Exception as e:
            logger.exception(f"ylim_changed error: {e}")

    def _on_crosshair_moved(self, group_id: str, x: float, y: float):
        """Handler para movimento do crosshair"""
        if self._updating:
            return

        self._sync_crosshair(group_id, x, y)

    def _on_region_selected(self, group_id: str, x1: float, x2: float,
                            y1: float, y2: float):
        """Handler para seleção de região"""
        if self._updating:
            return

        self._sync_region(group_id, x1, x2, y1, y2)

    def _sync_xlim(self, group_id: str, xmin: float, xmax: float, source=None):
        """Sincroniza limites X para todos os widgets do grupo"""
        config = self._group_config.get(group_id, {})
        if not config.get("sync_x", True):
            return

        try:
            self._updating = True

            for widget in self._groups.get(group_id, set()):
                try:
                    ax = widget.figure.gca()
                    if ax is not source:
                        ax.set_xlim(xmin, xmax)
                        widget.canvas.draw_idle()
                except Exception as e:
                    logger.debug(f"Failed to sync xlim for widget in group {group_id}: {e}")

            # Emitir signal
            self.xlim_changed.emit(group_id, xmin, xmax)

        finally:
            self._updating = False

    def _sync_ylim(self, group_id: str, ymin: float, ymax: float, source=None):
        """Sincroniza limites Y para todos os widgets do grupo"""
        config = self._group_config.get(group_id, {})
        if not config.get("sync_y", False):
            return

        try:
            self._updating = True

            for widget in self._groups.get(group_id, set()):
                try:
                    ax = widget.figure.gca()
                    if ax is not source:
                        ax.set_ylim(ymin, ymax)
                        widget.canvas.draw_idle()
                except Exception as e:
                    logger.debug(f"Failed to sync ylim for widget in group {group_id}: {e}")

            # Emitir signal
            self.ylim_changed.emit(group_id, ymin, ymax)

        finally:
            self._updating = False

    def _sync_crosshair(self, group_id: str, x: float, y: float):
        """Sincroniza posição do crosshair para todos os widgets do grupo"""
        config = self._group_config.get(group_id, {})
        if not config.get("sync_crosshair", True):
            return

        try:
            self._updating = True

            for widget in self._groups.get(group_id, set()):
                try:
                    if hasattr(widget, "set_crosshair_position"):
                        widget.set_crosshair_position(x, y)
                except Exception as e:
                    logger.debug(f"Failed to sync crosshair for widget in group {group_id}: {e}")

            # Emitir signal
            self.crosshair_moved.emit(group_id, x, y)

        finally:
            self._updating = False

    def _sync_region(self, group_id: str, x1: float, x2: float,
                     y1: float, y2: float):
        """Sincroniza seleção de região para todos os widgets do grupo"""
        config = self._group_config.get(group_id, {})
        if not config.get("sync_region", True):
            return

        try:
            self._updating = True

            for widget in self._groups.get(group_id, set()):
                try:
                    if hasattr(widget, "set_selection_region"):
                        widget.set_selection_region(x1, x2, y1, y2)
                except Exception:
                    pass

            # Emitir signal
            self.region_selected.emit(group_id, x1, x2, y1, y2)

        finally:
            self._updating = False

    # === API Pública ===

    def sync_zoom(self, group_id: str, xmin: float, xmax: float,
                  ymin: float | None = None, ymax: float | None = None):
        """
        Sincroniza zoom manualmente

        Args:
            group_id: ID do grupo
            xmin, xmax: Limites X
            ymin, ymax: Limites Y (opcional)
        """
        self._sync_xlim(group_id, xmin, xmax)
        if ymin is not None and ymax is not None:
            self._sync_ylim(group_id, ymin, ymax)

    def sync_pan(self, group_id: str, dx: float, dy: float = 0):
        """
        Sincroniza pan manualmente

        Args:
            group_id: ID do grupo
            dx: Deslocamento X
            dy: Deslocamento Y
        """
        for widget in self._groups.get(group_id, set()):
            try:
                ax = widget.figure.gca()
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
                ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
                widget.canvas.draw_idle()
            except Exception as e:
                logger.debug(f"Failed to sync pan for widget in group {group_id}: {e}")

    def get_groups(self) -> list[str]:
        """Retorna lista de grupos existentes"""
        return list(self._groups.keys())

    def get_group_widgets(self, group_id: str) -> list:
        """Retorna widgets de um grupo"""
        return list(self._groups.get(group_id, set()))

    def get_group_config(self, group_id: str) -> dict[str, bool]:
        """Retorna configuração de um grupo"""
        return self._group_config.get(group_id, {}).copy()

    def update_group_config(self, group_id: str, **kwargs):
        """Atualiza configuração de um grupo"""
        if group_id in self._group_config:
            self._group_config[group_id].update(kwargs)
            logger.debug(f"Group config updated: {group_id} -> {kwargs}")


def get_sync_manager() -> PlotSyncManager:
    """Retorna instância singleton do PlotSyncManager"""
    return PlotSyncManager()
