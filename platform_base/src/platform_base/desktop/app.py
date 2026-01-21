"""
PyQt6 Desktop Application Entry Point - Platform Base v2.0

Main application class implementing the desktop interface.
Replaces Dash web interface with native PyQt6 desktop application.
"""

from __future__ import annotations

import sys
import signal
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QStandardPaths
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPalette

from platform_base.core.dataset_store import DatasetStore
from platform_base.desktop.main_window import MainWindow
from platform_base.desktop.session_state import SessionState
from platform_base.desktop.signal_hub import SignalHub
from platform_base.utils.logging import get_logger, setup_logging
from platform_base.utils.errors import PlatformError

logger = get_logger(__name__)


class PlatformApplication(QApplication):
    """
    Main PyQt6 application class.
    
    Features:
    - Single window management
    - Graceful shutdown signal handling
    - Global exception handling
    - Splash screen
    - HiDPI support
    - Theme detection
    """
    
    # Application-wide signals
    shutdown_requested = pyqtSignal()
    
    def __init__(self, argv: list[str]):
        super().__init__(argv)
        
        # Basic application configuration
        self.setApplicationName("Platform Base")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("TRANSPETRO")
        self.setOrganizationDomain("transpetro.com.br")
        self.setApplicationDisplayName("Platform Base - Time Series Analysis")
        
        # Set application icon
        self.setWindowIcon(self._get_app_icon())
        
        # Configure default font
        self._setup_default_font()
        
        # Enable HiDPI support
        self._setup_hidpi_support()
        
        # Detect and apply theme
        self._setup_theme()
        
        # Initialize core components
        self._dataset_store: Optional[DatasetStore] = None
        self._session_state: Optional[SessionState] = None
        self._signal_hub: Optional[SignalHub] = None
        self._main_window: Optional[MainWindow] = None
        self._splash: Optional[QSplashScreen] = None
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("platform_application_initialized", version="2.0.0")
    
    def _setup_default_font(self):
        """Configure default application font"""
        if sys.platform == "win32":
            font = QFont("Segoe UI", 9)
        elif sys.platform == "darwin":
            font = QFont("SF Pro Display", 13)
        else:  # Linux
            font = QFont("Ubuntu", 10)
        
        self.setFont(font)
        logger.debug("default_font_configured", 
                    family=font.family(), size=font.pointSize())
    
    def _setup_hidpi_support(self):
        """Configure HiDPI support"""
        try:
            # PyQt6 automatically handles HiDPI scaling, but we can still set some attributes
            if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
                self.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            
            if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
                self.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            
            # Set device pixel ratio policy if available
            if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
                self.setHighDpiScaleFactorRoundingPolicy(
                    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
                )
            
            logger.debug("hidpi_support_configured")
            
        except AttributeError as e:
            # HiDPI attributes may not be available in this PyQt6 version
            logger.warning("hidpi_attributes_not_available", error=str(e))
            # PyQt6 handles HiDPI automatically, so this is not critical
    
    def _setup_theme(self):
        """Setup application theme"""
        # Detect system theme
        palette = self.palette()
        is_dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
        
        theme = "dark" if is_dark else "light"
        logger.info("system_theme_detected", theme=theme)
        
        # Apply theme-specific configurations
        if is_dark:
            self.setStyleSheet(self._get_dark_stylesheet())
        else:
            self.setStyleSheet(self._get_light_stylesheet())
    
    def _get_dark_stylesheet(self) -> str:
        """Get dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QDockWidget {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QTreeWidget {
            background-color: #404040;
            color: #ffffff;
            alternate-background-color: #4a4a4a;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        """
    
    def _get_light_stylesheet(self) -> str:
        """Get light theme stylesheet"""
        return """
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        """
    
    def _get_app_icon(self) -> QIcon:
        """Get application icon"""
        # Try to load icon from resources
        icon_paths = [
            Path(__file__).parent / "resources" / "icons" / "app_icon.png",
            Path(__file__).parent.parent / "ui" / "assets" / "icon.png",
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                return QIcon(str(icon_path))
        
        # Use system default icon
        return self.style().standardIcon(
            self.style().StandardPixmap.SP_ComputerIcon
        )
    
    def _setup_signal_handlers(self):
        """Configure system signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Timer to process system signals
        self._signal_timer = QTimer()
        self._signal_timer.timeout.connect(lambda: None)
        self._signal_timer.start(500)  # Check every 500ms
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info("shutdown_signal_received", signal=signum)
        self.shutdown_requested.emit()
    
    def initialize_components(self, cache_config: Optional[dict] = None) -> bool:
        """
        Initialize application components.
        
        Args:
            cache_config: Cache configuration
            
        Returns:
            True if initialization successful
        """
        try:
            logger.info("initializing_application_components")
            
            # Show splash screen
            self._show_splash()
            
            # Initialize dataset store
            self._update_splash("Inicializando gerenciador de dados...")
            self._dataset_store = DatasetStore(cache_config)
            
            # Initialize signal hub
            self._update_splash("Configurando sistema de comunicação...")
            self._signal_hub = SignalHub()
            
            # Initialize session state
            self._update_splash("Configurando estado da sessão...")
            self._session_state = SessionState(self._dataset_store)
            
            # Connect shutdown signal
            self.shutdown_requested.connect(self._graceful_shutdown)
            
            self._update_splash("Carregando interface principal...")
            
            logger.info("application_components_initialized")
            return True
            
        except Exception as e:
            logger.error("component_initialization_failed", error=str(e))
            self._show_error("Erro na Inicialização", 
                           f"Falha ao inicializar componentes da aplicação:\\n{e}")
            return False
    
    def _show_splash(self):
        """Show splash screen"""
        # Create simple splash screen
        pixmap = QPixmap(400, 200)
        pixmap.fill(Qt.GlobalColor.darkBlue)
        
        self._splash = QSplashScreen(pixmap)
        self._splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._splash.show()
        self._splash.showMessage(
            "Platform Base v2.0\\nCarregando...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            Qt.GlobalColor.white
        )
        self.processEvents()
    
    def _update_splash(self, message: str):
        """Update splash screen message"""
        if self._splash:
            self._splash.showMessage(
                f"Platform Base v2.0\\n{message}",
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
                Qt.GlobalColor.white
            )
            self.processEvents()
    
    def _hide_splash(self):
        """Hide splash screen"""
        if self._splash:
            self._splash.close()
            self._splash = None
    
    def create_main_window(self) -> bool:
        """
        Create and configure main window.
        
        Returns:
            True if creation successful
        """
        try:
            if not self._session_state or not self._signal_hub:
                raise PlatformError("Components not initialized")
            
            self._update_splash("Criando janela principal...")
            
            # Create main window
            self._main_window = MainWindow(
                session_state=self._session_state,
                signal_hub=self._signal_hub
            )
            
            # Configure window
            self._main_window.setWindowIcon(self.windowIcon())
            
            # Restore window geometry
            self._restore_window_geometry()
            
            # Show window
            self._main_window.show()
            
            # Hide splash
            self._hide_splash()
            
            logger.info("main_window_created")
            return True
            
        except Exception as e:
            logger.error("main_window_creation_failed", error=str(e))
            self._show_error("Erro na Interface", 
                           f"Falha ao criar janela principal:\\n{e}")
            return False
    
    def _restore_window_geometry(self):
        """Restore window geometry from settings"""
        if not self._main_window:
            return
            
        # Try to restore from QSettings
        # For now, use default sizing
        self._main_window.resize(1200, 800)
        
        # Center on screen
        screen = self.primaryScreen().availableGeometry()
        window_geometry = self._main_window.geometry()
        center_point = screen.center() - window_geometry.center()
        self._main_window.move(center_point)
    
    def _show_error(self, title: str, message: str):
        """Show error dialog"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def _graceful_shutdown(self):
        """Perform graceful application shutdown"""
        logger.info("graceful_shutdown_started")
        
        try:
            # Save session if main window exists
            if self._main_window:
                self._main_window.save_session_on_exit()
                
                # Save window geometry
                # For now, skip saving geometry
                pass
            
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
        Run the application.
        
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
            self._show_error("Erro Fatal", f"Erro inesperado na aplicação:\\n{e}")
            return 1


def create_application(argv: Optional[list[str]] = None, 
                      cache_config: Optional[dict] = None) -> PlatformApplication:
    """
    Factory function to create application instance.
    
    Args:
        argv: Command line arguments
        cache_config: Cache configuration
        
    Returns:
        Configured application instance
    """
    if argv is None:
        argv = sys.argv
        
    app = PlatformApplication(argv)
    return app


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for the desktop application.
    
    Args:
        argv: Command line arguments
        
    Returns:
        Exit code
    """
    # Setup logging
    setup_logging()
    
    # Create and run application
    app = create_application(argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())