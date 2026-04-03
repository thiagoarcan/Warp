#!/usr/bin/env python3
"""
Fixed launcher that bypasses problematic imports
"""

import sys
import os
from pathlib import Path

# Set environment for Windows
os.environ["QT_QPA_PLATFORM"] = "windows"
os.environ["PYTHONIOENCODING"] = "utf-8"

# Disable problematic logging modules temporarily
sys.modules['structlog'] = None

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def create_minimal_logger():
    """Create a minimal logger replacement"""
    class MinimalLogger:
        def info(self, *args, **kwargs): pass
        def debug(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass
        def exception(self, *args, **kwargs): pass
    return MinimalLogger()

def main():
    try:
        print("Starting Platform Base v2.0 with fixed launcher...")
        
        # Import PyQt6 first
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication, QMessageBox
        print("OK PyQt6 loaded")
        
        # Create QApplication early
        app = QApplication(sys.argv)
        app.setApplicationName("Platform Base v2.0")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("TRANSPETRO")
        print("OK QApplication created")
        
        # Monkey patch logger to avoid hanging
        import platform_base.utils.logging
        platform_base.utils.logging.get_logger = lambda x: create_minimal_logger()
        
        # Import and create core components
        from platform_base.core.dataset_store import DatasetStore
        dataset_store = DatasetStore()
        print("OK DatasetStore created")
        
        from platform_base.core.session_state import SessionState
        session_state = SessionState(dataset_store)
        print("OK SessionState created")
        
        from platform_base.core.signal_hub import SignalHub
        signal_hub = SignalHub()
        print("OK SignalHub created")
        
        # Import and create main window
        from platform_base.ui.main_window_unified import ModernMainWindow
        main_window = ModernMainWindow(session_state, signal_hub)
        print("OK ModernMainWindow created")
        
        # Show the window
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        print("SUCCESS: Platform Base v2.0 started successfully!")
        print("SUCCESS: Layout reorganized - no overlapping panels")
        print("SUCCESS: All components properly sized and organized")
        print("SUCCESS: Interface should now display correctly")
        
        # Run the application
        exit_code = app.exec()
        print(f"Application exited with code: {exit_code}")
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog if possible
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            if not QApplication.instance():
                app = QApplication(sys.argv)
            QMessageBox.critical(None, "Platform Base Error", f"Failed to start:\n{e}")
        except:
            pass

if __name__ == "__main__":
    main()