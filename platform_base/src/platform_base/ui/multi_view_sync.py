"""
Multi-View Synchronization - Sistema de sincronização entre múltiplas views conforme seção 11.4

Features:
- Sincronização temporal entre views
- Coordenação de QTimers
- Broadcast de updates para views subscribes
- Gestão de view lifecycle
- Sincronização de seleção entre views
"""

from __future__ import annotations

from typing import Dict, List, Optional, Callable, Any, Set
from datetime import timedelta
import time
from dataclasses import dataclass, field
from enum import Enum

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget

from platform_base.viz.streaming import StreamingEngine, TickUpdate, ViewSubscription
from platform_base.core.models import ViewID, Dataset
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class SyncMode(Enum):
    """Modos de sincronização multi-view"""
    INDEPENDENT = "independent"  # Views independentes
    TEMPORAL = "temporal"        # Sincronização temporal
    SELECTION = "selection"      # Sincronização de seleção
    FULL = "full"               # Sincronização completa


@dataclass
class ViewInfo:
    """Informações de uma view registrada"""
    view_id: ViewID
    widget: QWidget
    streaming_engine: Optional[StreamingEngine] = None
    sync_enabled: bool = True
    last_update_time: float = 0.0
    update_count: int = 0


@dataclass
class SyncState:
    """Estado de sincronização global"""
    current_time_index: int = 0
    current_time_seconds: float = 0.0
    is_playing: bool = False
    speed: float = 1.0
    sync_mode: SyncMode = SyncMode.TEMPORAL
    master_view_id: Optional[ViewID] = None


