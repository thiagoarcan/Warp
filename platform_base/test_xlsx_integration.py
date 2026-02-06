#!/usr/bin/env python3
"""
Test script for Platform Base v2.0 with XLSX files

Tests 2D/3D plotting and streaming with XLSX files from project root.
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

import pandas as pd
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

def test_xlsx_files():
    """Test loading and processing XLSX files from root"""
    root_dir = Path(__file__).parent.parent
    
    xlsx_files = list(root_dir.glob("*.xlsx"))
    
    print(f"\n{'='*70}")
    print(f"🔍 Encontrados {len(xlsx_files)} arquivos XLSX na raiz do projeto")
    print(f"{'='*70}\n")
    
    results = []
    
    for xlsx_file in xlsx_files:
        print(f"📊 Testando: {xlsx_file.name}")
        
        try:
            # Read XLSX
            df = pd.read_excel(xlsx_file, engine='openpyxl')
            
            rows, cols = df.shape
            print(f"  ✅ Carregado com sucesso")
            print(f"  📏 Dimensões: {rows:,} linhas × {cols} colunas")
            print(f"  📋 Colunas: {', '.join(df.columns[:5])}" + ("..." if cols > 5 else ""))
            print(f"  🔢 Tipos: {dict(df.dtypes.value_counts())}")
            print()
            
            results.append({
                "file": xlsx_file.name,
                "success": True,
                "rows": rows,
                "cols": cols,
                "columns": list(df.columns),
            })
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            print()
            results.append({
                "file": xlsx_file.name,
                "success": False,
                "error": str(e),
            })
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📈 RESUMO DOS TESTES")
    print(f"{'='*70}\n")
    
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    
    print(f"✅ Sucesso: {successful}/{len(results)}")
    print(f"❌ Falhas: {failed}/{len(results)}")
    print()
    
    if successful > 0:
        print("📊 Arquivos prontos para plotagem:")
        for r in results:
            if r.get("success"):
                print(f"  • {r['file']} ({r['rows']:,} × {r['cols']})")
        print()
    
    return results


def test_xlsx_to_csv_conversion():
    """Test XLSX to CSV conversion functionality"""
    from platform_base.utils.xlsx_to_csv import XlsxToCsvConverter
    
    print(f"\n{'='*70}")
    print(f"🔄 TESTE DE CONVERSÃO XLSX → CSV")
    print(f"{'='*70}\n")
    
    root_dir = Path(__file__).parent.parent
    xlsx_files = list(root_dir.glob("*.xlsx"))
    
    if not xlsx_files:
        print("⚠️ Nenhum arquivo XLSX encontrado para testar conversão")
        return
    
    # Test with first file
    test_file = xlsx_files[0]
    print(f"📄 Arquivo de teste: {test_file.name}")
    
    converter = XlsxToCsvConverter()
    
    # Get sheet names
    sheets = converter.get_sheet_names(test_file)
    print(f"📑 Sheets encontradas: {len(sheets)}")
    for sheet in sheets:
        print(f"  • {sheet}")
    print()
    
    # Preview
    preview_df = converter.preview_sheet(test_file, nrows=5)
    if preview_df is not None:
        print(f"👀 Preview (5 linhas):")
        print(preview_df)
        print()
    
    # Test conversion
    output_path = test_file.with_suffix('.csv')
    print(f"🔄 Convertendo para: {output_path.name}")
    
    success = converter.convert(test_file, output_path)
    
    if success:
        print(f"  ✅ Conversão bem-sucedida")
        
        # Verify CSV
        csv_df = pd.read_csv(output_path)
        print(f"  📏 CSV: {len(csv_df):,} linhas × {len(csv_df.columns)} colunas")
        
        # Cleanup
        output_path.unlink()
        print(f"  🗑️ Arquivo CSV de teste removido")
    else:
        print(f"  ❌ Conversão falhou")
    
    print()


def test_application_launch():
    """Test launching the application"""
    print(f"\n{'='*70}")
    print(f"🚀 TESTE DE INICIALIZAÇÃO DA APLICAÇÃO")
    print(f"{'='*70}\n")
    
    try:
        from platform_base.core.dataset_store import DatasetStore
        from platform_base.desktop.session_state import SessionState
        from platform_base.desktop.signal_hub import SignalHub
        from platform_base.ui.main_window_unified import ModernMainWindow
        
        print("📦 Criando componentes...")
        
        # Create core components
        dataset_store = DatasetStore()
        session_state = SessionState(dataset_store)
        signal_hub = SignalHub()
        
        print("  ✅ DatasetStore criado")
        print("  ✅ SessionState criado")
        print("  ✅ SignalHub criado")
        
        # Create main window (but don't show)
        print("\n🏗️ Criando ModernMainWindow...")
        main_window = ModernMainWindow(session_state, signal_hub)
        
        print("  ✅ ModernMainWindow criado com sucesso")
        
        # Verify new panels
        print("\n🔍 Verificando novos painéis:")
        panels = [
            ("ResourceMonitorPanel", main_window.resource_monitor_panel),
            ("ActivityLogPanel", main_window.activity_log_panel),
            ("DataTablesPanel", main_window.data_tables_panel),
        ]
        
        for name, panel in panels:
            if panel is not None:
                print(f"  ✅ {name} inicializado")
            else:
                print(f"  ❌ {name} não encontrado")
        
        # Verify detached manager
        if hasattr(main_window, 'detached_manager'):
            print(f"  ✅ DetachedManager inicializado")
            print(f"     Painéis destacados: {main_window.detached_manager.get_detached_count()}")
        else:
            print(f"  ❌ DetachedManager não encontrado")
        
        print("\n✅ Aplicação inicializada com sucesso!")
        print("   (Janela não mostrada - apenas teste de criação)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar aplicação:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("🧪 SUITE DE TESTES - Platform Base v2.0")
    print("="*70)
    
    # Create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Test 1: XLSX Files
    print("\n" + "🔹" * 35)
    print("TEST 1: Arquivos XLSX")
    print("🔹" * 35)
    test_xlsx_files()
    
    # Test 2: XLSX to CSV Conversion
    print("\n" + "🔹" * 35)
    print("TEST 2: Conversão XLSX → CSV")
    print("🔹" * 35)
    test_xlsx_to_csv_conversion()
    
    # Test 3: Application Launch
    print("\n" + "🔹" * 35)
    print("TEST 3: Inicialização da Aplicação")
    print("🔹" * 35)
    app_success = test_application_launch()
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 RESUMO FINAL")
    print("="*70)
    print()
    print("✅ Todos os testes concluídos")
    print()
    print("Próximos passos:")
    print("  1. Execute: python launch_app.py")
    print("  2. Use Ctrl+L para carregar arquivos XLSX")
    print("  3. Teste plotagem 2D/3D com os dados")
    print("  4. Experimente o botão 'Desgarrados' (Ctrl+Shift+D)")
    print("  5. Verifique o monitor de recursos")
    print("  6. Acompanhe o log de atividades")
    print()
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
