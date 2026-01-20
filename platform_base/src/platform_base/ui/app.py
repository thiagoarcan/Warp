"""
PyQt6 Desktop Application Entry Point - Platform Base v2.0

Implementa a aplicação desktop conforme especificação seção 12.1
"""

from __future__ import annotations

import sys
import signal
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont

from platform_base.core.dataset_store import DatasetStore
from platform_base.ui.main_window import MainWindow
from platform_base.ui.state import SessionState
from platform_base.utils.logging import get_logger, setup_logging
from platform_base.utils.errors import PlatformError

logger = get_logger(__name__)


class PlatformApplication(QApplication):
    """
    Aplicação principal PyQt6 conforme especificação seção 12.1
    
    Features:
    - Gerenciamento de janela única
    - Signal handling para shutdown graceful
    - Exception handling global
    - Splash screen
    """
    
    # Signal para shutdown graceful
    shutdown_requested = pyqtSignal()
    
    def __init__(self, argv: list[str]):
        super().__init__(argv)
        
        # Configuração básica
        self.setApplicationName("Platform Base")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("TRANSPETRO")
        self.setOrganizationDomain("transpetro.com.br")
        
        # Configurar fonte padrão
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        
        # State management
        self._dataset_store: Optional[DatasetStore] = None
        self._session_state: Optional[SessionState] = None
        self._main_window: Optional[MainWindow] = None
        self._splash: Optional[QSplashScreen] = None
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("platform_application_initialized", version="2.0.0")
    
    def _setup_signal_handlers(self):
        """Configura handlers para sinais do sistema"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Timer para processar sinais do sistema
        self._signal_timer = QTimer()
        self._signal_timer.timeout.connect(lambda: None)
        self._signal_timer.start(500)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais do sistema"""
        logger.info("shutdown_signal_received", signal=signum)
        self.shutdown_requested.emit()
    
    def initialize_components(self, cache_config: Optional[dict] = None) -> bool:
        """
        Inicializa componentes da aplicação
        
        Returns:
            True se inicialização bem-sucedida
        """
        try:
            logger.info("initializing_application_components")
            
            # Show splash screen
            self._show_splash()
            
            # Initialize dataset store
            self._dataset_store = DatasetStore(cache_config)
            self._update_splash("Inicializando gerenciador de dados...")
            
            # Initialize session state
            self._session_state = SessionState(self._dataset_store)
            self._update_splash("Configurando estado da sessão...")
            
            # Connect shutdown signal
            self.shutdown_requested.connect(self._graceful_shutdown)
            
            self._update_splash("Carregando interface principal...")
            
            logger.info("application_components_initialized")
            return True
            
        except Exception as e:
            logger.error("component_initialization_failed", error=str(e))
            self._show_error("Erro na Inicialização", 
                           f"Falha ao inicializar componentes da aplicação:\n{e}")
            return False
    
    def _show_splash(self):
        """Mostra splash screen"""
        # Criar splash simples (pode ser melhorado com imagem)
        pixmap = QPixmap(400, 200)
        pixmap.fill(Qt.GlobalColor.darkBlue)
        
        self._splash = QSplashScreen(pixmap)
        self._splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._splash.show()
        self._splash.showMessage(
            "Platform Base v2.0\nCarregando...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            Qt.GlobalColor.white
        )
        self.processEvents()
    
    def _update_splash(self, message: str):
        """Atualiza mensagem do splash screen"""
        if self._splash:
            self._splash.showMessage(
                f"Platform Base v2.0\n{message}",
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
                Qt.GlobalColor.white
            )
            self.processEvents()
    
    def _hide_splash(self):
        """Esconde splash screen"""
        if self._splash:
            self._splash.close()
            self._splash = None
    
    def create_main_window(self) -> bool:
        """
        Cria e configura janela principal
        
        Returns:
            True se criação bem-sucedida
        """
        try:
            if not self._session_state:
                raise PlatformError("Session state not initialized")
            
            self._update_splash("Criando janela principal...")
            
            # Create main window
            self._main_window = MainWindow(self._session_state)
            
            # Setup window
            self._main_window.setWindowIcon(self._get_app_icon())
            self._main_window.show()
            
            # Hide splash
            self._hide_splash()
            
            logger.info("main_window_created")
            return True
            
        except Exception as e:
            logger.error("main_window_creation_failed", error=str(e))
            self._show_error("Erro na Interface", 
                           f"Falha ao criar janela principal:\n{e}")
            return False
    
    def _get_app_icon(self) -> QIcon:
        """Obtém ícone da aplicação"""
        # Tentar carregar ícone se existir, senão usar ícone padrão
        icon_path = Path(__file__).parent / "assets" / "icon.png"
        if icon_path.exists():
            return QIcon(str(icon_path))
        else:
            # Usar ícone padrão do sistema
            return self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
    
    def _show_error(self, title: str, message: str):
        """Mostra diálogo de erro"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def _graceful_shutdown(self):
        """Shutdown graceful da aplicação"""
        logger.info("graceful_shutdown_started")
        
        try:
            # Save session if main window exists
            if self._main_window:
                self._main_window.save_session_on_exit()
            
            # Clear caches
            if self._dataset_store:
                self._dataset_store.clear_cache()
            
            logger.info("graceful_shutdown_completed")
            
        except Exception as e:
            logger.error("shutdown_error", error=str(e))
        
        finally:
            self.quit()
    
    def run(self) -> int:
        """
        Executa a aplicação
        
        Returns:
            Exit code
        """
        try:
            # Initialize components
            if not self.initialize_components():
                return 1
            
            # Create main window
            if not self.create_main_window():
                return 1
            
            # Run event loop
            logger.info("starting_application_event_loop")
            exit_code = self.exec()
            
            logger.info("application_exited", exit_code=exit_code)
            return exit_code
            
        except Exception as e:
            logger.error("application_run_failed", error=str(e))
            self._show_error("Erro Fatal", f"Erro inesperado na aplicação:\n{e}")
            return 1


def create_application(argv: Optional[list[str]] = None, 
                      cache_config: Optional[dict] = None) -> PlatformApplication:
    """
    Factory function para criar aplicação
    
    Args:
        argv: Argumentos da linha de comando
        cache_config: Configuração de cache
        
    Returns:
        Instância da aplicação configurada
    """
    if argv is None:
        argv = sys.argv
        
    app = PlatformApplication(argv)
    
    # Set high DPI support
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    return app


def main(argv: Optional[list[str]] = None) -> int:
    """
    Entry point principal da aplicação
    
    Args:
        argv: Argumentos da linha de comando
        
    Returns:
        Exit code
    """
    # Setup logging
    setup_logging()
    
    # Create and run application
    app = create_application(argv)
    return app.run()


def run():
    """Entry point for CLI command."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
