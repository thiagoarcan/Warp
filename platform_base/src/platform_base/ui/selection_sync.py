"""
Selection Sync - Sistema de sincronização de seleções entre múltiplas views

Features:
- Sincronização automática de seleções entre views
- Broadcast de mudanças de seleção
- Coordenação com multi-view synchronizer
- Filtros de sincronização por tipo de view
- Histórico centralizado de seleções
"""

from __future__ import annotations

import builtins
import contextlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from platform_base.ui.selection import Selection, SelectionCriteria, SelectionMode
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.core.models import ViewID
    from platform_base.ui.multi_view_sync import MultiViewSynchronizer


logger = get_logger(__name__)


class SelectionSyncMode(Enum):
    """Modos de sincronização de seleção"""
    DISABLED = "disabled"     # Sem sincronização
    MANUAL = "manual"         # Sincronização manual apenas
    AUTO = "auto"             # Sincronização automática
    FILTERED = "filtered"     # Sincronização com filtros por tipo


@dataclass
class SelectionSyncFilter:
    """Filtros para sincronização de seleção"""
    allowed_view_types: set[str] | None = None      # Tipos de view permitidos
    allowed_selection_modes: set[SelectionMode] | None = None  # Modos de seleção permitidos
    min_selection_size: int = 1                        # Tamanho mínimo de seleção
    max_selection_size: int | None = None           # Tamanho máximo de seleção
    temporal_tolerance: float = 0.001                  # Tolerância temporal para sincronização


@dataclass
class SelectionSyncEvent:
    """Evento de sincronização de seleção"""
    source_view_id: ViewID
    target_view_id: ViewID
    selection: Selection
    sync_mode: SelectionSyncMode
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    error_message: str | None = None


