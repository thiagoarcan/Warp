"""
Resource Manager - Gerenciador de recursos para evitar memory leaks

Funcionalidades:
- Cleanup de figuras matplotlib
- Liberação de recursos em close events
- Registro e tracking de recursos
- Garbage collection controlado
"""

from __future__ import annotations

import gc
import weakref
from typing import Any, Callable, Dict, List, Optional, Set

from PyQt6.QtCore import QObject, pyqtSignal

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class ResourceTracker:
    """
    Rastreador de recursos para debugging de memory leaks
    """
    
    def __init__(self):
        self._resources: Dict[str, weakref.WeakSet] = {}
        self._cleanup_funcs: Dict[str, List[Callable]] = {}
    
    def register(self, category: str, resource: Any) -> None:
        """
        Registra um recurso para tracking
        
        Args:
            category: Categoria do recurso (ex: 'figure', 'worker', 'canvas')
            resource: Objeto a ser rastreado
        """
        if category not in self._resources:
            self._resources[category] = weakref.WeakSet()
        
        self._resources[category].add(resource)
        logger.debug(f"Resource registered: {category}, total={len(self._resources[category])}")
    
    def unregister(self, category: str, resource: Any) -> None:
        """Remove recurso do tracking"""
        if category in self._resources:
            self._resources[category].discard(resource)
    
    def get_count(self, category: Optional[str] = None) -> Dict[str, int]:
        """
        Retorna contagem de recursos por categoria
        
        Args:
            category: Categoria específica ou None para todas
        
        Returns:
            Dicionário com contagens
        """
        if category:
            return {category: len(self._resources.get(category, []))}
        return {k: len(v) for k, v in self._resources.items()}
    
    def add_cleanup_func(self, category: str, func: Callable) -> None:
        """Adiciona função de cleanup para categoria"""
        if category not in self._cleanup_funcs:
            self._cleanup_funcs[category] = []
        self._cleanup_funcs[category].append(func)
    
    def cleanup_category(self, category: str) -> int:
        """
        Executa cleanup de categoria específica
        
        Returns:
            Número de recursos limpos
        """
        count = 0
        
        # Executar funções de cleanup registradas
        for func in self._cleanup_funcs.get(category, []):
            try:
                func()
            except Exception as e:
                logger.error(f"Cleanup function error: {e}")
        
        # Limpar referências
        if category in self._resources:
            count = len(self._resources[category])
            self._resources[category] = weakref.WeakSet()
        
        logger.info(f"Cleanup completed for {category}: {count} resources")
        return count
    
    def cleanup_all(self) -> Dict[str, int]:
        """Executa cleanup de todas as categorias"""
        results = {}
        for category in list(self._resources.keys()):
            results[category] = self.cleanup_category(category)
        return results


