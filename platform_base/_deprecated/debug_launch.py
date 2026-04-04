# DEPRECATED: Historical workaround launcher.
# Kept only for reference after Phase 2-3 runtime consolidation.
# Canonical entry point is launch_app.py.
#

#!/usr/bin/env python3
"""
Debug launcher para identificar problemas especÃ­ficos
"""

import sys
import os
import traceback
from pathlib import Path

# Set environment
os.environ["QT_QPA_PLATFORM"] = "windows"
os.environ["PYTHONIOENCODING"] = "utf-8"

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def debug_import(module_name):
    """Debug import function"""
    try:
        print(f"Importing {module_name}...", end=" ")
        module = __import__(module_name)
        print("OK")
        return module
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return None

def main():
    print("=== DEBUG PLATFORM BASE LAUNCH ===")
    
    # Test basic imports
    print("\n1. Testing basic imports...")
    if not debug_import("sys"):
        return
    if not debug_import("pathlib"):
        return
    
    # Test PyQt6
    print("\n2. Testing PyQt6...")
    try:
        print("Importing PyQt6.QtCore...", end=" ")
        from PyQt6.QtCore import Qt
        print("OK")
        
        print("Importing PyQt6.QtWidgets...", end=" ")
        from PyQt6.QtWidgets import QApplication, QMainWindow
        print("OK")
        
        print("Creating QApplication...", end=" ")
        app = QApplication(sys.argv)
        print("OK")
        
    except Exception as e:
        print(f"FAILED: {e}")
        return
    
    # Test platform_base core components step by step
    print("\n3. Testing platform_base core...")
    
    try:
        print("Importing logging...", end=" ")
        from platform_base.utils.logging import get_logger
        print("OK")
        logger = get_logger(__name__)
        
    except Exception as e:
        print(f"FAILED: {e}")
        print("Trying without logging...")
        logger = None
    
    try:
        print("Importing DatasetStore...", end=" ")
        from platform_base.core.dataset_store import DatasetStore
        print("OK")
        
        print("Creating DatasetStore...", end=" ")
        dataset_store = DatasetStore()
        print("OK")
        
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return
    
    try:
        print("Importing SessionState...", end=" ")
        from platform_base.core.session_state import SessionState
        print("OK")
        
        print("Creating SessionState...", end=" ")
        session_state = SessionState(dataset_store)
        print("OK")
        
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return
    
    try:
        print("Importing SignalHub...", end=" ")
        from platform_base.core.signal_hub import SignalHub
        print("OK")
        
        print("Creating SignalHub...", end=" ")
        signal_hub = SignalHub()
        print("OK")
        
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        return
    
    # Test main window
    print("\n4. Testing main window...")
    try:
        print("Importing ModernMainWindow...", end=" ")
        from platform_base.ui.main_window_unified import ModernMainWindow
        print("OK")
        
        print("Creating ModernMainWindow...", end=" ")
        main_window = ModernMainWindow(session_state, signal_hub)
        print("OK")
        
        print("Showing main window...", end=" ")
        main_window.show()
        print("OK")
        
        print("\n=== SUCCESS! ===")
        print("All components loaded successfully!")
        print("Starting application...")
        
        if logger:
            logger.info("application_started_successfully")
        
        app.exec()
        
    except Exception as e:
        print(f"FAILED: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        
        # Try to identify the specific problem
        print("\n=== ANALYSIS ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        if "ui" in str(e).lower():
            print("Possible UI file loading issue")
        elif "import" in str(e).lower():
            print("Possible import dependency issue")
        elif "theme" in str(e).lower():
            print("Possible theme loading issue")

if __name__ == "__main__":
    main()
