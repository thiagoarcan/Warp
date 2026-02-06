"""
DetachedManager - Gerenciador de painéis destacados

Rastreia e permite re-dock de todos os painéis QDockWidget destacados
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QDockWidget, QMainWindow


class DetachedManager(QObject):
    """
    Gerenciador de painéis destacados.
    
    Rastreia todos os QDockWidgets que foram destacados (floating)
    e permite re-docá-los de volta à janela principal.
    """
    
    detached_changed = pyqtSignal(int)  # Número de painéis destacados mudou
    
    def __init__(self, main_window: QMainWindow):
        super().__init__(main_window)
        self.main_window = main_window
        self._detached_docks: list[QDockWidget] = []
        
    def register_dock(self, dock: QDockWidget):
        """Registra um dock widget para monitoramento"""
        dock.topLevelChanged.connect(lambda floating: self._on_dock_floating_changed(dock, floating))
        
    def _on_dock_floating_changed(self, dock: QDockWidget, floating: bool):
        """Callback quando um dock widget muda seu estado floating"""
        if floating and dock not in self._detached_docks:
            self._detached_docks.append(dock)
            self.detached_changed.emit(len(self._detached_docks))
        elif not floating and dock in self._detached_docks:
            self._detached_docks.remove(dock)
            self.detached_changed.emit(len(self._detached_docks))
    
    def get_detached_count(self) -> int:
        """Retorna o número de painéis destacados"""
        return len(self._detached_docks)
    
    def get_detached_docks(self) -> list[QDockWidget]:
        """Retorna lista de painéis destacados"""
        return self._detached_docks.copy()
    
    def redock_all(self):
        """Re-doca todos os painéis destacados de volta à janela principal"""
        for dock in self._detached_docks.copy():
            if dock.isFloating():
                # Torna o dock não-floating (volta para a janela principal)
                dock.setFloating(False)
                # Força adição ao main window se necessário
                if not self.main_window.restoreDockWidget(dock):
                    # Se restore falhar, adiciona manualmente
                    from PyQt6.QtCore import Qt
                    self.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
        self._detached_docks.clear()
        self.detached_changed.emit(0)
