from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from platform_base.core.dataset_store import DatasetStore
from platform_base.core.models import ViewID, SessionID
from platform_base.viz.streaming import StreamingEngine
from platform_base.caching.memory import MemoryCache
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class Selection(BaseModel):
    """Seleção de dados conforme PRD seção 13"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Método 1: Temporal (range)
    time_range: Optional[tuple[float, float]] = None
    
    # Método 2: Interativo (clique/arrasto no gráfico)
    interactive_points: Optional[list[int]] = None
    
    # Método 3: Condicional (query-like)
    predicates: Optional[list[Dict[str, Any]]] = None
    
    # Combinação (AND/OR)
    combination: str = "and"


class CacheManager(BaseModel):
    """Gerenciador de cache multi-nível"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    memory_cache: MemoryCache = Field(default_factory=MemoryCache)
    disk_enabled: bool = True
    disk_path: str = ".cache"


class AppState(BaseModel):
    """Estado centralizado da aplicação conforme PRD seção 12.3"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # DatasetStore principal
    datasets: DatasetStore = Field(default_factory=DatasetStore)
    
    # Sessões de streaming (não global)
    streaming_sessions: dict[SessionID, StreamingEngine] = Field(default_factory=dict)
    
    # Subscrições de views para sincronização
    view_subscriptions: dict[ViewID, SessionID] = Field(default_factory=dict)
    
    # Seleções por view
    ui_selections: dict[ViewID, Selection] = Field(default_factory=dict)
    
    # Cache manager
    cache: CacheManager = Field(default_factory=CacheManager)
    
    def sync_callback(self, session_id: SessionID) -> None:
        """
        Callback de sincronização conforme PRD seção 11.3
        
        Chamado a cada tick:
        1. Atualiza current_time_index no StreamingEngine
        2. Notifica todas views subscritas via Dash callback
        3. Views recalculam janela e re-renderizam
        """
        if session_id not in self.streaming_sessions:
            logger.warning("sync_callback_unknown_session", session_id=session_id)
            return
            
        engine = self.streaming_sessions[session_id]
        update = engine.tick()
        
        # Encontra views subscritas a esta sessão
        subscribed_views = [
            view_id for view_id, sess_id in self.view_subscriptions.items()
            if sess_id == session_id
        ]
        
        logger.info("sync_callback_tick",
                   session_id=session_id,
                   current_time_index=update.current_time_index,
                   subscribed_views=len(subscribed_views))
        
        # Notificações para views seriam implementadas aqui
        # usando callbacks do Dash
        
    def add_streaming_session(self, session_id: SessionID, engine: StreamingEngine) -> None:
        """Adiciona nova sessão de streaming"""
        self.streaming_sessions[session_id] = engine
        logger.info("streaming_session_added", session_id=session_id)
        
    def subscribe_view(self, view_id: ViewID, session_id: SessionID) -> None:
        """Subscreve view para receber updates de sessão"""
        self.view_subscriptions[view_id] = session_id
        logger.info("view_subscribed", view_id=view_id, session_id=session_id)
        
    def unsubscribe_view(self, view_id: ViewID) -> None:
        """Remove subscrição de view"""
        if view_id in self.view_subscriptions:
            session_id = self.view_subscriptions.pop(view_id)
            logger.info("view_unsubscribed", view_id=view_id, session_id=session_id)
            
    def set_selection(self, view_id: ViewID, selection: Selection) -> None:
        """Define seleção para uma view"""
        self.ui_selections[view_id] = selection
        logger.info("selection_updated", view_id=view_id)
        
    def get_selection(self, view_id: ViewID) -> Optional[Selection]:
        """Obtém seleção de uma view"""
        return self.ui_selections.get(view_id)
        
    def clear_cache(self) -> None:
        """Limpa todos os caches"""
        self.cache.memory_cache.clear()
        logger.info("cache_cleared")


# Singleton global para estado da aplicação
# Sincronização: Dash Store (client) <-> AppState (server) <-> DatasetStore (persistence)
_app_state: Optional[AppState] = None


def get_app_state() -> AppState:
    """Obtém instância singleton do estado da aplicação"""
    global _app_state
    if _app_state is None:
        _app_state = AppState()
        logger.info("app_state_initialized")
    return _app_state


def reset_app_state() -> None:
    """Reseta o estado da aplicação (usado em testes)"""
    global _app_state
    _app_state = None
    logger.info("app_state_reset")
