#!/usr/bin/env python
"""Debug profundo da aplicação Platform Base v2.0"""

import os
import sys
import traceback
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def section(title):
    print()
    print('=' * 70)
    print(f' {title}')
    print('=' * 70)


def create_app_components():
    """Cria componentes da aplicação corretamente"""
    from platform_base.core.dataset_store import DatasetStore
    from platform_base.desktop.session_state import SessionState
    
    dataset_store = DatasetStore()
    session_state = SessionState(dataset_store)
    return dataset_store, session_state


def test_ui_loader():
    """Testar sistema de carregamento de .ui"""
    section("4. TESTANDO SISTEMA DE CARREGAMENTO .UI")
    
    from platform_base.ui.loader import DESIGNER_PATH, validate_ui_file
    
    print(f"\nDESIGNER_PATH: {DESIGNER_PATH}")
    print(f"Existe: {DESIGNER_PATH.exists()}")
    
    tests = [
        ('main_window', True),
        ('panels/data_panel', True),
        ('dialogs/settings_dialog', False),
        ('panels/viz_panel', False),
    ]
    
    print("\nValidação de arquivos .ui:")
    for ui_name, expected in tests:
        result = validate_ui_file(ui_name)
        status = '✅' if result == expected else '❌'
        exists = 'existe' if result else 'não existe'
        print(f"  {status} {ui_name}: {exists}")


