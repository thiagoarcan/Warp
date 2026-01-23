#!/usr/bin/env python3
"""
Final test to verify application can load files with new encoding fixes
"""

import sys
import os
from pathlib import Path
import time

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Set environment for Windows console encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

def test_final_load():
    """Test complete loading workflow"""
    try:
        print("Testing complete file loading workflow...")
        
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer, QEventLoop
        
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
        
        # Test with the original Excel file now that we have encoding fixes
        test_file = r"C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Warp\BAR_FT-OP10.xlsx"
        
        if not Path(test_file).exists():
            print("   Excel file not found, using CSV sample")
            test_file = str(Path("tests/fixtures/BAR_FT-OP10_sample.csv").absolute())
        
        print(f"3. Testing file loading: {Path(test_file).name}")
        
        # Track results
        results = {'completed': False, 'error': None, 'dataset_id': None}
        
        def on_dataset_loaded(dataset_id):
            print(f"   Dataset loaded successfully: {dataset_id}")
            results['completed'] = True
            results['dataset_id'] = dataset_id
            app.quit()
        
        def on_error():
            print("   Load failed")
            results['completed'] = True
            results['error'] = "Load failed"
            app.quit()
        
        # Connect signals
        data_panel.dataset_loaded.connect(on_dataset_loaded)
        
        # Start loading
        data_panel.load_dataset(test_file)
        
        print("4. Load initiated, waiting for completion...")
        
        # Set a timeout for the test
        QTimer.singleShot(15000, on_error)  # 15 second timeout
        
        # Run until completion
        app.exec()
        
        if results['completed'] and results['dataset_id'] and not results['error']:
            print("FINAL LOAD TEST: SUCCESS!")
            
            # Check session state
            datasets = session_state.get_all_datasets()
            print(f"   Total datasets in session: {len(datasets)}")
            
            if datasets:
                for dataset_id, dataset in datasets.items():
                    print(f"   Dataset {dataset_id}: {len(dataset.series)} series, {len(dataset.t_seconds)} points")
            
            return True
        else:
            print(f"FINAL LOAD TEST: FAILED - {results.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"ERROR in final test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_final_load()