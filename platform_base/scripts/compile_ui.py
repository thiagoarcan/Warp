"""
Build system para compilar arquivos .ui do Qt Designer em Python

Converte arquivos .ui em módulos Python usando pyuic6
"""

import subprocess
import sys
from pathlib import Path
from typing import List


def compile_ui_files(ui_dir: Path, output_dir: Path) -> List[str]:
    """
    Compila todos os arquivos .ui em um diretório
    
    Args:
        ui_dir: Diretório contendo arquivos .ui
        output_dir: Diretório para salvar arquivos Python compilados
        
    Returns:
        Lista de arquivos compilados com sucesso
    """
    compiled = []
    
    if not ui_dir.exists():
        print(f"[ERROR] UI directory not found: {ui_dir}")
        return compiled
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ui_files = list(ui_dir.glob('*.ui'))
    if not ui_files:
        print(f"[INFO] No .ui files found in {ui_dir}")
        return compiled
    
    print(f"[INFO] Compiling {len(ui_files)} .ui files...")
    
    for ui_file in ui_files:
        try:
            # Nome do arquivo Python de saída
            py_filename = f"ui_{ui_file.stem}.py"
            py_path = output_dir / py_filename
            
            # Comando pyuic6
            cmd = [sys.executable, '-m', 'PyQt6.uic', str(ui_file), '-o', str(py_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[WARN] Failed to compile {ui_file.name}: {result.stderr}")
                continue
            
            print(f"[OK] Compiled {ui_file.name} -> {py_filename}")
            compiled.append(py_filename)
            
        except Exception as e:
            print(f"[ERROR] Exception compiling {ui_file.name}: {e}")
            continue
    
    return compiled

def main():
    """Compila todos os arquivos .ui do projeto"""
    base_path = Path(__file__).parent.parent
    
    ui_dirs = [
        base_path / 'src/platform_base/desktop/ui_files',
        base_path / 'src/platform_base/ui/ui_files',
    ]
    
    output_dir = base_path / 'src/platform_base/desktop/ui_compiled'
    
    total_compiled = 0
    
    for ui_dir in ui_dirs:
        if ui_dir.exists():
            compiled = compile_ui_files(ui_dir, output_dir)
            total_compiled += len(compiled)
    
    print(f"\n[DONE] Total files compiled: {total_compiled}")
    
    # Criar __init__.py no diretório de saída
    init_file = output_dir / '__init__.py'
    if not init_file.exists():
        init_file.write_text('"""Compiled UI files from Qt Designer"""\n')
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