class SelectionSynchronizer(QObject):
    """
    Sincronizador de seleções entre múltiplas views

    Coordena sincronização de seleções entre views, aplicando filtros
    e transformações apropriadas para cada tipo de view.
    """

    # Signals
    selection_synced = pyqtSignal(object)  # SelectionSyncEvent
    sync_failed = pyqtSignal(str, str)     # source_view_id, error
    sync_mode_changed = pyqtSignal(object) # SelectionSyncMode

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        # Registry de views que participam da sincronização
        self.registered_views: dict[ViewID, SelectionSyncView] = {}

        # Configuração de sincronização
        self.sync_mode = SelectionSyncMode.AUTO
        self.sync_filter = SelectionSyncFilter()

        # Histórico de eventos de sincronização
        self.sync_events: list[SelectionSyncEvent] = []
        self.max_history_size = 1000

        # Flag para evitar loops de sincronização
        self._sync_in_progress = False

        logger.info("selection_synchronizer_initialized")

    def register_view(self, view_id: ViewID, view: SelectionSyncView):
        """Registra view para sincronização de seleção"""
        if view_id in self.registered_views:
            logger.warning("view_already_registered_for_selection_sync", view_id=view_id)
            return

        self.registered_views[view_id] = view

        # Connect view's selection signals
        view.selection_changed.connect(
            lambda selection: self._on_view_selection_changed(view_id, selection),
        )

        logger.info("view_registered_for_selection_sync",
                   view_id=view_id,
                   total_views=len(self.registered_views))

    def unregister_view(self, view_id: ViewID):
        """Remove view da sincronização"""
        if view_id in self.registered_views:
            view = self.registered_views[view_id]

            # Disconnect signals
            with contextlib.suppress(builtins.BaseException):
                view.selection_changed.disconnect()

            del self.registered_views[view_id]
            logger.info("view_unregistered_from_selection_sync", view_id=view_id)

    def set_sync_mode(self, mode: SelectionSyncMode):
        """Define modo de sincronização"""
        old_mode = self.sync_mode
        self.sync_mode = mode

        self.sync_mode_changed.emit(mode)
        logger.info("selection_sync_mode_changed", old_mode=old_mode.value, new_mode=mode.value)

    def set_sync_filter(self, filter_config: SelectionSyncFilter):
        """Define filtros de sincronização"""
        self.sync_filter = filter_config
        logger.info("selection_sync_filter_updated")

    def sync_selection_to_views(self, source_view_id: ViewID, selection: Selection,
                               target_view_ids: list[ViewID] | None = None) -> list[SelectionSyncEvent]:
        """
        Sincroniza seleção para views específicas ou todas as views

        Args:
            source_view_id: ID da view que originou a seleção
            selection: Seleção a ser sincronizada
            target_view_ids: IDs das views alvo (None = todas exceto source)

        Returns:
            Lista de eventos de sincronização
        """
        if self._sync_in_progress:
            return []

        if self.sync_mode == SelectionSyncMode.DISABLED:
            return []

        # Determine target views
        if target_view_ids is None:
            target_view_ids = [vid for vid in self.registered_views if vid != source_view_id]

        sync_events = []
        self._sync_in_progress = True

        try:
            for target_view_id in target_view_ids:
                if target_view_id not in self.registered_views:
                    continue

                # Apply filters
                if not self._should_sync_to_view(source_view_id, target_view_id, selection):
                    continue

                # Transform selection for target view
                transformed_selection = self._transform_selection_for_view(
                    selection, target_view_id,
                )

                if transformed_selection is None:
                    continue

                # Apply selection to target view
                target_view = self.registered_views[target_view_id]
                success = True
                error_message = None

                try:
                    target_view.apply_synced_selection(transformed_selection)

                except Exception as e:
                    success = False
                    error_message = str(e)
                    logger.exception("selection_sync_failed",
                               source_view=source_view_id,
                               target_view=target_view_id,
                               error=str(e))

                # Create sync event
                event = SelectionSyncEvent(
                    source_view_id=source_view_id,
                    target_view_id=target_view_id,
                    selection=transformed_selection,
                    sync_mode=self.sync_mode,
                    success=success,
                    error_message=error_message,
                )

                sync_events.append(event)
                self._add_sync_event(event)

                if success:
                    self.selection_synced.emit(event)
                else:
                    self.sync_failed.emit(source_view_id, error_message)

        finally:
            self._sync_in_progress = False

        logger.info("selection_sync_completed",
                   source_view=source_view_id,
                   target_count=len(sync_events),
                   successful_count=sum(1 for e in sync_events if e.success))

        return sync_events

    @pyqtSlot(str, object)
    def _on_view_selection_changed(self, view_id: ViewID, selection: Selection | None):
        """Callback quando seleção de uma view muda"""
        if self._sync_in_progress or self.sync_mode == SelectionSyncMode.DISABLED:
            return

        if selection is None:
            # Clear selection in other views
            self._clear_selection_in_views(view_id)
            return

        if self.sync_mode == SelectionSyncMode.AUTO:
            # Auto-sync to other views
            self.sync_selection_to_views(view_id, selection)

        # Manual mode requires explicit sync calls

    def _clear_selection_in_views(self, source_view_id: ViewID):
        """Limpa seleção em outras views"""
        for view_id, view in self.registered_views.items():
            if view_id != source_view_id:
                try:
                    view.clear_synced_selection()
                except Exception as e:
                    logger.exception("clear_selection_failed",
                               target_view=view_id, error=str(e))

    def _should_sync_to_view(self, source_view_id: ViewID, target_view_id: ViewID,
                           selection: Selection) -> bool:
        """Verifica se deve sincronizar seleção para view alvo"""
        if source_view_id == target_view_id:
            return False

        # Apply filter checks
        filter_config = self.sync_filter

        # Check selection mode filter
        if (filter_config.allowed_selection_modes and
            selection.criteria.mode not in filter_config.allowed_selection_modes):
            return False

        # Check selection size filters
        if selection.n_points < filter_config.min_selection_size:
            return False

        if (filter_config.max_selection_size and
            selection.n_points > filter_config.max_selection_size):
            return False

        # Check view type filter (would need view type info)
        target_view = self.registered_views[target_view_id]
        return not (filter_config.allowed_view_types and hasattr(target_view, "view_type") and target_view.view_type not in filter_config.allowed_view_types)

    def _transform_selection_for_view(self, selection: Selection,
                                    target_view_id: ViewID) -> Selection | None:
        """Transforma seleção para view alvo"""
        target_view = self.registered_views[target_view_id]

        # Let the target view transform the selection if it has custom logic
        if hasattr(target_view, "transform_synced_selection"):
            try:
                return target_view.transform_synced_selection(selection)
            except Exception as e:
                logger.exception("selection_transformation_failed",
                           target_view=target_view_id, error=str(e))
                return None

        # Default: return selection as-is
        return selection

    def _add_sync_event(self, event: SelectionSyncEvent):
        """Adiciona evento ao histórico"""
        self.sync_events.append(event)

        # Maintain history size
        if len(self.sync_events) > self.max_history_size:
            self.sync_events = self.sync_events[-self.max_history_size:]

    def get_sync_statistics(self) -> dict[str, Any]:
        """Retorna estatísticas de sincronização"""
        if not self.sync_events:
            return {"total_events": 0}

        recent_events = [e for e in self.sync_events
                        if time.time() - e.timestamp < 3600]  # Last hour

        total_events = len(self.sync_events)
        recent_events_count = len(recent_events)
        success_rate = sum(1 for e in self.sync_events if e.success) / total_events
        recent_success_rate = (sum(1 for e in recent_events if e.success) / recent_events_count
                              if recent_events_count > 0 else 0)

        return {
            "total_events": total_events,
            "recent_events": recent_events_count,
            "overall_success_rate": success_rate,
            "recent_success_rate": recent_success_rate,
            "registered_views": len(self.registered_views),
            "sync_mode": self.sync_mode.value,
        }

    def clear_sync_history(self):
        """Limpa histórico de sincronização"""
        self.sync_events.clear()


