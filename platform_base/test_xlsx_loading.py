"""
Test script para validar carregamento de arquivos xlsx

Este script testa se os 8 arquivos xlsx mencionados na auditoria
podem ser carregados corretamente pelo sistema.
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_xlsx_loading():
    """Testa carregamento de arquivos xlsx"""
    from pathlib import Path

    import pandas as pd

    # Lista de arquivos para testar
    xlsx_files = [
        "BAR_DT-OP10.xlsx",
        "BAR_FT-OP10.xlsx", 
        "BAR_PT-OP10.xlsx",
        "BAR_TT-OP10.xlsx",
        "Original.xlsx",
        "PLN_DT-OP10.xlsx",
        "PLN_FT-OP10.xlsx",
        "PLN_PT-OP10.xlsx",
    ]
    
    base_path = Path(__file__).parent.parent  # Warp directory
    
    results = []
    
    print("=" * 60)
    print("🔍 TESTE DE CARREGAMENTO DE ARQUIVOS XLSX")
    print("=" * 60)
    
    for filename in xlsx_files:
        filepath = base_path / filename
        
        result = {
            'file': filename,
            'exists': filepath.exists(),
            'loaded': False,
            'rows': 0,
            'cols': 0,
            'error': None
        }
        
        if filepath.exists():
            try:
                df = pd.read_excel(filepath)
                result['loaded'] = True
                result['rows'] = len(df)
                result['cols'] = len(df.columns)
                print(f"✅ {filename}: {result['rows']} linhas x {result['cols']} colunas")
            except Exception as e:
                result['error'] = str(e)
                print(f"❌ {filename}: ERRO - {e}")
        else:
            print(f"⚠️  {filename}: ARQUIVO NÃO ENCONTRADO")
        
        results.append(result)
    
    print("=" * 60)
    
    # Resumo
    found = sum(1 for r in results if r['exists'])
    loaded = sum(1 for r in results if r['loaded'])
    total = len(results)
    
    print(f"\n📊 RESUMO:")
    print(f"   Arquivos encontrados: {found}/{total}")
    print(f"   Arquivos carregados:  {loaded}/{total}")
    
    if loaded == total:
        print("\n🎉 TODOS OS ARQUIVOS XLSX PODEM SER CARREGADOS!")
        return True
    else:
        print("\n⚠️  ALGUNS ARQUIVOS NÃO PUDERAM SER CARREGADOS")
        return False


def test_loader_module():
    """Testa se o módulo loader suporta xlsx"""
    try:
        from platform_base.io.loader import FileFormat, LoadConfig, LoadStrategy
        
        print("\n" + "=" * 60)
        print("🔧 TESTE DO MÓDULO LOADER")
        print("=" * 60)
        
        # Testa detecção de formato
        xlsx_format = FileFormat.from_extension('.xlsx')
        print(f"✅ Formato xlsx detectado: {xlsx_format}")
        
        xls_format = FileFormat.from_extension('.xls')
        print(f"✅ Formato xls detectado: {xls_format}")
        
        # Testa estratégia de carregamento
        strategy = LoadStrategy(format=xlsx_format)
        print(f"✅ LoadStrategy criada para xlsx")
        
        # Verifica LoadConfig
        config = LoadConfig()
        print(f"✅ LoadConfig default: sheet_name={config.sheet_name}")
        
        print("\n🎉 MÓDULO LOADER SUPORTA XLSX CORRETAMENTE!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🚀 Iniciando testes..." + "\n")
    
    test1 = test_xlsx_loading()
    test2 = test_loader_module()
    
    print("\n" + "=" * 60)
    print("📋 RESULTADO FINAL")
    print("=" * 60)
    
    if test1 and test2:
        print("✅ Todos os testes passaram!")
        sys.exit(0)
    else:
        print("❌ Alguns testes falharam")
        sys.exit(1)