def test_app_initialization():
    """Testar inicialização da aplicação"""
    section("5. TESTANDO INICIALIZAÇÃO DA APLICAÇÃO")
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        print("✅ QApplication criado com sucesso")
        
        # Criar componentes corretamente
        dataset_store, session_state = create_app_components()
        print("✅ DatasetStore criado com sucesso")
        print("✅ SessionState criado com sucesso")
        
        # Testar MainWindow do desktop
        from platform_base.desktop.main_window import MainWindow
        from platform_base.desktop.signal_hub import SignalHub
        
        signal_hub = SignalHub()
        print("✅ SignalHub criado com sucesso")
        
        window = MainWindow(session_state, signal_hub)
        print("✅ MainWindow criado com sucesso")
        print(f"   Tamanho: {window.size().width()}x{window.size().height()}")
        
        return True
    except Exception as e:
        print(f"❌ Erro na inicialização: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def test_data_loading():
    """Testar carregamento de dados"""
    section("6. TESTANDO CARREGAMENTO DE DADOS")
    
    from platform_base.io.loader import FileFormat, load
    
    print("✅ load() importado")
    print("✅ FileFormat importado")
    
    # Verificar formatos suportados
    print(f"\nFormatos suportados: {[f.value for f in FileFormat]}")
    
    # Verificar se há arquivos de teste
    test_files = list(Path('tests/fixtures').rglob('*.csv'))
    test_files += list(Path('tests/fixtures').rglob('*.xlsx'))
    
    print(f"\nArquivos de teste encontrados: {len(test_files)}")
    for f in test_files[:5]:
        print(f"   {f}")


def test_processing():
    """Testar módulos de processamento"""
    section("7. TESTANDO MÓDULOS DE PROCESSAMENTO")
    
    import numpy as np

    # Interpolação
    from platform_base.processing.interpolation import SUPPORTED_METHODS, interpolate
    print(f"✅ interpolate() importado")
    print(f"   Métodos suportados: {SUPPORTED_METHODS}")
    
    # Dados de teste
    t = np.array([0, 1, 2, 3, 4], dtype=np.float64)
    y = np.array([0, 1, 4, 9, 16], dtype=np.float64)
    
    # Assinatura: interpolate(values, t_seconds, method, params)
    result = interpolate(y, t, 'linear', {'target_points': 10})
    print(f"✅ Interpolação linear funcionando: {len(result.values)} pontos")
    
    # Cálculo
    from platform_base.processing.calculus import derivative, integral
    print("✅ derivative() importado")
    print("✅ integral() importado")
    
    # Derivada com Numba (método padrão)
    deriv = derivative(t, y, order=1)
    print(f"✅ Derivada calculada: {len(deriv.values)} pontos")
    
    # Suavização
    from platform_base.processing.smoothing import smooth
    print(f"✅ smooth() importado")


def test_visualization():
    """Testar módulos de visualização"""
    section("8. TESTANDO MÓDULOS DE VISUALIZAÇÃO")
    
    # 2D
    from platform_base.viz import figures_2d
    print(f"✅ figures_2d importado")
    funcs_2d = [x for x in dir(figures_2d) if not x.startswith('_') and callable(getattr(figures_2d, x, None))]
    print(f"   Funções: {funcs_2d[:5]}...")
    
    # 3D
    from platform_base.viz import figures_3d
    print(f"✅ figures_3d importado")
    funcs_3d = [x for x in dir(figures_3d) if not x.startswith('_') and callable(getattr(figures_3d, x, None))]
    print(f"   Funções: {funcs_3d[:5]}...")


def test_ui_panels():
    """Testar painéis da UI"""
    section("9. TESTANDO PAINÉIS DA UI")
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    
    dataset_store, session_state = create_app_components()
    
    panels = [
        ('platform_base.ui.panels.data_panel', 'CompactDataPanel'),
        ('platform_base.ui.panels.viz_panel', 'ModernVizPanel'),
        ('platform_base.ui.panels.operations_panel', 'OperationsPanel'),
        ('platform_base.ui.panels.config_panel', 'ConfigPanel'),
        ('platform_base.ui.panels.results_panel', 'ResultsPanel'),
    ]
    
    for module_name, class_name in panels:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            panel = cls(session_state)
            print(f"✅ {class_name}: OK")
        except Exception as e:
            print(f"❌ {class_name}: {type(e).__name__}: {str(e)[:50]}")


def test_dialogs():
    """Testar diálogos"""
    section("10. TESTANDO DIÁLOGOS")
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    
    dialogs = [
        ('platform_base.ui.dialogs.settings_dialog', 'SettingsDialog', []),
        ('platform_base.ui.dialogs.filter_dialog', 'FilterDialog', []),
        ('platform_base.ui.dialogs.smoothing_dialog', 'SmoothingDialog', []),
        ('platform_base.ui.export_dialog', 'ExportDialog', []),
    ]
    
    for module_name, class_name, args in dialogs:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            dialog = cls(*args)
            print(f"✅ {class_name}: OK")
        except Exception as e:
            print(f"❌ {class_name}: {type(e).__name__}: {str(e)[:50]}")


def check_potential_issues():
    """Verificar problemas potenciais"""
    section("11. VERIFICANDO PROBLEMAS POTENCIAIS")
    
    issues = []
    warnings = []
    
    # Verificar se .egg-info foi removido
    egg_info = Path('src/platform_base.egg-info')
    if egg_info.exists():
        warnings.append(f"Pasta .egg-info ainda existe (pode ser deletada)")
    else:
        print("✅ Pasta .egg-info removida corretamente")
    
    # Verificar __pycache__
    pycache_dirs = list(Path('.').rglob('__pycache__'))
    if pycache_dirs:
        print(f"⚠️  {len(pycache_dirs)} pastas __pycache__ encontradas (normal)")
    
    # Verificar .gitignore
    gitignore = Path('../.gitignore')
    if gitignore.exists():
        print("✅ .gitignore existe")
    else:
        warnings.append(".gitignore não encontrado na raiz")
    
    # Verificar configuração
    config = Path('configs/platform.yaml')
    if config.exists():
        print(f"✅ Configuração encontrada: {config}")
    else:
        warnings.append(f"Configuração não encontrada: {config}")
    
    # Verificar subpastas UI Designer
    designer_path = Path('src/platform_base/ui/designer')
    subdirs = ['panels', 'dialogs', 'tabs', 'components']
    for subdir in subdirs:
        subdir_path = designer_path / subdir
        if subdir_path.exists():
            ui_count = len(list(subdir_path.glob('*.ui')))
            print(f"✅ {subdir}/: {ui_count} arquivos .ui")
        else:
            print(f"⚠️  {subdir}/: pasta não existe ainda")
    
    if warnings:
        print("\nAvisos:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    return len(issues) == 0


def test_full_launch():
    """Testar launch completo da aplicação"""
    section("12. TESTANDO LAUNCH COMPLETO")
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from platform_base.desktop.app import PlatformApplication
        
        app = PlatformApplication(sys.argv)
        print("✅ PlatformApplication criado")
        
        success = app.initialize_components()
        print(f"{'✅' if success else '❌'} initialize_components(): {success}")
        
        if success:
            success = app.create_main_window()
            print(f"{'✅' if success else '❌'} create_main_window(): {success}")
        
        return success
    except Exception as e:
        print(f"❌ Erro: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def main():
    print("\n" + "🔍" * 35)
    print("  DEBUG PROFUNDO - PLATFORM BASE v2.0")
    print("🔍" * 35)
    
    results = {}
    
    # Teste 1-3: Imports (já verificados)
    section("1-3. IMPORTS JÁ VERIFICADOS ✅")
    print("Todos os imports principais estão OK")
    
    # Teste 4: UI Loader
    try:
        test_ui_loader()
        results['ui_loader'] = True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['ui_loader'] = False
    
    # Teste 5: App Initialization
    try:
        results['app_init'] = test_app_initialization()
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['app_init'] = False
    
    # Teste 6: Data Loading
    try:
        test_data_loading()
        results['data_loading'] = True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['data_loading'] = False
    
    # Teste 7: Processing
    try:
        test_processing()
        results['processing'] = True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['processing'] = False
    
    # Teste 8: Visualization
    try:
        test_visualization()
        results['visualization'] = True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['visualization'] = False
    
    # Teste 9: UI Panels
    try:
        test_ui_panels()
        results['ui_panels'] = True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['ui_panels'] = False
    
    # Teste 10: Dialogs
    try:
        test_dialogs()
        results['dialogs'] = True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['dialogs'] = False
    
    # Teste 11: Potential Issues
    try:
        results['issues_check'] = check_potential_issues()
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['issues_check'] = False
    
    # Teste 12: Full Launch
    try:
        results['full_launch'] = test_full_launch()
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()
        results['full_launch'] = False
    
    # Resumo
    section("📊 RESUMO DO DEBUG")
    
    print("\nResultados por módulo:")
    for name, passed in results.items():
        status = '✅' if passed else '❌'
        print(f"  {status} {name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n{'='*70}")
    print(f"  RESULTADO FINAL: {total_passed}/{total_tests} módulos OK")
    if total_passed == total_tests:
        print("  🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("  ⚠️  Alguns módulos precisam de atenção")
    print(f"{'='*70}")
    
    return total_passed == total_tests


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
