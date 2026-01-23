#!/usr/bin/env python3
"""
Teste simples para verificar carregamento de arquivo sem interface
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_simple_load():
    """Teste básico de carregamento"""
    try:
        from platform_base.io.loader import load, LoadConfig, get_file_info
        
        # Arquivo de teste
        test_file = r"C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Warp\BAR_FT-OP10.xlsx"
        
        print(f"Testando arquivo: {test_file}")
        
        # 1. Test file info
        print("1. Obtendo informacoes do arquivo...")
        file_info = get_file_info(test_file)
        print(f"   Info: {file_info}")
        
        # 2. Test load
        print("2. Carregando dados...")
        config = LoadConfig()
        dataset = load(test_file, config)
        print(f"   Dataset carregado: {len(dataset.series)} series, {len(dataset.t_seconds)} pontos")
        
        # 3. Test series
        print("3. Verificando series...")
        for series_id, series in dataset.series.items():
            print(f"   {series.name}: {len(series.values)} valores, unidade: {series.unit}")
        
        print("TESTE BASICO: SUCESSO!")
        return True
        
    except Exception as e:
        print(f"ERRO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_load()