class MatplotlibResourceManager:
    """
    Gerenciador específico para recursos matplotlib
    
    Evita memory leaks causados por:
    - Figuras não fechadas
    - Axes não removidos
    - Event handlers não desconectados
    """
    
    _instance: Optional["MatplotlibResourceManager"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._figures: weakref.WeakSet = weakref.WeakSet()
        self._canvases: weakref.WeakSet = weakref.WeakSet()
        
        logger.debug("MatplotlibResourceManager initialized")
    
    def register_figure(self, fig) -> None:
        """Registra figura para tracking"""
        self._figures.add(fig)
        logger.debug(f"Figure registered, total={len(self._figures)}")
    
    def register_canvas(self, canvas) -> None:
        """Registra canvas para tracking"""
        self._canvases.add(canvas)
    
    def close_figure(self, fig) -> None:
        """
        Fecha figura corretamente liberando recursos
        
        Args:
            fig: Figura matplotlib
        """
        try:
            import matplotlib.pyplot as plt

            # Desconectar event handlers
            if hasattr(fig, 'canvas') and fig.canvas:
                fig.canvas.mpl_disconnect('all')
            
            # Limpar axes
            for ax in fig.axes:
                ax.clear()
            
            # Fechar figura
            plt.close(fig)
            
            # Remover do tracking
            self._figures.discard(fig)
            
            logger.debug("Figure closed and cleaned up")
        except Exception as e:
            logger.error(f"Error closing figure: {e}")
    
    def cleanup_all_figures(self) -> int:
        """
        Fecha todas as figuras rastreadas
        
        Returns:
            Número de figuras fechadas
        """
        import matplotlib.pyplot as plt
        
        count = 0
        
        # Fechar figuras rastreadas
        for fig in list(self._figures):
            try:
                self.close_figure(fig)
                count += 1
            except Exception:
                pass
        
        # Fechar todas as figuras restantes
        plt.close('all')
        
        # Forçar garbage collection
        gc.collect()
        
        logger.info(f"Matplotlib cleanup: {count} figures closed")
        return count
    
    def get_figure_count(self) -> int:
        """Retorna número de figuras ativas"""
        import matplotlib.pyplot as plt
        return len(plt.get_fignums())
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Retorna informações de uso de memória matplotlib
        
        Returns:
            Dicionário com estatísticas
        """
        import matplotlib.pyplot as plt
        
        return {
            'active_figures': len(plt.get_fignums()),
            'tracked_figures': len(self._figures),
            'tracked_canvases': len(self._canvases),
        }


class CloseEventHandler(QObject):
    """
    Handler para eventos de close de widgets
    
    Garante limpeza adequada de recursos quando widgets são fechados
    """
    
    cleanup_completed = pyqtSignal()
    
    def __init__(self, widget, cleanup_func: Optional[Callable] = None):
        super().__init__(widget)
        
        self._widget = weakref.ref(widget)
        self._cleanup_func = cleanup_func
        self._cleaned = False
        
        # Instalar event filter
        if widget:
            widget.installEventFilter(self)
    
    def eventFilter(self, a0, a1) -> bool:
        """Intercepta eventos de close"""
        from PyQt6.QtCore import QEvent
        
        if a1 is not None and a1.type() == QEvent.Type.Close:
            self.cleanup()
        
        return super().eventFilter(a0, a1)
    
    def cleanup(self) -> None:
        """Executa cleanup"""
        if self._cleaned:
            return
        
        self._cleaned = True
        
        try:
            # Executar função de cleanup customizada
            if self._cleanup_func:
                self._cleanup_func()
            
            # Cleanup padrão
            widget = self._widget()
            if widget:
                # Se widget tem figuras matplotlib
                if hasattr(widget, 'figure'):
                    get_matplotlib_manager().close_figure(widget.figure)
                
                # Se widget tem canvas
                if hasattr(widget, 'canvas'):
                    canvas = widget.canvas
                    if hasattr(canvas, 'close'):
                        canvas.close()
            
            self.cleanup_completed.emit()
            logger.debug("CloseEventHandler cleanup completed")
            
        except Exception as e:
            logger.error(f"CloseEventHandler cleanup error: {e}")


def get_resource_tracker() -> ResourceTracker:
    """Retorna instância global do ResourceTracker"""
    global _resource_tracker
    if '_resource_tracker' not in globals():
        _resource_tracker = ResourceTracker()
    return _resource_tracker


def get_matplotlib_manager() -> MatplotlibResourceManager:
    """Retorna instância singleton do MatplotlibResourceManager"""
    return MatplotlibResourceManager()


def cleanup_on_close(widget, cleanup_func: Optional[Callable] = None) -> CloseEventHandler:
    """
    Decorator/função para garantir cleanup no close de widget
    
    Args:
        widget: Widget PyQt
        cleanup_func: Função de cleanup customizada (opcional)
    
    Returns:
        CloseEventHandler configurado
    
    Example:
        handler = cleanup_on_close(my_widget, lambda: my_cleanup())
    """
    return CloseEventHandler(widget, cleanup_func)


def force_cleanup() -> Dict[str, Any]:
    """
    Força cleanup de todos os recursos
    
    Returns:
        Estatísticas de cleanup
    """
    results = {
        'matplotlib': get_matplotlib_manager().cleanup_all_figures(),
        'resources': get_resource_tracker().cleanup_all(),
        'gc_collected': gc.collect(),
    }
    
    logger.info(f"Force cleanup completed: {results}")
    return results