class SelectionSyncView:
    """
    Mixin para views que participam de sincronização de seleção

    Classes de view devem herdar deste mixin e implementar os métodos
    abstratos para participar da sincronização.
    """

    # Signals - devem ser definidos nas classes filhas
    selection_changed = pyqtSignal(object)  # Optional[Selection]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_selection: Selection | None = None
        self.sync_enabled = True

    def apply_synced_selection(self, selection: Selection):
        """
        Aplica seleção recebida via sincronização

        Override este método para implementar como a view
        deve aplicar seleções recebidas de outras views.
        """
        raise NotImplementedError("Subclasses must implement apply_synced_selection")

    def clear_synced_selection(self):
        """
        Limpa seleção sincronizada

        Override este método para implementar limpeza de seleção.
        """
        self.current_selection = None

    def transform_synced_selection(self, selection: Selection) -> Selection | None:
        """
        Transforma seleção para esta view

        Override este método para implementar transformações
        personalizadas de seleção para esta view.

        Returns:
            Selection transformada ou None se não aplicável
        """
        return selection  # Default: return as-is

    def emit_selection_changed(self, selection: Selection | None):
        """Emite sinal de mudança de seleção"""
        if not self.sync_enabled:
            return

        self.current_selection = selection
        self.selection_changed.emit(selection)

    def set_sync_enabled(self, enabled: bool):
        """Habilita/desabilita sincronização para esta view"""
        self.sync_enabled = enabled


class GlobalSelectionSynchronizer(QObject):
    """Sincronizador global de seleções"""

    def __init__(self, multi_view_sync: MultiViewSynchronizer | None = None):
        super().__init__()

        self.selection_sync = SelectionSynchronizer()
        self.multi_view_sync = multi_view_sync

        # Integrate with multi-view synchronizer if available
        if self.multi_view_sync:
            self._integrate_with_multi_view_sync()

    def _integrate_with_multi_view_sync(self):
        """Integra com sincronizador multi-view"""
        # Connect to multi-view synchronizer events
        self.multi_view_sync.view_registered.connect(self._on_view_registered)
        self.multi_view_sync.view_unregistered.connect(self._on_view_unregistered)

    @pyqtSlot(str)
    def _on_view_registered(self, view_id: ViewID):
        """Callback quando view é registrada no multi-view sync"""
        if view_id in self.multi_view_sync.views:
            view_info = self.multi_view_sync.views[view_id]
            view_widget = view_info.widget

            # Check if view supports selection sync
            if isinstance(view_widget, SelectionSyncView):
                self.selection_sync.register_view(view_id, view_widget)

    @pyqtSlot(str)
    def _on_view_unregistered(self, view_id: ViewID):
        """Callback quando view é removida do multi-view sync"""
        self.selection_sync.unregister_view(view_id)

    def get_selection_synchronizer(self) -> SelectionSynchronizer:
        """Retorna sincronizador de seleção"""
        return self.selection_sync


# Global instance
_global_selection_sync: GlobalSelectionSynchronizer | None = None


def get_global_selection_synchronizer(multi_view_sync: MultiViewSynchronizer | None = None) -> GlobalSelectionSynchronizer:
    """Retorna instância global do sincronizador"""
    global _global_selection_sync
    if _global_selection_sync is None:
        _global_selection_sync = GlobalSelectionSynchronizer(multi_view_sync)
    return _global_selection_sync


def cleanup_global_selection_synchronizer():
    """Limpa instância global"""
    global _global_selection_sync
    _global_selection_sync = None


# Utility functions for common synchronization patterns
def sync_temporal_selection_across_views(synchronizer: SelectionSynchronizer,
                                       source_view_id: ViewID,
                                       start_time: float,
                                       end_time: float) -> list[SelectionSyncEvent]:
    """Conveniência para sincronizar seleção temporal entre views"""

    # Create temporal selection criteria

    criteria = SelectionCriteria(
        mode=SelectionMode.TEMPORAL,
        start_time=start_time,
        end_time=end_time,
        description=f"Temporal sync: {start_time:.3f} - {end_time:.3f}s",
    )

    # Create mock selection (in real usage, would come from actual data)
    selection = Selection(
        t_seconds=np.array([]),
        series={},
        criteria=criteria,
        metadata={"sync_type": "temporal"},
    )

    return synchronizer.sync_selection_to_views(source_view_id, selection)


def create_selection_sync_filter(view_types: list[str] | None = None,
                                selection_modes: list[SelectionMode] | None = None,
                                min_size: int = 1,
                                max_size: int | None = None) -> SelectionSyncFilter:
    """Conveniência para criar filtro de sincronização"""
    return SelectionSyncFilter(
        allowed_view_types=set(view_types) if view_types else None,
        allowed_selection_modes=set(selection_modes) if selection_modes else None,
        min_selection_size=min_size,
        max_selection_size=max_size,
    )
