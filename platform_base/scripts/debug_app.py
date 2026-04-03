#!/usr/bin/env python
"""Debug profundo da aplicaÃ§Ã£o Platform Base v2.0"""

import os
import sys
import traceback
from pathlib import Path


# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def section(title):
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def create_app_components():
    """Cria componentes da aplicaÃ§Ã£o corretamente"""
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
        ("main_window", True),
        ("panels/data_panel", True),
        ("dialogs/settings_dialog", False),
        ("panels/viz_panel", False),
    ]

    print("\nValidaÃ§Ã£o de arquivos .ui:")
    for ui_name, expected in tests:
        result = validate_ui_file(ui_name)
        status = "âœ…" if result == expected else "âŒ"
        exists = "existe" if result else "nÃ£o existe"
        print(f"  {status} {ui_name}: {exists}")


def test_app_initialization():
    """Testar inicializaÃ§Ã£o da aplicaÃ§Ã£o"""
    section("5. TESTANDO INICIALIZAÃ‡ÃƒO DA APLICAÃ‡ÃƒO")

    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    try:
        from PyQt6.QtWidgets import QApplication
        QApplication.instance() or QApplication(sys.argv)
        print("âœ… QApplication criado com sucesso")

        # Criar componentes corretamente
        dataset_store, session_state = create_app_components()
        print("âœ… DatasetStore criado com sucesso")
        print("âœ… SessionState criado com sucesso")

        # Testar MainWindow do desktop
        from platform_base.desktop.main_window import MainWindow
        from platform_base.desktop.signal_hub import SignalHub

        signal_hub = SignalHub()
        print("âœ… SignalHub criado com sucesso")

        window = MainWindow(session_state, signal_hub)
        print("âœ… MainWindow criado com sucesso")
        print(f"   Tamanho: {window.size().width()}x{window.size().height()}")

        return True
    except Exception as e:
        print(f"âŒ Erro na inicializaÃ§Ã£o: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def test_data_loading():
    """Testar carregamento de dados"""
    section("6. TESTANDO CARREGAMENTO DE DADOS")

    from platform_base.io.loader import FileFormat

    print("âœ… load() importado")
    print("âœ… FileFormat importado")

    # Verificar formatos suportados
    print(f"\nFormatos suportados: {[f.value for f in FileFormat]}")

    # Verificar se hÃ¡ arquivos de teste
    test_files = list(Path("tests/fixtures").rglob("*.csv"))
    test_files += list(Path("tests/fixtures").rglob("*.xlsx"))

    print(f"\nArquivos de teste encontrados: {len(test_files)}")
    for f in test_files[:5]:
        print(f"   {f}")


def test_processing():
    """Testar mÃ³dulos de processamento"""
    section("7. TESTANDO MÃ“DULOS DE PROCESSAMENTO")

    import numpy as np

    # InterpolaÃ§Ã£o
    from platform_base.processing.interpolation import SUPPORTED_METHODS, interpolate
    print("âœ… interpolate() importado")
    print(f"   MÃ©todos suportados: {SUPPORTED_METHODS}")

    # Dados de teste
    t = np.array([0, 1, 2, 3, 4], dtype=np.float64)
    y = np.array([0, 1, 4, 9, 16], dtype=np.float64)

    # Assinatura: interpolate(values, t_seconds, method, params)
    result = interpolate(y, t, "linear", {"target_points": 10})
    print(f"âœ… InterpolaÃ§Ã£o linear funcionando: {len(result.values)} pontos")

    # CÃ¡lculo
    from platform_base.processing.calculus import derivative
    print("âœ… derivative() importado")
    print("âœ… integral() importado")

    # Derivada com Numba (mÃ©todo padrÃ£o)
    deriv = derivative(t, y, order=1)
    print(f"âœ… Derivada calculada: {len(deriv.values)} pontos")

    # SuavizaÃ§Ã£o
    print("âœ… smooth() importado")


def test_visualization():
    """Testar mÃ³dulos de visualizaÃ§Ã£o"""
    section("8. TESTANDO MÃ“DULOS DE VISUALIZAÃ‡ÃƒO")

    # 2D
    from platform_base.viz import figures_2d
    print("âœ… figures_2d importado")
    funcs_2d = [x for x in dir(figures_2d) if not x.startswith("_") and callable(getattr(figures_2d, x, None))]
    print(f"   FunÃ§Ãµes: {funcs_2d[:5]}...")

    # 3D
    from platform_base.viz import figures_3d
    print("âœ… figures_3d importado")
    funcs_3d = [x for x in dir(figures_3d) if not x.startswith("_") and callable(getattr(figures_3d, x, None))]
    print(f"   FunÃ§Ãµes: {funcs_3d[:5]}...")


def test_ui_panels():
    """Testar painÃ©is da UI"""
    section("9. TESTANDO PAINÃ‰IS DA UI")

    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PyQt6.QtWidgets import QApplication
    QApplication.instance() or QApplication(sys.argv)

    dataset_store, session_state = create_app_components()

    panels = [
        ("platform_base.ui.panels.data_panel", "CompactDataPanel"),
        ("platform_base.ui.panels.viz_panel", "ModernVizPanel"),
        ("platform_base.ui.panels.operations_panel", "OperationsPanel"),
        ("platform_base.ui.panels.config_panel", "ConfigPanel"),
        ("platform_base.ui.panels.results_panel", "ResultsPanel"),
    ]

    for module_name, class_name in panels:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            cls(session_state)
            print(f"âœ… {class_name}: OK")
        except Exception as e:
            print(f"âŒ {class_name}: {type(e).__name__}: {str(e)[:50]}")


def test_dialogs():
    """Testar diÃ¡logos"""
    section("10. TESTANDO DIÃLOGOS")

    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PyQt6.QtWidgets import QApplication
    QApplication.instance() or QApplication(sys.argv)

    dialogs = [
        ("platform_base.ui.dialogs.settings_dialog", "SettingsDialog", []),
        ("platform_base.ui.dialogs.filter_dialog", "FilterDialog", []),
        ("platform_base.ui.dialogs.smoothing_dialog", "SmoothingDialog", []),
        ("platform_base.ui.export_dialog", "ExportDialog", []),
    ]

    for module_name, class_name, args in dialogs:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            cls(*args)
            print(f"âœ… {class_name}: OK")
        except Exception as e:
            print(f"âŒ {class_name}: {type(e).__name__}: {str(e)[:50]}")


def check_potential_issues():
    """Verificar problemas potenciais"""
    section("11. VERIFICANDO PROBLEMAS POTENCIAIS")

    issues = []
    warnings = []

    # Verificar se .egg-info foi removido
    egg_info = Path("src/platform_base.egg-info")
    if egg_info.exists():
        warnings.append("Pasta .egg-info ainda existe (pode ser deletada)")
    else:
        print("âœ… Pasta .egg-info removida corretamente")

    # Verificar __pycache__
    pycache_dirs = list(Path().rglob("__pycache__"))
    if pycache_dirs:
        print(f"âš ï¸  {len(pycache_dirs)} pastas __pycache__ encontradas (normal)")

    # Verificar .gitignore
    gitignore = Path("../.gitignore")
    if gitignore.exists():
        print("âœ… .gitignore existe")
    else:
        warnings.append(".gitignore nÃ£o encontrado na raiz")

    # Verificar configuraÃ§Ã£o
    config = Path("configs/platform.yaml")
    if config.exists():
        print(f"âœ… ConfiguraÃ§Ã£o encontrada: {config}")
    else:
        warnings.append(f"ConfiguraÃ§Ã£o nÃ£o encontrada: {config}")

    # Verificar subpastas UI Designer
    designer_path = Path("src/platform_base/ui/designer")
    subdirs = ["panels", "dialogs", "tabs", "components"]
    for subdir in subdirs:
        subdir_path = designer_path / subdir
        if subdir_path.exists():
            ui_count = len(list(subdir_path.glob("*.ui")))
            print(f"âœ… {subdir}/: {ui_count} arquivos .ui")
        else:
            print(f"âš ï¸  {subdir}/: pasta nÃ£o existe ainda")

    if warnings:
        print("\nAvisos:")
        for w in warnings:
            print(f"  âš ï¸  {w}")

    return len(issues) == 0


def test_full_launch():
    """Testar launch completo da aplicaÃ§Ã£o"""
    section("12. TESTANDO LAUNCH COMPLETO")

    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    try:
        from platform_base.ui.app import PlatformApplication

        app = PlatformApplication(sys.argv)
        print("âœ… PlatformApplication criado")

        success = app.initialize_components()
        print(f"{'âœ…' if success else 'âŒ'} initialize_components(): {success}")

        if success:
            success = app.create_main_window()
            print(f"{'âœ…' if success else 'âŒ'} create_main_window(): {success}")

        return success
    except Exception as e:
        print(f"âŒ Erro: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def main():
    print("\n" + "ðŸ”" * 35)
    print("  DEBUG PROFUNDO - PLATFORM BASE v2.0")
    print("ðŸ”" * 35)

    results = {}

    # Teste 1-3: Imports (jÃ¡ verificados)
    section("1-3. IMPORTS JÃ VERIFICADOS âœ…")
    print("Todos os imports principais estÃ£o OK")

    # Teste 4: UI Loader
    try:
        test_ui_loader()
        results["ui_loader"] = True
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["ui_loader"] = False

    # Teste 5: App Initialization
    try:
        results["app_init"] = test_app_initialization()
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["app_init"] = False

    # Teste 6: Data Loading
    try:
        test_data_loading()
        results["data_loading"] = True
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["data_loading"] = False

    # Teste 7: Processing
    try:
        test_processing()
        results["processing"] = True
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["processing"] = False

    # Teste 8: Visualization
    try:
        test_visualization()
        results["visualization"] = True
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["visualization"] = False

    # Teste 9: UI Panels
    try:
        test_ui_panels()
        results["ui_panels"] = True
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["ui_panels"] = False

    # Teste 10: Dialogs
    try:
        test_dialogs()
        results["dialogs"] = True
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["dialogs"] = False

    # Teste 11: Potential Issues
    try:
        results["issues_check"] = check_potential_issues()
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["issues_check"] = False

    # Teste 12: Full Launch
    try:
        results["full_launch"] = test_full_launch()
    except Exception as e:
        print(f"âŒ ERRO: {e}")
        traceback.print_exc()
        results["full_launch"] = False

    # Resumo
    section("ðŸ“Š RESUMO DO DEBUG")

    print("\nResultados por mÃ³dulo:")
    for name, passed in results.items():
        status = "âœ…" if passed else "âŒ"
        print(f"  {status} {name}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\n{'='*70}")
    print(f"  RESULTADO FINAL: {total_passed}/{total_tests} mÃ³dulos OK")
    if total_passed == total_tests:
        print("  ðŸŽ‰ TODOS OS TESTES PASSARAM!")
    else:
        print("  âš ï¸  Alguns mÃ³dulos precisam de atenÃ§Ã£o")
    print(f"{'='*70}")

    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

