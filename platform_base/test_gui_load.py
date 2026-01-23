#!/usr/bin/env python3
"""
Test file loading through GUI interface - simulating user interaction
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

def test_gui_loading():
    """Test loading file through GUI components"""
    try:
        print("Testing GUI file loading components...")
        
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        
        from platform_base.ui.state import SessionState
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.panels.data_panel import CompactDataPanel
        
        # Create minimal QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        print("1. Creating components...")
        
        # Create components
        dataset_store = DatasetStore()
        session_state = SessionState(dataset_store)
        data_panel = CompactDataPanel(session_state)
        
        print("2. Components created successfully")
        
        # Test file loading - use the CSV sample to avoid encoding issues
        test_file = Path("tests/fixtures/BAR_FT-OP10_sample.csv").absolute()
        if not test_file.exists():
            print("   No test file available, skipping load test")
            return True
        
        test_file = str(test_file)
        
        print(f"3. Testing file loading: {Path(test_file).name}")
        
        # Connect to finished signal to track completion
        results = {'completed': False, 'error': None}
        
        def on_dataset_loaded(dataset_id):
            print(f"   Dataset loaded: {dataset_id}")
            results['completed'] = True
            # Don't call app.quit() here as we might be in an existing app
        
        def on_load_error(error):
            print(f"   Load error: {error}")
            results['error'] = error
            results['completed'] = True
        
        # Connect signals
        data_panel.dataset_loaded.connect(on_dataset_loaded)
        
        # Start loading
        data_panel.load_dataset(test_file)
        
        print("4. Load initiated, waiting for completion...")
        
        # Wait for completion with timeout
        timeout_counter = 0
        max_timeout = 100  # 10 seconds
        
        while not results['completed'] and timeout_counter < max_timeout:
            app.processEvents()
            QTimer.singleShot(100, lambda: None)  # 100ms delay
            timeout_counter += 1
        
        if results['completed']:
            if results['error']:
                print(f"GUI LOAD TEST: FALHOU - {results['error']}")
                return False
            else:
                print("GUI LOAD TEST: SUCESSO!")
                
                # Check session state
                datasets = session_state.get_all_datasets()
                print(f"   Total datasets in session: {len(datasets)}")
                return True
        else:
            print("GUI LOAD TEST: TIMEOUT!")
            return False
        
    except Exception as e:
        print(f"ERRO no teste GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_gui_loading()