#!/usr/bin/env python3
"""Test launcher script"""
import os
import sys
from pathlib import Path

# Disable dask cupy integration to speed up loading
os.environ['DASK_DATAFRAME__QUERY_PLANNING'] = 'False'

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import traceback


def main():
    try:
        print('1. Importando PyQt6...')
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        print('2. Importando componentes...')
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.desktop.session_state import SessionState
        from platform_base.desktop.signal_hub import SignalHub
        
        print('3. Criando componentes...')
        ds = DatasetStore()
        ss = SessionState(ds)
        sh = SignalHub()
        
        print('4. Importando MainWindow...')
        from platform_base.desktop.main_window import MainWindow
        
        print('5. Criando janela principal...')
        w = MainWindow(session_state=ss, signal_hub=sh)
        w.resize(1200, 800)
        w.show()
        
        print('6. Executando loop de eventos...')
        print('   (A janela deve estar visivel agora)')
        return app.exec()
        
    except Exception as e:
        print(f'ERRO FATAL: {e}')
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
