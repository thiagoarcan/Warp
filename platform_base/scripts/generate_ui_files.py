#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar arquivos .ui automaticamente a partir de arquivos Python

Este script varre os diretórios de UI e cria arquivos .ui correspondentes
com uma estrutura básica, permitindo depois refiná-los no Qt Designer.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Corrigir encoding no Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Template básico para arquivo .ui
UI_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>{class_name}</class>
 <widget class="{base_widget}" name="{widget_name}">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>{title}</string>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QLabel" name="label">
     <property name="text">
      <string>{placeholder}</string>
     </property>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
"""

def extract_class_info(py_file: Path) -> List[Tuple[str, str, str]]:
    """
    Extrai informações de classes de um arquivo Python
    
    Returns:
        Lista de tuplas (nome_classe, classe_base, nome_widget)
    """
    try:
        content = py_file.read_text(encoding='utf-8')
        
        # Padrão para encontrar class definitions
        pattern = r'class\s+(\w+)\s*\(.*?([QDialog|QWidget|QMainWindow]+).*?\):'
        matches = re.finditer(pattern, content)
        
        results = []
        for match in matches:
            class_name = match.group(1)
            base_widget = 'QDialog'  # default
            
            # Determinar classe base
            if 'QMainWindow' in match.group(0):
                base_widget = 'QMainWindow'
            elif 'QDialog' in match.group(0):
                base_widget = 'QDialog'
            elif 'QWidget' in match.group(0):
                base_widget = 'QWidget'
            
            widget_name = class_name[0].lower() + class_name[1:] if class_name else 'widget'
            results.append((class_name, base_widget, widget_name))
        
        return results
    except Exception as e:
        print(f"Error processing {py_file}: {e}")
        return []

def generate_ui_file(class_name: str, base_widget: str, widget_name: str, output_path: Path):
    """Gera arquivo .ui para uma classe"""
    
    title = ' '.join(re.findall('[A-Z][a-z]*', class_name))
    placeholder = f"UI for {class_name}"
    
    content = UI_TEMPLATE.format(
        class_name=class_name,
        base_widget=base_widget,
        widget_name=widget_name,
        title=title,
        placeholder=placeholder
    )
    
    output_path.write_text(content, encoding='utf-8')
    print(f"[OK] Generated: {output_path}")

def main():
    """Processa todos os arquivos Python e gera .ui files"""
    
    base_path = Path(__file__).parent.parent
    
    # Diretórios a processar
    dirs_to_process = [
        'src/platform_base/ui',
        'src/platform_base/desktop/widgets',
        'src/platform_base/desktop/dialogs',
    ]
    
    ui_output_base = Path('src/platform_base/desktop/ui_files')
    
    total_generated = 0
    
    for dir_path in dirs_to_process:
        py_dir = base_path / dir_path
        if not py_dir.exists():
            print(f"[WARN] Directory not found: {py_dir}")
            continue
        
        print(f"\nProcessing {dir_path}...")
        
        for py_file in py_dir.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            
            classes = extract_class_info(py_file)
            
            for class_name, base_widget, widget_name in classes:
                # Pular classes que já têm .ui (começam com 'Ui_')
                if class_name.startswith('Ui_'):
                    continue
                
                ui_filename = f"{widget_name}.ui"
                ui_path = ui_output_base / ui_filename
                
                # Não sobrescrever .ui existentes
                if ui_path.exists():
                    print(f"  [SKIP] {ui_filename} (already exists)")
                    continue
                
                generate_ui_file(class_name, base_widget, widget_name, ui_path)
                total_generated += 1
    
    print(f"\n[DONE] Total .ui files generated: {total_generated}")

if __name__ == '__main__':
    main()
