# DEPRECATED: Historical workaround launcher.
# Kept only for reference after Phase 2-3 runtime consolidation.
# Canonical entry point is launch_app.py.
#

#!/usr/bin/env python3
"""
Test launcher script to identify issues
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

print("Starting import test...")

try:
    print("1. Importing PyQt6...")
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import QApplication, QMessageBox
    print("   PyQt6 imported successfully")

    print("2. Importing core components...")
    from platform_base.core.dataset_store import DatasetStore
    print("   DatasetStore imported")
    
    from platform_base.desktop.session_state import SessionState
    print("   SessionState imported")
    
    from platform_base.desktop.signal_hub import SignalHub
    print("   SignalHub imported")

    print("3. Importing main window...")
    from platform_base.ui.main_window_unified import ModernMainWindow
    print("   ModernMainWindow imported successfully")

    print("4. Creating QApplication...")
    app = QApplication(sys.argv)
    app.setApplicationName("Platform Base Test")
    print("   QApplication created")

    print("5. Creating components...")
    dataset_store = DatasetStore()
    session_state = SessionState(dataset_store)
    signal_hub = SignalHub()
    print("   Core components created")

    print("6. Creating main window...")
    main_window = ModernMainWindow(session_state, signal_hub)
    print("   Main window created successfully")

    print("7. Showing window...")
    main_window.show()
    print("   Window shown")

    print("SUCCESS: All components loaded. Starting app...")
    app.exec()

except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    print("TRACEBACK:")
    print(traceback.format_exc())
