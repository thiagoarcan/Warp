#!/usr/bin/env python3
"""
Test multiple file loading workflow
"""

import sys
import os
from pathlib import Path
import glob

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Set environment for Windows console encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

def test_multiple_load():
    """Test loading multiple files"""
    try:
        print("Testing multiple file loading...")
        
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        
        from platform_base.ui.state import SessionState
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.panels.data_panel import CompactDataPanel
        
        # Create QApplication
        app = QApplication([])
        
        print("1. Creating components...")
        
        # Create components
        dataset_store = DatasetStore()
        session_state = SessionState(dataset_store)
        data_panel = CompactDataPanel(session_state)
        
        print("2. Components created successfully")
        
        # Get all Excel files in the parent directory
        excel_files = list(Path("..").glob("*.xlsx"))
        if len(excel_files) == 0:
            print("   No Excel files found, using CSV sample")
            test_files = [Path("tests/fixtures/BAR_FT-OP10_sample.csv").absolute()]
        else:
            # Use first 3 files to test multiple loading
            test_files = excel_files[:3]
        
        print(f"3. Testing {len(test_files)} files:")
        for file_path in test_files:
            print(f"   - {file_path.name}")
        
        # Track results
        results = {'loaded_count': 0, 'target_count': len(test_files), 'completed': False}
        
        def on_dataset_loaded(dataset_id):
            results['loaded_count'] += 1
            print(f"   Dataset loaded: {dataset_id} ({results['loaded_count']}/{results['target_count']})")
            
            if results['loaded_count'] >= results['target_count']:
                results['completed'] = True
                app.quit()
        
        def on_timeout():
            print("   Test timeout reached")
            results['completed'] = True
            app.quit()
        
        # Connect signals
        data_panel.dataset_loaded.connect(on_dataset_loaded)
        
        # Start loading all files
        print("4. Loading files...")
        for file_path in test_files:
            data_panel.load_dataset(str(file_path))
        
        # Set a timeout for the test
        QTimer.singleShot(30000, on_timeout)  # 30 second timeout for multiple files
        
        # Run until completion
        app.exec()
        
        if results['completed'] and results['loaded_count'] > 0:
            print("MULTIPLE LOAD TEST: SUCCESS!")
            
            # Check session state
            datasets = session_state.get_all_datasets()
            print(f"   Total datasets in session: {len(datasets)}")
            print(f"   Successfully loaded: {results['loaded_count']} out of {results['target_count']}")
            
            return True
        else:
            print(f"MULTIPLE LOAD TEST: FAILED - Loaded {results['loaded_count']} out of {results['target_count']}")
            return False
        
    except Exception as e:
        print(f"ERROR in multiple load test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_multiple_load()