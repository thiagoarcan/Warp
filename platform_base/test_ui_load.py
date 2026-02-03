"""
Teste de carregamento via UI para debug de travamento
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow


def test_ui_loading():
    """Testa carregamento com UI simples"""
    app = QApplication(sys.argv)
    
    # Import after QApplication
    from platform_base.core.dataset_store import DatasetStore
    from platform_base.ui.panels.data_panel import CompactDataPanel
    from platform_base.ui.state import SessionState

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Test Load")
    window.setGeometry(100, 100, 800, 600)
    
    # Create session state with store
    store = DatasetStore()
    session = SessionState(store)
    
    # Create data panel
    panel = CompactDataPanel(session)
    window.setCentralWidget(panel)
    window.show()
    
    # Test files - na pasta pai (Warp)
    warp_folder = Path(__file__).parent.parent
    test_files = list(warp_folder.glob("BAR_*.xlsx"))[:3]
    print(f"Arquivos para teste: {[f.name for f in test_files]}")
    
    if not test_files:
        print("ERRO: Nenhum arquivo xlsx encontrado!")
        return
    
    # Timer to load files after UI is shown
    def do_load():
        print("Iniciando carregamento...")
        start_time = time.perf_counter()
        
        for f in test_files:
            print(f"  - Carregando: {f.name}")
            panel.load_dataset(str(f))
        
        print(f"Carregamentos iniciados em {(time.perf_counter() - start_time)*1000:.0f}ms")
    
    # Schedule load after 1 second
    QTimer.singleShot(1000, do_load)
    
    # Timer to check results
    def check_results():
        datasets = session.get_all_datasets()
        print(f"\nDatasets carregados: {len(datasets)}")
        for ds_id, ds in datasets.items():
            print(f"  - {ds_id}: {len(ds.series)} séries, {len(ds.t_seconds)} pontos")
        
        if len(datasets) >= len(test_files):
            print("\n✅ SUCESSO: Todos os arquivos carregados!")
            app.quit()
        else:
            # Check again in 2 seconds
            QTimer.singleShot(2000, check_results)
    
    # Check after 3 seconds
    QTimer.singleShot(3000, check_results)
    
    # Timeout after 30 seconds
    QTimer.singleShot(30000, lambda: (print("\n❌ TIMEOUT"), app.quit()))
    
    print("Janela aberta. Aguardando carregamento...")
    sys.exit(app.exec())

if __name__ == "__main__":
    test_ui_loading()
