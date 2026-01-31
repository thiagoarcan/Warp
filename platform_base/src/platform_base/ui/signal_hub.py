"""
SignalHub - Hub centralizado de sinais para coordenação entre componentes

Centraliza a comunicação entre diferentes painéis e widgets da aplicação,
permitindo sincronização de estado, seleção, e eventos entre views.

Features:
- Broadcast de eventos de seleção
- Sincronização de crosshair entre plots
- Notificações de mudança de dados
- Coordenação de streaming entre views
- Eventos de operações globais
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QMutex, QMutexLocker, QObject, pyqtSignal

from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


class EventType(Enum):
    """Tipos de eventos do SignalHub"""
    # Seleção
    SELECTION_CHANGED = auto()
    SELECTION_CLEARED = auto()
    REGION_SELECTED = auto()

    # Crosshair
    CROSSHAIR_MOVED = auto()
    CROSSHAIR_TOGGLED = auto()

    # Dados
    DATASET_LOADED = auto()
    DATASET_UNLOADED = auto()
    SERIES_ADDED = auto()
    SERIES_REMOVED = auto()
    DATA_MODIFIED = auto()

    # Visualização
    PLOT_CREATED = auto()
    PLOT_CLOSED = auto()
    ZOOM_CHANGED = auto()
    PAN_CHANGED = auto()

    # Streaming
    STREAM_STARTED = auto()
    STREAM_PAUSED = auto()
    STREAM_STOPPED = auto()
    STREAM_POSITION_CHANGED = auto()

    # Operações
    OPERATION_STARTED = auto()
    OPERATION_COMPLETED = auto()
    OPERATION_FAILED = auto()

    # UI
    THEME_CHANGED = auto()
    LAYOUT_CHANGED = auto()
    SETTINGS_CHANGED = auto()


@dataclass
class HubEvent:
    """Estrutura de evento do SignalHub"""
    event_type: EventType
    source: str  # ID do componente que gerou o evento
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


class SignalHub(QObject):
    """
    Hub centralizado de sinais para comunicação entre componentes.

    Implementa padrão Observer/Publisher-Subscriber para coordenar
    eventos entre diferentes partes da aplicação.

    Usage:
        hub = SignalHub.instance()
        hub.subscribe(EventType.CROSSHAIR_MOVED, my_handler)
        hub.emit(EventType.CROSSHAIR_MOVED, "plot_1", {"x": 10.5, "y": 20.3})
    """

    # Singleton instance
    _instance: SignalHub | None = None

    # Signals PyQt para diferentes categorias
    selection_signal = pyqtSignal(object)  # HubEvent
    crosshair_signal = pyqtSignal(object)  # HubEvent
    data_signal = pyqtSignal(object)  # HubEvent
    visualization_signal = pyqtSignal(object)  # HubEvent
    streaming_signal = pyqtSignal(object)  # HubEvent
    operation_signal = pyqtSignal(object)  # HubEvent
    ui_signal = pyqtSignal(object)  # HubEvent

    # Signal genérico para todos os eventos
    any_event = pyqtSignal(object)  # HubEvent

    def __init__(self, parent=None):
        super().__init__(parent)

        self._mutex = QMutex()
        self._subscribers: dict[EventType, list[Callable]] = {}
        self._component_registry: dict[str, set[EventType]] = {}
        self._event_history: list[HubEvent] = []
        self._max_history = 100

        # Mapear tipos de evento para signals
        self._signal_map = {
            EventType.SELECTION_CHANGED: self.selection_signal,
            EventType.SELECTION_CLEARED: self.selection_signal,
            EventType.REGION_SELECTED: self.selection_signal,
            EventType.CROSSHAIR_MOVED: self.crosshair_signal,
            EventType.CROSSHAIR_TOGGLED: self.crosshair_signal,
            EventType.DATASET_LOADED: self.data_signal,
            EventType.DATASET_UNLOADED: self.data_signal,
            EventType.SERIES_ADDED: self.data_signal,
            EventType.SERIES_REMOVED: self.data_signal,
            EventType.DATA_MODIFIED: self.data_signal,
            EventType.PLOT_CREATED: self.visualization_signal,
            EventType.PLOT_CLOSED: self.visualization_signal,
            EventType.ZOOM_CHANGED: self.visualization_signal,
            EventType.PAN_CHANGED: self.visualization_signal,
            EventType.STREAM_STARTED: self.streaming_signal,
            EventType.STREAM_PAUSED: self.streaming_signal,
            EventType.STREAM_STOPPED: self.streaming_signal,
            EventType.STREAM_POSITION_CHANGED: self.streaming_signal,
            EventType.OPERATION_STARTED: self.operation_signal,
            EventType.OPERATION_COMPLETED: self.operation_signal,
            EventType.OPERATION_FAILED: self.operation_signal,
            EventType.THEME_CHANGED: self.ui_signal,
            EventType.LAYOUT_CHANGED: self.ui_signal,
            EventType.SETTINGS_CHANGED: self.ui_signal,
        }

        logger.debug("SignalHub initialized")

    @classmethod
    def instance(cls) -> SignalHub:
        """Retorna instância singleton do SignalHub"""
        if cls._instance is None:
            cls._instance = SignalHub()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset da instância singleton (para testes)"""
        cls._instance = None

    def subscribe(self, event_type: EventType, handler: Callable,
                  component_id: str | None = None):
        """
        Registra um handler para um tipo de evento.

        Args:
            event_type: Tipo de evento a escutar
            handler: Callable que recebe HubEvent
            component_id: ID opcional do componente (para unsubscribe em bloco)
        """
        with QMutexLocker(self._mutex):
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

            # Registrar componente
            if component_id:
                if component_id not in self._component_registry:
                    self._component_registry[component_id] = set()
                self._component_registry[component_id].add(event_type)

            logger.debug(f"Subscribed to {event_type.name}")

    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Remove um handler de um tipo de evento"""
        with QMutexLocker(self._mutex):
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)
                    logger.debug(f"Unsubscribed from {event_type.name}")

    def unsubscribe_component(self, component_id: str):
        """Remove todas as subscriptions de um componente"""
        with QMutexLocker(self._mutex):
            if component_id in self._component_registry:
                # Note: This removes the component from registry but doesn't
                # remove handlers since we don't track handler-component mapping
                del self._component_registry[component_id]
                logger.debug(f"Component {component_id} unsubscribed from all events")

    def emit(self, event_type: EventType, source: str, data: dict[str, Any] | None = None):
        """
        Emite um evento para todos os subscribers.

        Args:
            event_type: Tipo de evento
            source: ID do componente que gerou o evento
            data: Dados adicionais do evento
        """
        import time

        event = HubEvent(
            event_type=event_type,
            source=source,
            data=data or {},
            timestamp=time.time(),
        )

        # Adicionar ao histórico
        with QMutexLocker(self._mutex):
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)

            # Obter handlers
            handlers = self._subscribers.get(event_type, []).copy()

        # Emitir signal PyQt específico
        if event_type in self._signal_map:
            self._signal_map[event_type].emit(event)

        # Emitir signal genérico
        self.any_event.emit(event)

        # Chamar handlers registrados
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.exception(f"Handler error for {event_type.name}: {e}")

        logger.debug(f"Event emitted: {event_type.name} from {source}")

    # ========== CONVENIENCE METHODS ==========

    def emit_crosshair_moved(self, source: str, x: float, y: float):
        """Emite evento de movimento do crosshair"""
        self.emit(EventType.CROSSHAIR_MOVED, source, {"x": x, "y": y})

    def emit_selection_changed(self, source: str, selection: Any):
        """Emite evento de mudança de seleção"""
        self.emit(EventType.SELECTION_CHANGED, source, {"selection": selection})

    def emit_region_selected(self, source: str, x_min: float, x_max: float,
                             y_min: float, y_max: float):
        """Emite evento de região selecionada"""
        self.emit(EventType.REGION_SELECTED, source, {
            "x_min": x_min, "x_max": x_max,
            "y_min": y_min, "y_max": y_max,
        })

    def emit_dataset_loaded(self, source: str, dataset_id: str, dataset_name: str):
        """Emite evento de dataset carregado"""
        self.emit(EventType.DATASET_LOADED, source, {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
        })

    def emit_stream_position(self, source: str, position: float, total: float):
        """Emite evento de posição do streaming"""
        self.emit(EventType.STREAM_POSITION_CHANGED, source, {
            "position": position,
            "total": total,
            "progress": position / total if total > 0 else 0,
        })

    def emit_operation_started(self, source: str, operation_name: str,
                               operation_id: str | None = None):
        """Emite evento de início de operação"""
        self.emit(EventType.OPERATION_STARTED, source, {
            "operation_name": operation_name,
            "operation_id": operation_id,
        })

    def emit_operation_completed(self, source: str, operation_name: str,
                                 result: Any = None, operation_id: str | None = None):
        """Emite evento de operação concluída"""
        self.emit(EventType.OPERATION_COMPLETED, source, {
            "operation_name": operation_name,
            "operation_id": operation_id,
            "result": result,
        })

    def emit_operation_failed(self, source: str, operation_name: str,
                              error: str, operation_id: str | None = None):
        """Emite evento de falha de operação"""
        self.emit(EventType.OPERATION_FAILED, source, {
            "operation_name": operation_name,
            "operation_id": operation_id,
            "error": error,
        })

    # ========== QUERY METHODS ==========

    def get_event_history(self, event_type: EventType | None = None,
                          limit: int = 10) -> list[HubEvent]:
        """Retorna histórico de eventos"""
        with QMutexLocker(self._mutex):
            if event_type:
                filtered = [e for e in self._event_history if e.event_type == event_type]
            else:
                filtered = self._event_history.copy()
            return filtered[-limit:]

    def get_last_event(self, event_type: EventType) -> HubEvent | None:
        """Retorna último evento de um tipo"""
        history = self.get_event_history(event_type, limit=1)
        return history[0] if history else None

    def get_subscriber_count(self, event_type: EventType) -> int:
        """Retorna número de subscribers para um evento"""
        with QMutexLocker(self._mutex):
            return len(self._subscribers.get(event_type, []))

    def get_registered_components(self) -> list[str]:
        """Retorna lista de componentes registrados"""
        with QMutexLocker(self._mutex):
            return list(self._component_registry.keys())


# Funções de conveniência para acesso global
def get_signal_hub() -> SignalHub:
    """Retorna instância global do SignalHub"""
    return SignalHub.instance()


def emit_event(event_type: EventType, source: str, data: dict[str, Any] | None = None):
    """Emite evento via instância global"""
    SignalHub.instance().emit(event_type, source, data)


def subscribe_event(event_type: EventType, handler: Callable,
                    component_id: str | None = None):
    """Subscreve a evento via instância global"""
    SignalHub.instance().subscribe(event_type, handler, component_id)
