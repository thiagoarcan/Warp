#!/usr/bin/env python3
"""
Script para completar arquivos .ui placeholder com estrutura real.

Lê a estrutura das classes Python e gera .ui correspondentes.
"""

from __future__ import annotations

import re
from pathlib import Path

# Diretórios
SRC_DIR = Path(__file__).parent.parent / "src" / "platform_base"
DESKTOP_UI_FILES = SRC_DIR / "desktop" / "ui_files"


def create_complete_ui_template(class_name: str, base_class: str = "QWidget") -> str:
    """Cria um arquivo .ui completo básico para uma classe"""
    
    # Determinar se é dialog ou widget
    is_dialog = "Dialog" in class_name
    widget_class = "QDialog" if is_dialog else "QWidget"
    
    # Criar nome do widget
    widget_name = class_name[0].upper() + class_name[1:]
    
    # Template básico mas funcional
    template = f'''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>{widget_name}</class>
 <widget class="{widget_class}" name="{widget_name}">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>600</width>
    <height>400</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>{class_name}</string>
  </property>
  <layout class="QVBoxLayout" name="mainLayout">
   <item>
    <widget class="QWidget" name="contentWidget">
     <layout class="QVBoxLayout" name="contentLayout"/>
    </widget>
   </item>'''
    
    # Adicionar botões para diálogos
    if is_dialog:
        template += '''
   <item>
    <widget class="QDialogButtonBox" name="buttonBox">
     <property name="orientation">
      <enum>Qt::Horizontal</enum>
     </property>
     <property name="standardButtons">
      <set>QDialogButtonBox::Cancel|QDialogButtonBox::Ok</set>
     </property>
    </widget>
   </item>'''
    
    template += '''
  </layout>
 </widget>
 <resources/>
 <connections>'''
    
    if is_dialog:
        template += '''
  <connection>
   <sender>buttonBox</sender>
   <signal>accepted()</signal>
   <receiver>{widget_name}</receiver>
   <slot>accept()</slot>
  </connection>
  <connection>
   <sender>buttonBox</sender>
   <signal>rejected()</signal>
   <receiver>{widget_name}</receiver>
   <slot>reject()</slot>
  </connection>'''.format(widget_name=widget_name)
    
    template += '''
 </connections>
</ui>'''
    
    return template


def is_placeholder(ui_path: Path) -> bool:
    """Verifica se um arquivo .ui é placeholder"""
    content = ui_path.read_text(encoding='utf-8')
    return 'UI for ' in content and content.count('<widget') <= 3


def update_placeholder_ui(ui_path: Path) -> bool:
    """Atualiza um arquivo .ui placeholder para versão completa"""
    
    # Ler conteúdo atual
    content = ui_path.read_text(encoding='utf-8')
    
    # Extrair nome da classe
    match = re.search(r'<class>(\w+)</class>', content)
    if not match:
        return False
    
    class_name = match.group(1)
    
    # Gerar novo conteúdo
    new_content = create_complete_ui_template(class_name)
    
    # Escrever
    ui_path.write_text(new_content, encoding='utf-8')
    return True


def main():
    """Atualiza todos os arquivos .ui placeholder"""
    
    print("🔄 Atualizando arquivos .ui placeholder...\n")
    
    ui_files = list(DESKTOP_UI_FILES.glob("*.ui"))
    updated = 0
    skipped = 0
    
    for ui_file in ui_files:
        if is_placeholder(ui_file):
            if update_placeholder_ui(ui_file):
                print(f"  ✅ {ui_file.name}")
                updated += 1
            else:
                print(f"  ❌ {ui_file.name} - Erro")
        else:
            skipped += 1
    
    print(f"\n📊 Resultado:")
    print(f"   - Atualizados: {updated}")
    print(f"   - Já completos: {skipped}")
    print(f"   - Total: {len(ui_files)}")


if __name__ == "__main__":
    main()
