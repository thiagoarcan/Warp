#!/usr/bin/env python3
"""
Script de debug para verificar atualizações da UI após carregamento
"""

import os
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtWidgets import QApplication, QMessageBox

    from platform_base.core.dataset_store import DatasetStore
    from platform_base.ui.main_window import ModernMainWindow
    from platform_base.ui.state import SessionState
    from platform_base.utils.logging import get_logger
    
    logger = get_logger(__name__)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Platform Base DEBUG")
    
    # Create dataset store and session state
    dataset_store = DatasetStore()
    session_state = SessionState(dataset_store)
    
    # Create main window
    main_window = ModernMainWindow(session_state)
    main_window.show()
    
    # Get data panel for debugging
    data_panel = main_window._data_panel
    
    def debug_ui_state():
        """Imprime estado da UI para debug"""
        print("\n" + "="*70)
        print("DEBUG: Estado da UI")
        print("="*70)
        
        # Check session state
        current_id = session_state.current_dataset
        all_datasets = session_state.get_all_datasets()
        print(f"\nSessionState:")
        print(f"  - current_dataset: {current_id}")
        print(f"  - total datasets: {len(all_datasets)}")
        print(f"  - dataset IDs: {list(all_datasets.keys())}")
        
        # Check data panel internal state
        print(f"\nDataPanel:")
        print(f"  - _current_dataset: {data_panel._current_dataset}")
        print(f"  - _updating_ui: {data_panel._updating_ui}")
        
        # Check tree widget
        datasets_tree = data_panel._datasets_tree
        print(f"\nDatasets Tree Widget:")
        print(f"  - isVisible: {datasets_tree.isVisible()}")
        print(f"  - isEnabled: {datasets_tree.isEnabled()}")
        print(f"  - size: {datasets_tree.size().width()}x{datasets_tree.size().height()}")
        print(f"  - topLevelItemCount: {datasets_tree.topLevelItemCount()}")
        
        if datasets_tree.topLevelItemCount() > 0:
            for i in range(datasets_tree.topLevelItemCount()):
                item = datasets_tree.topLevelItem(i)
                print(f"    Item {i}: [{item.text(0)}] [{item.text(1)}] [{item.text(2)}]")
        else:
            print("    (vazio)")
            
        # Check series tree
        series_tree = data_panel._series_tree
        print(f"\nSeries Tree Widget:")
        print(f"  - isVisible: {series_tree.isVisible()}")
        print(f"  - topLevelItemCount: {series_tree.topLevelItemCount()}")
        
        # Check data table  
        data_table = data_panel._data_table
        print(f"\nData Table Widget:")
        print(f"  - isVisible: {data_table.isVisible()}")
        print(f"  - rowCount: {data_table.rowCount()}")
        print(f"  - columnCount: {data_table.columnCount()}")
        
        # Check overall visibility chain
        print(f"\nVisibility Chain:")
        widget = datasets_tree
        chain = []
        while widget:
            vis = "visible" if widget.isVisible() else "HIDDEN"
            size = f"{widget.size().width()}x{widget.size().height()}"
            chain.append(f"{widget.__class__.__name__}({vis},{size})")
            widget = widget.parent() if hasattr(widget, 'parent') else None
            if widget and not isinstance(widget, type(QApplication.instance())):
                widget = widget if hasattr(widget, '__class__') else None
            else:
                break
        for i, c in enumerate(chain):
            print(f"  {'  '*i}{c}")
        
        print("="*70 + "\n")
    
    def auto_load_test():
        """Carrega arquivo automaticamente para teste"""
        print("\n>>> Auto-carregando arquivo de teste...")
        
        # Find test files
        warp_dir = current_dir.parent
        test_files = list(warp_dir.glob("BAR_*.xlsx"))[:1]
        
        if test_files:
            test_file = str(test_files[0])
            print(f">>> Carregando: {test_file}")
            data_panel.load_dataset(test_file)
            
            # Check state after loading (with delay)
            QTimer.singleShot(3000, debug_ui_state)
            
            # Force repaint
            def force_repaint():
                print(">>> Forçando repaint...")
                data_panel._datasets_tree.update()
                data_panel._datasets_tree.repaint()
                data_panel.update()
                data_panel.repaint()
                main_window.update()
                main_window.repaint()
                debug_ui_state()
                
            QTimer.singleShot(5000, force_repaint)
        else:
            print(">>> Nenhum arquivo de teste encontrado")
            debug_ui_state()
    
    # Initial state
    print(">>> Estado inicial:")
    debug_ui_state()
    
    # Auto load after window is shown
    QTimer.singleShot(1000, auto_load_test)
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
