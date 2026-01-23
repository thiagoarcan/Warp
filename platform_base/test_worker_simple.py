#!/usr/bin/env python3
"""
Teste simples de worker thread
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_worker():
    """Teste worker thread"""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QThread
        from platform_base.ui.workers.file_worker import FileLoadWorker
        from platform_base.io.loader import LoadConfig
        
        # Create QApplication
        app = QApplication([])
        
        print("Testando worker thread...")
        
        # Create worker thread
        worker_thread = QThread()
        worker = FileLoadWorker(
            r"C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Warp\BAR_FT-OP10.xlsx",
            LoadConfig()
        )
        worker.moveToThread(worker_thread)
        
        # Results
        results = {}
        
        def on_progress(percent, message):
            print(f"   Progress: {percent}% - {message}")
            
        def on_finished(dataset):
            print(f"   Finished: {len(dataset.series)} series, {len(dataset.t_seconds)} points")
            results['success'] = True
            app.quit()
            
        def on_error(error):
            print(f"   Error: {error}")
            results['error'] = error
            app.quit()
        
        # Connect signals
        worker.progress.connect(on_progress)
        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        worker_thread.started.connect(worker.load_file)
        
        # Start
        worker_thread.start()
        
        # Run app
        app.exec()
        
        if 'success' in results:
            print("WORKER TEST: SUCESSO!")
            return True
        else:
            print(f"WORKER TEST: FALHOU - {results.get('error', 'Unknown')}")
            return False
        
    except Exception as e:
        print(f"ERRO no teste worker: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_worker()