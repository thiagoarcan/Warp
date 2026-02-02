#!/usr/bin/env python
"""
Script de migração automática de classes Python para usar arquivos .ui

Este script modifica as classes Python para:
1. Herdar de UiLoaderMixin
2. Carregar o arquivo .ui correspondente
3. Manter fallback para criação programática

Fase 2 - Conexão das classes aos arquivos .ui
"""

import re
from pathlib import Path
from typing import NamedTuple


class MigrationTarget(NamedTuple):
    """Alvo de migração"""
    py_file: str  # Caminho relativo do arquivo .py
    class_name: str  # Nome da classe
    ui_file: str  # Nome do arquivo .ui
    widget_mappings: dict[str, str]  # Mapeamento: nome_no_ui -> nome_no_codigo


BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src" / "platform_base"

# Lista de migrações a realizar
# O DataPanel já foi migrado manualmente como exemplo

MIGRATIONS = [
    MigrationTarget(
        py_file="desktop/widgets/viz_panel.py",
        class_name="VizPanel",
        ui_file="vizPanel.ui",
        widget_mappings={
            "plotToolbar": "plot_toolbar",
            "mainSplitter": "main_splitter",
            "plotTabs": "plot_tabs",
            "controlsWidget": "controls_widget",
            "settingsGroup": "settings_group",
            "seriesGroup": "series_group",
        }
    ),
    MigrationTarget(
        py_file="desktop/widgets/config_panel.py",
        class_name="ConfigPanel",
        ui_file="configPanel.ui",
        widget_mappings={
            "operationCombo": "operation_combo",
            "configTabs": "config_tabs",
            "executeBtn": "execute_btn",
            "previewBtn": "preview_btn",
            "historyList": "history_list",
        }
    ),
    MigrationTarget(
        py_file="desktop/widgets/results_panel.py",
        class_name="ResultsPanel",
        ui_file="resultsPanel.ui",
        widget_mappings={
            "resultsTabs": "results_tabs",
            "resultsTable": "results_table",
            "logsText": "logs_text",
            "qualityChart": "quality_chart",
            "exportBtn": "export_btn",
            "clearBtn": "clear_btn",
        }
    ),
    MigrationTarget(
        py_file="desktop/dialogs/upload_dialog.py",
        class_name="UploadDialog",
        ui_file="uploadDialog.ui",
        widget_mappings={
            "filePathEdit": "file_path_edit",
            "browseBtn": "browse_btn",
            "configTabs": "config_tabs",
            "progressBar": "progress_bar",
            "previewTable": "preview_table",
            "buttonBox": "button_box",
        }
    ),
    MigrationTarget(
        py_file="desktop/dialogs/settings_dialog.py",
        class_name="SettingsDialog",
        ui_file="settingsDialog.ui",
        widget_mappings={
            "settingsTabs": "settings_tabs",
            "buttonBox": "button_box",
        }
    ),
]


def generate_import_block() -> str:
    """Gera o bloco de import do UiLoaderMixin"""
    return "from platform_base.ui.ui_loader_mixin import UiLoaderMixin"


def modify_class_declaration(content: str, class_name: str, base_class: str = "QWidget") -> str:
    """Modifica declaração da classe para incluir UiLoaderMixin"""
    # Padrão: class ClassName(QWidget):
    pattern = rf"class {class_name}\(({base_class})\):"
    replacement = rf"class {class_name}(\1, UiLoaderMixin):"
    
    new_content = re.sub(pattern, replacement, content)
    
    # Se não encontrou QWidget, tentar QDialog
    if new_content == content and base_class == "QWidget":
        return modify_class_declaration(content, class_name, "QDialog")
    
    return new_content


def add_ui_file_constant(content: str, class_name: str, ui_file: str) -> str:
    """Adiciona constante UI_FILE após a docstring da classe"""
    # Encontrar a docstring da classe
    class_pattern = rf'(class {class_name}\([^)]+\):\s*"""[^"]*""")'
    
    def replacement(match):
        original = match.group(1)
        return f'{original}\n    \n    # Arquivo .ui que define a interface\n    UI_FILE = "desktop/ui_files/{ui_file}"'
    
    return re.sub(class_pattern, replacement, content, flags=re.DOTALL)


