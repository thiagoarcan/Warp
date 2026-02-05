"""
MainWindow - Interface PyQt6 Unificada

Este módulo re-exporta a ModernMainWindow unificada para compatibilidade.

A versão unificada combina todas as funcionalidades:
- QDockWidget com painéis acopláveis (Data, Config, Operations, Streaming, Results)
- SessionState + SignalHub para comunicação entre componentes
- 5 temas visuais: Light, Dark, Ocean, Forest, Sunset
- Undo/Redo Manager completo
- ProcessingWorkerManager para operações assíncronas
- Toolbar horizontal com ícones intuitivos
- Sistema drag-and-drop para visualizações
- Tradução completa PT-BR
- Persistência de layout com QSettings
"""

from platform_base.ui.main_window_unified import ModernMainWindow, MainWindow

__all__ = ["ModernMainWindow", "MainWindow"]
