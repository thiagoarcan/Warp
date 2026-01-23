#!/usr/bin/env python3
"""
Simple launcher para debug
"""

import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Set environment for Windows console encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'  # Force UTF-8 mode

def main():
    """Launch simple version"""
    try:
        print("Starting Simple Platform Base...")
        
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt
        
        # Import main window
        from platform_base.ui.main_window import ModernMainWindow
        from platform_base.ui.state import SessionState
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.utils.logging import get_logger
        
        logger = get_logger(__name__)
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Platform Base v2.0 - Simple")
        
        # Create dataset store and session state
        dataset_store = DatasetStore()
        session_state = SessionState(dataset_store)
        
        # Create main window with error handling
        try:
            main_window = ModernMainWindow(session_state)
            main_window.show()
            
            print("Simple Platform Base started successfully!")
            logger.info("application_started", version="2.0.0")
            
            # Run application
            exit_code = app.exec()
            
            logger.info("application_closed", exit_code=exit_code)
            return exit_code
            
        except Exception as e:
            logger.error("application_startup_failed", error=str(e))
            print(f"Error starting application: {e}")
            import traceback
            traceback.print_exc()
            return 1

    except Exception as e:
        print(f"Import error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())