class MultiViewSynchronizer(QObject):
    """
    Sincronizador multi-view conforme seção 11.4
    
    Coordena sincronização temporal e de seleção entre múltiplas views,
    garantindo que todas as views estejam alinhadas durante streaming.
    """
    
    # Signals
    sync_update = pyqtSignal(object)  # TickUpdate
    view_registered = pyqtSignal(str)  # view_id
    view_unregistered = pyqtSignal(str)  # view_id
    sync_mode_changed = pyqtSignal(object)  # SyncMode
    master_changed = pyqtSignal(str)  # master_view_id
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # View registry
        self.views: Dict[ViewID, ViewInfo] = {}
        self.sync_state = SyncState()
        
        # Master timer for coordinated updates
        self.master_timer = QTimer()
        self.master_timer.timeout.connect(self._on_master_tick)
        self.master_timer.setSingleShot(False)
        
        # Performance tracking
        self.sync_stats = {
            'total_updates': 0,
            'avg_update_time': 0.0,
            'max_views_synced': 0
        }
        
        logger.info("multi_view_synchronizer_initialized")
    
    def register_view(self, view_id: ViewID, widget: QWidget, 
                     streaming_engine: Optional[StreamingEngine] = None) -> None:
        """
        Registra uma nova view para sincronização
        
        Args:
            view_id: ID único da view
            widget: Widget da view
            streaming_engine: Engine de streaming (opcional)
        """
        if view_id in self.views:
            logger.warning("view_already_registered", view_id=view_id)
            return
        
        view_info = ViewInfo(
            view_id=view_id,
            widget=widget,
            streaming_engine=streaming_engine,
            last_update_time=time.perf_counter()
        )
        
        self.views[view_id] = view_info
        
        # Se é a primeira view, torna-se master
        if len(self.views) == 1:
            self.sync_state.master_view_id = view_id
            self.master_changed.emit(view_id)
        
        # Configure streaming engine callback
        if streaming_engine:
            streaming_engine.add_sync_callback(self._on_view_update)
        
        self.view_registered.emit(view_id)
        logger.info("view_registered", view_id=view_id, total_views=len(self.views))
    
    def unregister_view(self, view_id: ViewID) -> None:
        """Remove view da sincronização"""
        if view_id not in self.views:
            return
        
        # Se era master, elege nova master
        if self.sync_state.master_view_id == view_id:
            remaining_views = [vid for vid in self.views.keys() if vid != view_id]
            if remaining_views:
                self.sync_state.master_view_id = remaining_views[0]
                self.master_changed.emit(self.sync_state.master_view_id)
            else:
                self.sync_state.master_view_id = None
        
        del self.views[view_id]
        
        self.view_unregistered.emit(view_id)
        logger.info("view_unregistered", view_id=view_id, remaining_views=len(self.views))
    
    def set_sync_mode(self, mode: SyncMode) -> None:
        """Define modo de sincronização"""
        old_mode = self.sync_state.sync_mode
        self.sync_state.sync_mode = mode
        
        if mode == SyncMode.INDEPENDENT:
            self._stop_master_timer()
        elif mode in [SyncMode.TEMPORAL, SyncMode.FULL]:
            self._start_master_timer()
        
        self.sync_mode_changed.emit(mode)
        logger.info("sync_mode_changed", old_mode=old_mode.value, new_mode=mode.value)
    
    def set_master_view(self, view_id: ViewID) -> None:
        """Define view master para sincronização"""
        if view_id not in self.views:
            logger.warning("invalid_master_view", view_id=view_id)
            return
        
        old_master = self.sync_state.master_view_id
        self.sync_state.master_view_id = view_id
        
        self.master_changed.emit(view_id)
        logger.info("master_view_changed", old_master=old_master, new_master=view_id)
    
    def start_sync_playback(self, interval_ms: int = 100) -> None:
        """Inicia playback sincronizado"""
        if self.sync_state.sync_mode == SyncMode.INDEPENDENT:
            logger.warning("cannot_start_sync_independent_mode")
            return
        
        self.sync_state.is_playing = True
        
        # Configure all streaming engines
        for view_info in self.views.values():
            if view_info.streaming_engine and view_info.sync_enabled:
                view_info.streaming_engine.play()
        
        # Start master timer
        self.master_timer.start(interval_ms)
        
        logger.info("sync_playback_started", interval_ms=interval_ms, n_views=len(self.views))
    
    def pause_sync_playback(self) -> None:
        """Pausa playback sincronizado"""
        self.sync_state.is_playing = False
        
        # Pause all streaming engines
        for view_info in self.views.values():
            if view_info.streaming_engine and view_info.sync_enabled:
                view_info.streaming_engine.pause()
        
        # Stop master timer
        self.master_timer.stop()
        
        logger.info("sync_playback_paused")
    
    def stop_sync_playback(self) -> None:
        """Para playback sincronizado"""
        self.sync_state.is_playing = False
        self.sync_state.current_time_index = 0
        self.sync_state.current_time_seconds = 0.0
        
        # Stop all streaming engines
        for view_info in self.views.values():
            if view_info.streaming_engine and view_info.sync_enabled:
                view_info.streaming_engine.stop()
        
        # Stop master timer
        self.master_timer.stop()
        
        logger.info("sync_playback_stopped")
    
    def seek_all_views(self, time_seconds: float) -> None:
        """Faz seek em todas as views sincronizadas"""
        self.sync_state.current_time_seconds = time_seconds
        
        updates = []
        for view_info in self.views.values():
            if view_info.streaming_engine and view_info.sync_enabled:
                view_info.streaming_engine.seek(time_seconds)
                update = view_info.streaming_engine._current_update()
                updates.append((view_info.view_id, update))
        
        # Broadcast seeks
        for view_id, update in updates:
            self._broadcast_update_to_others(view_id, update)
        
        logger.info("seek_all_views", time_seconds=time_seconds, n_views=len(updates))
    
    def sync_selection(self, source_view_id: ViewID, selection_data: Any) -> None:
        """Sincroniza seleção entre views"""
        if self.sync_state.sync_mode not in [SyncMode.SELECTION, SyncMode.FULL]:
            return
        
        # Broadcast selection to other views
        for view_id, view_info in self.views.items():
            if view_id != source_view_id and view_info.sync_enabled:
                # Call selection sync on target view
                if hasattr(view_info.widget, 'sync_selection'):
                    try:
                        view_info.widget.sync_selection(selection_data)
                    except Exception as e:
                        logger.error("selection_sync_failed", 
                                   source_view=source_view_id,
                                   target_view=view_id,
                                   error=str(e))
        
        logger.debug("selection_synced", source_view=source_view_id, n_targets=len(self.views)-1)
    
    def set_view_sync_enabled(self, view_id: ViewID, enabled: bool) -> None:
        """Habilita/desabilita sincronização para view específica"""
        if view_id in self.views:
            self.views[view_id].sync_enabled = enabled
            logger.info("view_sync_toggled", view_id=view_id, enabled=enabled)
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de sincronização"""
        active_views = sum(1 for v in self.views.values() if v.sync_enabled)
        
        return {
            'total_views': len(self.views),
            'active_views': active_views,
            'sync_mode': self.sync_state.sync_mode.value,
            'master_view': self.sync_state.master_view_id,
            'is_playing': self.sync_state.is_playing,
            'current_time': self.sync_state.current_time_seconds,
            **self.sync_stats
        }
    
    @pyqtSlot()
    def _on_master_tick(self) -> None:
        """Master timer tick - coordena updates de todas as views"""
        if not self.sync_state.is_playing:
            return
        
        start_time = time.perf_counter()
        
        # Get master view update
        master_update = None
        master_view = self.views.get(self.sync_state.master_view_id)
        
        if master_view and master_view.streaming_engine and master_view.sync_enabled:
            master_update = master_view.streaming_engine.tick()
            self.sync_state.current_time_index = master_update.current_time_index
            self.sync_state.current_time_seconds = master_update.current_time_seconds
        
        # Sync all other views to master time
        synced_views = 0
        for view_id, view_info in self.views.items():
            if (view_id != self.sync_state.master_view_id and 
                view_info.streaming_engine and 
                view_info.sync_enabled):
                
                try:
                    # Seek to master time and get update
                    view_info.streaming_engine.seek(self.sync_state.current_time_seconds)
                    update = view_info.streaming_engine._current_update()
                    
                    # Update view stats
                    view_info.last_update_time = time.perf_counter()
                    view_info.update_count += 1
                    synced_views += 1
                    
                except Exception as e:
                    logger.error("view_sync_failed", view_id=view_id, error=str(e))
        
        # Broadcast master update
        if master_update:
            self.sync_update.emit(master_update)
        
        # Update performance stats
        duration = time.perf_counter() - start_time
        self.sync_stats['total_updates'] += 1
        self.sync_stats['avg_update_time'] = (
            (self.sync_stats['avg_update_time'] * (self.sync_stats['total_updates'] - 1) + duration) /
            self.sync_stats['total_updates']
        )
        self.sync_stats['max_views_synced'] = max(self.sync_stats['max_views_synced'], synced_views)
        
        logger.debug("master_tick_completed", 
                    synced_views=synced_views,
                    duration_ms=duration * 1000,
                    current_time=self.sync_state.current_time_seconds)
    
    def _on_view_update(self, update: TickUpdate) -> None:
        """Callback quando view individual tem update"""
        # In independent mode, broadcast all updates
        if self.sync_state.sync_mode == SyncMode.INDEPENDENT:
            self.sync_update.emit(update)
        
        # In synchronized modes, only master triggers broadcasts
        # (handled in _on_master_tick)
    
    def _broadcast_update_to_others(self, source_view_id: ViewID, update: TickUpdate) -> None:
        """Broadcasts update para outras views"""
        for view_id, view_info in self.views.items():
            if view_id != source_view_id and view_info.sync_enabled:
                if hasattr(view_info.widget, 'on_sync_update'):
                    try:
                        view_info.widget.on_sync_update(update)
                    except Exception as e:
                        logger.error("broadcast_update_failed",
                                   source_view=source_view_id,
                                   target_view=view_id,
                                   error=str(e))
    
    def _start_master_timer(self) -> None:
        """Inicia master timer se necessário"""
        if self.sync_state.is_playing and not self.master_timer.isActive():
            self.master_timer.start(100)  # 100ms default
    
    def _stop_master_timer(self) -> None:
        """Para master timer"""
        if self.master_timer.isActive():
            self.master_timer.stop()


class ViewSyncMixin:
    """
    Mixin para widgets que participam de sincronização multi-view
    
    Adicione este mixin às suas view classes para participar da sincronização.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._view_id: Optional[ViewID] = None
        self._synchronizer: Optional[MultiViewSynchronizer] = None
    
    def register_with_synchronizer(self, synchronizer: MultiViewSynchronizer, 
                                 view_id: ViewID, 
                                 streaming_engine: Optional[StreamingEngine] = None) -> None:
        """Registra esta view com o sincronizador"""
        self._synchronizer = synchronizer
        self._view_id = view_id
        synchronizer.register_view(view_id, self, streaming_engine)
    
    def unregister_from_synchronizer(self) -> None:
        """Remove registro do sincronizador"""
        if self._synchronizer and self._view_id:
            self._synchronizer.unregister_view(self._view_id)
            self._synchronizer = None
            self._view_id = None
    
    def on_sync_update(self, update: TickUpdate) -> None:
        """Override este método para receber updates sincronizados"""
        pass
    
    def sync_selection(self, selection_data: Any) -> None:
        """Override este método para receber sincronização de seleção"""
        pass
    
    def emit_selection_change(self, selection_data: Any) -> None:
        """Chame este método quando seleção mudar para broadcast"""
        if self._synchronizer and self._view_id:
            self._synchronizer.sync_selection(self._view_id, selection_data)


# Global synchronizer instance
_global_synchronizer: Optional[MultiViewSynchronizer] = None


def get_global_synchronizer() -> MultiViewSynchronizer:
    """Retorna instância global do sincronizador"""
    global _global_synchronizer
    if _global_synchronizer is None:
        _global_synchronizer = MultiViewSynchronizer()
    return _global_synchronizer


def cleanup_global_synchronizer() -> None:
    """Limpa instância global (para shutdown da aplicação)"""
    global _global_synchronizer
    if _global_synchronizer:
        _global_synchronizer.stop_sync_playback()
        _global_synchronizer = None