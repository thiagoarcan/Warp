#!/usr/bin/env python3
"""
Script de teste para verificar a aplicação PyQt6
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Testa se todos os imports essenciais funcionam"""
    try:
        print("Testando imports...")
        
        # Core components
        from platform_base.core.models import Dataset, Series
        print("OK Core models importados")
        
        from platform_base.core.dataset_store import DatasetStore
        print("OK DatasetStore importado")
        
        from platform_base.ui.state import SessionState
        print("OK SessionState importado")
        
        # PyQt6 components
        from PyQt6.QtWidgets import QApplication
        from platform_base.ui.app import PlatformApplication
        from platform_base.ui.main_window import MainWindow
        print("OK PyQt6 components importados")
        
        # Processing
        from platform_base.processing.interpolation import interpolate
        from platform_base.processing.synchronization import synchronize
        from platform_base.processing.calculus import derivative, integral
        print("OK Processing modules importados")
        
        # I/O
        from platform_base.io.loader import load, LoadConfig
        print("OK I/O modules importados")
        
        print("\nOK Todos os imports funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"ERRO no import: {e}")
        return False

def test_basic_functionality():
    """Testa funcionalidade básica sem GUI"""
    try:
        print("\nTestando funcionalidade básica...")
        
        # Test DatasetStore
        from platform_base.core.dataset_store import DatasetStore
        store = DatasetStore()
        print("OK DatasetStore criado")
        
        # Test SessionState  
        from platform_base.ui.state import SessionState
        session = SessionState(store)
        print("OK SessionState criado")
        
        # Test logging
        from platform_base.utils.logging import setup_logging, get_logger
        setup_logging("INFO")
        logger = get_logger("test")
        logger.info("teste_log_funcionando", test=True)
        print("OK Logging funcionando")
        
        print("\nOK Funcionalidade basica funcionando!")
        return True
        
    except Exception as e:
        print(f"ERRO na funcionalidade basica: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui():
    """Testa se a GUI pode ser criada (sem mostrar)"""
    try:
        print("\nTestando interface gráfica...")
        
        # Create application (required for any Qt widgets)
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # Test basic widget creation
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.ui.state import SessionState
        from platform_base.ui.main_window import MainWindow
        
        store = DatasetStore()
        session = SessionState(store)
        
        # Create main window (but don't show it)
        window = MainWindow(session)
        print("OK MainWindow criada")
        
        # Test panel creation
        if window._data_panel:
            print("OK DataPanel criado")
        if window._viz_panel:
            print("OK VizPanel criado") 
        if window._operations_panel:
            print("OK OperationsPanel criado")
        
        # Cleanup
        window.close()
        app.quit()
        
        print("\nOK Interface grafica funcionando!")
        return True
        
    except Exception as e:
        print(f"ERRO na interface grafica: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("=== Teste da Aplicação Platform Base ===")
    print(f"Python: {sys.version}")
    print(f"Diretório: {Path.cwd()}")
    print()
    
    success = True
    
    # Test imports
    success &= test_imports()
    
    # Test basic functionality
    success &= test_basic_functionality()
    
    # Test GUI
    success &= test_gui()
    
    print("\n" + "="*50)
    if success:
        print("SUCESSO! Todos os testes passaram! A aplicacao esta pronta para uso.")
        print("\nPara executar a aplicação completa:")
        print("python -m platform_base.ui.app")
    else:
        print("ERRO: Alguns testes falharam. Verifique os erros acima.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())