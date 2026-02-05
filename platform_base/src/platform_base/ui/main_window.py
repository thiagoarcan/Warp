"""
MainWindow - Interface PyQt6

Este módulo re-exporta a MainWindow funcional do módulo desktop.
A implementação principal está em platform_base.desktop.main_window.

Funcionalidades:
- QDockWidget com painéis acopláveis (Data, Config, Operations, Streaming, Results)
- SessionState + SignalHub para comunicação entre componentes
- Undo/Redo Manager completo
- ProcessingWorkerManager para operações assíncronas
- Toolbar e menus completos
- Interface carregada de mainWindow.ui
- Tradução completa PT-BR
- Persistência de layout com QSettings
"""

from platform_base.desktop.main_window import MainWindow

__all__ = ["MainWindow"]
