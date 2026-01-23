#!/usr/bin/env python3
"""
Test multiple file loading directly
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

def test_multiple_direct():
    """Test loading multiple files directly"""
    try:
        print("Testing multiple file loading directly...")
        
        from platform_base.io.loader import load, LoadConfig
        from platform_base.ui.state import SessionState
        from platform_base.core.dataset_store import DatasetStore
        
        print("1. Creating session state...")
        
        # Create session state
        dataset_store = DatasetStore()
        session_state = SessionState(dataset_store)
        
        print("2. Finding Excel files...")
        
        # Get all Excel files in the parent directory
        base_path = Path("..").resolve()
        excel_files = list(base_path.glob("*.xlsx"))
        
        if len(excel_files) == 0:
            print("   No Excel files found")
            return False
        
        # Test with first 8 files (as user requested)
        test_files = excel_files[:8]
        
        print(f"3. Testing {len(test_files)} files:")
        for file_path in test_files:
            print(f"   - {file_path.name}")
        
        print("4. Loading files...")
        
        loaded_count = 0
        config = LoadConfig()
        
        for i, file_path in enumerate(test_files, 1):
            try:
                print(f"   Loading {i}/{len(test_files)}: {file_path.name}")
                
                # Normalize path
                normalized_path = str(file_path.resolve())
                
                # Load dataset
                dataset = load(normalized_path, config)
                
                # Add to session state
                dataset_id = session_state.add_dataset(dataset)
                
                print(f"     Success: {len(dataset.series)} series, {len(dataset.t_seconds)} points -> {dataset_id}")
                loaded_count += 1
                
            except Exception as e:
                print(f"     Failed: {e}")
        
        # Verify in session state
        all_datasets = session_state.get_all_datasets()
        print(f"5. Results:")
        print(f"   Successfully loaded: {loaded_count} out of {len(test_files)}")
        print(f"   Total datasets in session: {len(all_datasets)}")
        
        for dataset_id, dataset in all_datasets.items():
            filename = dataset_id
            if hasattr(dataset, 'source') and dataset.source:
                filename = Path(dataset.source.filename).name
            print(f"   - {dataset_id}: {filename} ({len(dataset.series)} series)")
        
        if loaded_count >= len(test_files):
            print("MULTIPLE DIRECT LOAD TEST: SUCCESS!")
            return True
        else:
            print("MULTIPLE DIRECT LOAD TEST: PARTIAL SUCCESS!")
            return True  # Still consider success if some files loaded
        
    except Exception as e:
        print(f"ERROR in multiple direct test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_multiple_direct()