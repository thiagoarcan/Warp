#!/usr/bin/env python3
"""
Launcher script for Platform Base v2.0
Ensures proper GUI initialization and error handling
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import QApplication, QMessageBox

    # Import main window - usa versão unificada com todas as funcionalidades
    from platform_base.core.dataset_store import DatasetStore
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub
    from platform_base.ui.main_window_unified import ModernMainWindow
    from platform_base.utils.logging import get_logger
    
    logger = get_logger(__name__)
    
    def main():
        """Main application entry point"""
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Platform Base v2.0")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("TRANSPETRO")
        
        # Set application attributes for better display (PyQt6 compatible)
        # Note: High DPI scaling is automatic in PyQt6
        
        try:
            # Create dataset store and session state
            dataset_store = DatasetStore()
            session_state = SessionState(dataset_store)
            
            # Create signal hub for inter-component communication
            signal_hub = SignalHub()
            
            # Create and show main window with all features
            main_window = ModernMainWindow(session_state, signal_hub)
            main_window.show()
            
            # Start event loop
            logger.info("application_started", version="2.0.0")
            print("Platform Base v2.0 iniciado com sucesso!")
            print("Interface moderna carregada")
            print("Todas as correcoes implementadas")
            
            # Run application
            exit_code = app.exec()
            
            logger.info("application_closed", exit_code=exit_code)
            return exit_code
            
        except Exception as e:
            logger.error("application_startup_failed", error=str(e))
            QMessageBox.critical(
                None,
                "Erro de Inicializacao",
                f"Falha ao iniciar Platform Base v2.0:\n\n{e}"
            )
            return 1

    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"Erro de importacao: {e}")
    print("Verifique se todas as dependencias estao instaladas")
    sys.exit(1)