#!/usr/bin/env python3
"""
Test direct loading without GUI worker threads
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
os.environ['PYTHONUTF8'] = '1'

def test_direct_load():
    """Test direct loading with encoding fix"""
    try:
        print("Testing direct load with encoding fixes...")
        
        from platform_base.io.loader import load, LoadConfig
        from platform_base.ui.state import SessionState
        from platform_base.core.dataset_store import DatasetStore
        
        print("1. Creating session state...")
        
        # Create session state
        dataset_store = DatasetStore()
        session_state = SessionState(dataset_store)
        
        print("2. Testing file with original encoding issue...")
        
        # Test with the original Excel file that had encoding issues
        test_file = r"C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Warp\BAR_FT-OP10.xlsx"
        
        if not Path(test_file).exists():
            print("   Excel file not found")
            return False
        
        print(f"3. Loading: {Path(test_file).name}")
        
        # Test path normalization
        try:
            normalized_path = str(Path(test_file).resolve())
            print(f"   Normalized path: {normalized_path}")
        except Exception as e:
            print(f"   Path normalization failed: {e}")
            normalized_path = test_file
        
        # Load directly
        print("4. Loading dataset...")
        config = LoadConfig()
        dataset = load(normalized_path, config)
        
        print(f"   Dataset loaded: {len(dataset.series)} series, {len(dataset.t_seconds)} points")
        
        # Add to session state
        print("5. Adding to session state...")
        dataset_id = session_state.add_dataset(dataset)
        print(f"   Dataset added with ID: {dataset_id}")
        
        # Verify in session state
        all_datasets = session_state.get_all_datasets()
        print(f"   Total datasets in session: {len(all_datasets)}")
        
        print("DIRECT LOAD TEST: SUCCESS!")
        return True
        
    except Exception as e:
        print(f"ERROR in direct load test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_load()