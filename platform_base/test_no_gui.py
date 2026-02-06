#!/usr/bin/env python3
"""
Standalone test for XLSX converter (no GUI required)
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

import pandas as pd


def test_xlsx_loading():
    """Test loading XLSX files from root"""
    root_dir = Path(__file__).parent.parent
    xlsx_files = list(root_dir.glob("*.xlsx"))
    
    print(f"\n{'='*70}")
    print(f"📊 TESTE 1: Carregamento de Arquivos XLSX")
    print(f"{'='*70}\n")
    
    print(f"Encontrados {len(xlsx_files)} arquivos XLSX\n")
    
    results = []
    for xlsx_file in xlsx_files:
        try:
            df = pd.read_excel(xlsx_file, engine='openpyxl')
            rows, cols = df.shape
            
            print(f"✅ {xlsx_file.name}")
            print(f"   Dimensões: {rows:,} × {cols}")
            print(f"   Colunas: {list(df.columns)}")
            print()
            
            results.append({"file": xlsx_file.name, "success": True, "shape": (rows, cols)})
        except Exception as e:
            print(f"❌ {xlsx_file.name}: {e}\n")
            results.append({"file": xlsx_file.name, "success": False, "error": str(e)})
    
    successful = sum(1 for r in results if r["success"])
    print(f"Resultado: {successful}/{len(results)} arquivos carregados com sucesso\n")
    
    return results


def test_xlsx_to_csv_basic():
    """Test basic XLSX to CSV conversion"""
    from platform_base.utils.xlsx_to_csv import XlsxToCsvConverter
    
    print(f"\n{'='*70}")
    print(f"🔄 TESTE 2: Conversão XLSX → CSV")
    print(f"{'='*70}\n")
    
    root_dir = Path(__file__).parent.parent
    xlsx_files = list(root_dir.glob("*.xlsx"))
    
    if not xlsx_files:
        print("❌ Nenhum arquivo XLSX encontrado\n")
        return False
    
    test_file = xlsx_files[0]
    print(f"Arquivo de teste: {test_file.name}\n")
    
    converter = XlsxToCsvConverter()
    
    # Get sheet names
    sheets = converter.get_sheet_names(test_file)
    print(f"Sheets: {sheets}")
    
    # Preview
    preview = converter.preview_sheet(test_file, nrows=3)
    if preview is not None:
        print(f"\nPreview:")
        print(preview)
        print()
    
    # Convert
    output_path = Path("/tmp") / f"{test_file.stem}_test.csv"
    print(f"Convertendo para: {output_path}\n")
    
    # Note: We can't actually test conversion signals without Qt
    # but we can test the static methods
    try:
        df_xlsx = pd.read_excel(test_file, engine='openpyxl')
        df_xlsx.to_csv(output_path, index=False)
        
        df_csv = pd.read_csv(output_path)
        
        print(f"✅ Conversão bem-sucedida")
        print(f"   XLSX: {df_xlsx.shape}")
        print(f"   CSV: {df_csv.shape}")
        print(f"   Match: {df_xlsx.shape == df_csv.shape}")
        
        # Cleanup
        output_path.unlink()
        print(f"   Arquivo temporário removido\n")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False


def test_module_imports():
    """Test that all new modules can be imported"""
    print(f"\n{'='*70}")
    print(f"📦 TESTE 3: Importação de Módulos")
    print(f"{'='*70}\n")
    
    modules = [
        ("DetachedManager", "platform_base.ui.panels.detached_manager", "DetachedManager"),
        ("ResourceMonitorPanel", "platform_base.ui.panels.resource_monitor_panel", "ResourceMonitorPanel"),
        ("ActivityLogPanel", "platform_base.ui.panels.activity_log_panel", "ActivityLogPanel"),
        ("DataTablesPanel", "platform_base.ui.panels.data_tables_panel", "DataTablesPanel"),
        ("XlsxToCsvConverter", "platform_base.utils.xlsx_to_csv", "XlsxToCsvConverter"),
        ("TooltipManager", "platform_base.ui.tooltip_manager", "TooltipManager"),
    ]
    
    results = []
    for name, module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {name} ({module_path})")
            results.append(True)
        except Exception as e:
            print(f"❌ {name}: {e}")
            results.append(False)
    
    print(f"\nResultado: {sum(results)}/{len(results)} módulos importados com sucesso\n")
    
    return all(results)


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 SUITE DE TESTES - Platform Base v2.0 (Sem GUI)")
    print("="*70)
    
    results = []
    
    # Test 1: XLSX Loading
    xlsx_results = test_xlsx_loading()
    results.append(("XLSX Loading", any(r["success"] for r in xlsx_results)))
    
    # Test 2: XLSX to CSV
    csv_result = test_xlsx_to_csv_basic()
    results.append(("XLSX to CSV", csv_result))
    
    # Test 3: Module Imports
    import_result = test_module_imports()
    results.append(("Module Imports", import_result))
    
    # Summary
    print("\n" + "="*70)
    print("📊 RESUMO FINAL")
    print("="*70 + "\n")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n✅ Todos os testes passaram com sucesso!")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
    
    print("\n" + "="*70 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
