#!/usr/bin/env python
"""Script de teste para debug do MainWindow"""
import sys
import traceback

# Adicionar src ao path
sys.path.insert(0, 'src')

print('=== Iniciando teste de debug ===')

try:
    print('1. Importando PyQt6...')
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    print('   OK')
    
    print('2. Importando DatasetStore...')
    from platform_base.core.dataset_store import DatasetStore
    ds = DatasetStore()
    print('   OK')
    
    print('3. Importando SessionState...')
    from platform_base.desktop.session_state import SessionState
    ss = SessionState(ds)
    print('   OK')
    
    print('4. Importando SignalHub...')
    from platform_base.desktop.signal_hub import SignalHub
    sh = SignalHub()
    print('   OK')
    
    print('5. Importando MainWindow...')
    from platform_base.desktop.main_window import MainWindow
    print('   OK')
    
    print('6. Criando MainWindow...')
    w = MainWindow(session_state=ss, signal_hub=sh)
    print('   OK')
    
    print('7. Mostrando janela...')
    w.show()
    print('   OK')
    
    print('=== Tudo OK! Iniciando event loop ===')
    sys.exit(app.exec())
    
except Exception as e:
    print(f'\nERRO: {e}')
    traceback.print_exc()
    sys.exit(1)