def add_load_ui_call(content: str) -> str:
    """Adiciona chamada a _load_ui() no __init__"""
    # Procurar por self._setup_ui() e adicionar _load_ui() antes
    pattern = r'(\s+)(self\._setup_ui\(\))'
    
    replacement = r'''\1# Carregar interface do arquivo .ui
\1if not self._load_ui():
\1    # Fallback para criação programática se .ui falhar
\1    logger.warning("ui_load_failed_using_fallback", cls=self.__class__.__name__)
\1    self._setup_ui_fallback()
\1else:
\1    self._setup_ui_from_file()
\1
\1# Conectar signals (comum a ambos os modos)'''
    
    return re.sub(pattern, replacement, content)


def rename_setup_ui_to_fallback(content: str) -> str:
    """Renomeia _setup_ui para _setup_ui_fallback"""
    return content.replace("def _setup_ui(self):", "def _setup_ui_fallback(self):")


def add_setup_ui_from_file(content: str, class_name: str, widget_mappings: dict) -> str:
    """Adiciona método _setup_ui_from_file"""
    mappings_code = "\n        ".join([
        f"self.{py_name} = self.{ui_name}"
        for ui_name, py_name in widget_mappings.items()
    ])
    
    method = f'''
    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Os widgets já existem como atributos (criados pelo uic.loadUi)
        # Aqui apenas configuramos comportamentos dinâmicos
        
        # Manter referências com nomes usados no código existente
        {mappings_code}
        
        # TODO: Configurar comportamentos específicos
        pass

'''
    
    # Inserir antes do _setup_ui_fallback ou _connect_signals
    insert_point = content.find("def _setup_ui_fallback(self):")
    if insert_point == -1:
        insert_point = content.find("def _connect_signals(self):")
    
    if insert_point != -1:
        return content[:insert_point] + method + content[insert_point:]
    
    return content


def migrate_file(target: MigrationTarget, dry_run: bool = True) -> bool:
    """Migra um arquivo para usar .ui"""
    file_path = SRC_DIR / target.py_file
    
    if not file_path.exists():
        print(f"  ❌ Arquivo não encontrado: {target.py_file}")
        return False
    
    content = file_path.read_text(encoding="utf-8")
    original_content = content
    
    # 1. Verificar se já foi migrado
    if "UiLoaderMixin" in content:
        print(f"  ✅ {target.class_name} já migrado")
        return True
    
    # 2. Adicionar import
    if "from platform_base.ui.ui_loader_mixin import UiLoaderMixin" not in content:
        # Encontrar último import de platform_base
        last_import_pos = content.rfind("from platform_base")
        if last_import_pos != -1:
            # Encontrar fim da linha
            end_line = content.find("\n", last_import_pos)
            content = content[:end_line+1] + generate_import_block() + "\n" + content[end_line+1:]
    
    # 3. Modificar declaração da classe
    content = modify_class_declaration(content, target.class_name)
    
    # 4. Adicionar UI_FILE
    content = add_ui_file_constant(content, target.class_name, target.ui_file)
    
    if dry_run:
        print(f"  🔄 {target.class_name} - Migração seria aplicada")
        # Mostrar diff resumido
        if content != original_content:
            print(f"     Mudanças: +UiLoaderMixin, +UI_FILE={target.ui_file}")
        return True
    else:
        # Salvar arquivo modificado
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✅ {target.class_name} migrado para usar {target.ui_file}")
        return True


def main():
    """Executa migração"""
    import sys
    
    dry_run = "--apply" not in sys.argv
    
    print("=" * 70)
    print("🔄 MIGRAÇÃO FASE 2 - CONEXÃO CLASSES PYTHON ↔ ARQUIVOS .UI")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  MODO DRY-RUN - Nenhuma alteração será feita")
        print("    Use --apply para aplicar as mudanças\n")
    else:
        print("\n🔧 APLICANDO MUDANÇAS...\n")
    
    success_count = 0
    fail_count = 0
    
    for target in MIGRATIONS:
        print(f"\n📄 {target.class_name} ({target.py_file})")
        if migrate_file(target, dry_run):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"""
   Total de classes: {len(MIGRATIONS)}
   ✅ Migradas: {success_count}
   ❌ Falhas: {fail_count}
""")
    
    if dry_run:
        print("Execute com --apply para aplicar as mudanças:")
        print("  python scripts/auto_migrate_ui.py --apply")


if __name__ == "__main__":
    main()
