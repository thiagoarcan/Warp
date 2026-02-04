#!/usr/bin/env python3
"""
validate_ui_migration.py - Script de validação para migração de UI

Verifica:
1. Correspondência entre classes Python e arquivos .ui
2. Widgets programáticos que precisam de migração
3. Arquivos .ui existentes mas não utilizados
4. Promoted widgets configurados corretamente
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Diretórios do projeto
PROJECT_ROOT = Path(__file__).parent.parent
SRC_ROOT = PROJECT_ROOT / "src" / "platform_base"
UI_FILES_DIR = SRC_ROOT / "desktop" / "ui_files"
DESIGNER_DIR = SRC_ROOT / "ui" / "designer"


@dataclass
class UIComponent:
    """Representa um componente de UI identificado"""
    class_name: str
    file_path: Path
    base_classes: list[str] = field(default_factory=list)
    ui_file: str | None = None
    uses_ui_loader_mixin: bool = False
    has_fallback: bool = False
    is_programmatic: bool = True
    widgets_created: list[str] = field(default_factory=list)
    custom_widgets_used: list[str] = field(default_factory=list)


@dataclass
class UIFile:
    """Representa um arquivo .ui"""
    file_path: Path
    class_name: str | None = None
    widgets: list[str] = field(default_factory=list)
    promoted_widgets: list[str] = field(default_factory=list)
    is_used: bool = False
    used_by: str | None = None


class UIASTVisitor(ast.NodeVisitor):
    """Visitor AST para identificar componentes de UI"""
    
    UI_BASE_CLASSES = {
        'QWidget', 'QDialog', 'QMainWindow', 'QDockWidget',
        'QFrame', 'QGroupBox', 'QScrollArea', 'QSplitter',
        'QTabWidget', 'QToolBar', 'QStatusBar', 'QMenuBar'
    }
    
    UI_WIDGET_TYPES = {
        'QPushButton', 'QLabel', 'QLineEdit', 'QTextEdit',
        'QComboBox', 'QSpinBox', 'QDoubleSpinBox', 'QCheckBox',
        'QRadioButton', 'QSlider', 'QProgressBar', 'QTabWidget',
        'QTreeWidget', 'QTableWidget', 'QListWidget', 'QStackedWidget',
        'QGroupBox', 'QFrame', 'QSplitter', 'QScrollArea',
        'QToolBar', 'QMenuBar', 'QStatusBar', 'QDockWidget'
    }
    
    LAYOUT_TYPES = {
        'QVBoxLayout', 'QHBoxLayout', 'QGridLayout', 'QFormLayout',
        'QStackedLayout', 'QBoxLayout'
    }
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.components: list[UIComponent] = []
        self.current_class: UIComponent | None = None
        
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """Visita definição de classe"""
        # Verificar se herda de classes Qt
        base_names = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)
                
        # Verificar se é componente de UI
        is_ui_component = any(
            base in self.UI_BASE_CLASSES or base == 'UiLoaderMixin'
            for base in base_names
        )
        
        if is_ui_component:
            component = UIComponent(
                class_name=node.name,
                file_path=self.file_path,
                base_classes=base_names,
                uses_ui_loader_mixin='UiLoaderMixin' in base_names
            )
            
            # Verificar atributos de classe
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == 'UI_FILE':
                            if isinstance(item.value, ast.Constant):
                                component.ui_file = item.value.value
                                component.is_programmatic = False
                                
            self.current_class = component
            self.generic_visit(node)
            self.components.append(component)
            self.current_class = None
        else:
            self.generic_visit(node)
            
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Visita definição de função/método"""
        if self.current_class is None:
            return
            
        # Detectar métodos de fallback
        if '_setup_ui_fallback' in node.name or '_setup_ui' in node.name:
            self.current_class.has_fallback = True
            self.current_class.is_programmatic = True
            
        self.generic_visit(node)
        
    def visit_Call(self, node: ast.Call) -> Any:
        """Visita chamadas de função"""
        if self.current_class is None:
            self.generic_visit(node)
            return
            
        # Detectar criação de widgets
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            
        if func_name:
            if func_name in self.UI_WIDGET_TYPES:
                self.current_class.widgets_created.append(func_name)
            elif func_name in self.LAYOUT_TYPES:
                self.current_class.widgets_created.append(func_name)
            # Detectar widgets customizados (PascalCase terminando em Widget/Dialog/Panel)
            elif re.match(r'^[A-Z][a-zA-Z]*(?:Widget|Dialog|Panel|Canvas)$', func_name):
                self.current_class.custom_widgets_used.append(func_name)
                
        self.generic_visit(node)


def scan_python_files() -> list[UIComponent]:
    """Escaneia arquivos Python em busca de componentes de UI"""
    components: list[UIComponent] = []
    
    # Diretórios a escanear
    scan_dirs = [
        SRC_ROOT / "desktop",
        SRC_ROOT / "ui",
        SRC_ROOT / "viz",
    ]
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
            
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            if "_ui.py" in py_file.name:  # Ignorar arquivos gerados
                continue
                
            try:
                source = py_file.read_text(encoding='utf-8')
                tree = ast.parse(source)
                visitor = UIASTVisitor(py_file)
                visitor.visit(tree)
                components.extend(visitor.components)
            except SyntaxError as e:
                print(f"⚠️ Erro de sintaxe em {py_file}: {e}")
            except Exception as e:
                print(f"⚠️ Erro ao processar {py_file}: {e}")
                
    return components


def scan_ui_files() -> list[UIFile]:
    """Escaneia arquivos .ui existentes"""
    ui_files: list[UIFile] = []
    
    for ui_dir in [UI_FILES_DIR, DESIGNER_DIR]:
        if not ui_dir.exists():
            continue
            
        for ui_path in ui_dir.glob("*.ui"):
            ui_file = UIFile(file_path=ui_path)
            
            try:
                content = ui_path.read_text(encoding='utf-8')
                
                # Extrair nome da classe
                class_match = re.search(r'<class>(\w+)</class>', content)
                if class_match:
                    ui_file.class_name = class_match.group(1)
                    
                # Extrair widgets
                widget_matches = re.findall(r'<widget class="(\w+)"', content)
                ui_file.widgets = list(set(widget_matches))
                
                # Extrair promoted widgets
                promoted_matches = re.findall(
                    r'<customwidget>\s*<class>(\w+)</class>',
                    content,
                    re.DOTALL
                )
                ui_file.promoted_widgets = list(set(promoted_matches))
                
            except Exception as e:
                print(f"⚠️ Erro ao processar {ui_path}: {e}")
                
            ui_files.append(ui_file)
            
    return ui_files


def correlate_components_and_files(
    components: list[UIComponent],
    ui_files: list[UIFile]
) -> None:
    """Correlaciona componentes Python com arquivos .ui"""
    ui_by_name = {}
    for ui in ui_files:
        if ui.class_name:
            ui_by_name[ui.class_name] = ui
        # Também indexar pelo nome do arquivo (sem extensão)
        stem = ui.file_path.stem
        # Converter camelCase para PascalCase se necessário
        pascal_name = stem[0].upper() + stem[1:] if stem else ""
        ui_by_name[pascal_name] = ui
        
    for comp in components:
        # Verificar se tem UI_FILE definido
        if comp.ui_file:
            for ui in ui_files:
                if comp.ui_file.endswith(ui.file_path.name):
                    ui.is_used = True
                    ui.used_by = comp.class_name
                    break
        else:
            # Tentar encontrar .ui pelo nome da classe
            if comp.class_name in ui_by_name:
                ui = ui_by_name[comp.class_name]
                # Existe .ui mas não está sendo usado
                if not ui.is_used:
                    comp.ui_file = str(ui.file_path.name)
                    # Ainda é programático se não usa UiLoaderMixin


def generate_report(
    components: list[UIComponent],
    ui_files: list[UIFile]
) -> dict[str, Any]:
    """Gera relatório de validação"""
    
    # Classificar componentes
    programmatic = [c for c in components if c.is_programmatic and not c.uses_ui_loader_mixin]
    using_ui = [c for c in components if c.uses_ui_loader_mixin]
    with_fallback = [c for c in components if c.has_fallback]
    
    # Classificar arquivos .ui
    used_ui = [u for u in ui_files if u.is_used]
    unused_ui = [u for u in ui_files if not u.is_used]
    
    # Identificar widgets customizados
    custom_widgets = set()
    for comp in components:
        custom_widgets.update(comp.custom_widgets_used)
        
    report = {
        "summary": {
            "total_components": len(components),
            "programmatic": len(programmatic),
            "using_ui_loader": len(using_ui),
            "with_fallback": len(with_fallback),
            "total_ui_files": len(ui_files),
            "used_ui_files": len(used_ui),
            "unused_ui_files": len(unused_ui),
            "custom_widgets_identified": len(custom_widgets),
        },
        "programmatic_components": [
            {
                "class": c.class_name,
                "file": str(c.file_path.relative_to(PROJECT_ROOT)),
                "base_classes": c.base_classes,
                "widgets_created": list(set(c.widgets_created))[:10],  # Limitar
                "custom_widgets": c.custom_widgets_used,
            }
            for c in sorted(programmatic, key=lambda x: x.class_name)
        ],
        "using_ui_loader": [
            {
                "class": c.class_name,
                "file": str(c.file_path.relative_to(PROJECT_ROOT)),
                "ui_file": c.ui_file,
                "has_fallback": c.has_fallback,
            }
            for c in sorted(using_ui, key=lambda x: x.class_name)
        ],
        "unused_ui_files": [
            {
                "file": str(u.file_path.relative_to(PROJECT_ROOT)),
                "class_name": u.class_name,
                "widgets": u.widgets[:5],  # Limitar
                "promoted_widgets": u.promoted_widgets,
            }
            for u in sorted(unused_ui, key=lambda x: x.file_path.name)
        ],
        "custom_widgets": sorted(list(custom_widgets)),
        "migration_priority": categorize_migration_priority(programmatic),
    }
    
    return report


def categorize_migration_priority(components: list[UIComponent]) -> dict[str, list[str]]:
    """Categoriza componentes por prioridade de migração"""
    priority = {
        "high": [],  # MainWindow, painéis principais
        "medium": [],  # Diálogos, widgets de visualização
        "low": [],  # Widgets simples, tooltips
    }
    
    for comp in components:
        name = comp.class_name
        
        # Alta prioridade: MainWindow e painéis principais
        if "MainWindow" in name or name.endswith("Panel"):
            priority["high"].append(name)
        # Média prioridade: Diálogos e widgets de visualização
        elif name.endswith("Dialog") or "Plot" in name or "Canvas" in name:
            priority["medium"].append(name)
        # Baixa prioridade: Resto
        else:
            priority["low"].append(name)
            
    return priority


def print_report(report: dict[str, Any]) -> None:
    """Imprime relatório formatado"""
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO DE VALIDAÇÃO - MIGRAÇÃO UI")
    print("=" * 70)
    
    summary = report["summary"]
    print(f"""
📈 RESUMO
─────────────────────────────────────
Total de componentes UI:     {summary['total_components']}
├── 100% Programáticos:      {summary['programmatic']}
├── Usando UiLoaderMixin:    {summary['using_ui_loader']}
└── Com fallback:            {summary['with_fallback']}

Total de arquivos .ui:       {summary['total_ui_files']}
├── Em uso:                  {summary['used_ui_files']}
└── Não utilizados:          {summary['unused_ui_files']}

Widgets customizados:        {summary['custom_widgets_identified']}
""")
    
    # Prioridade de migração
    print("🎯 PRIORIDADE DE MIGRAÇÃO")
    print("─────────────────────────────────────")
    priority = report["migration_priority"]
    print(f"Alta ({len(priority['high'])}):   {', '.join(priority['high'][:5])}{'...' if len(priority['high']) > 5 else ''}")
    print(f"Média ({len(priority['medium'])}):  {', '.join(priority['medium'][:5])}{'...' if len(priority['medium']) > 5 else ''}")
    print(f"Baixa ({len(priority['low'])}):  {', '.join(priority['low'][:5])}{'...' if len(priority['low']) > 5 else ''}")
    
    # Componentes usando UiLoaderMixin
    print("\n✅ COMPONENTES USANDO UILOADERMIXIN")
    print("─────────────────────────────────────")
    for comp in report["using_ui_loader"]:
        fallback = " (com fallback)" if comp["has_fallback"] else ""
        print(f"  • {comp['class']}: {comp['ui_file']}{fallback}")
        
    # Arquivos .ui não utilizados
    print(f"\n⚠️ ARQUIVOS .UI NÃO UTILIZADOS ({len(report['unused_ui_files'])})")
    print("─────────────────────────────────────")
    for ui in report["unused_ui_files"][:10]:
        print(f"  • {ui['file']} ({ui['class_name']})")
    if len(report["unused_ui_files"]) > 10:
        print(f"  ... e mais {len(report['unused_ui_files']) - 10}")
        
    # Widgets customizados identificados
    print(f"\n🧩 WIDGETS CUSTOMIZADOS ({len(report['custom_widgets'])})")
    print("─────────────────────────────────────")
    for widget in report["custom_widgets"][:15]:
        print(f"  • {widget}")
    if len(report["custom_widgets"]) > 15:
        print(f"  ... e mais {len(report['custom_widgets']) - 15}")
        
    print("\n" + "=" * 70)


def main():
    """Função principal"""
    print("🔍 Escaneando componentes de UI...")
    components = scan_python_files()
    print(f"   Encontrados {len(components)} componentes")
    
    print("📁 Escaneando arquivos .ui...")
    ui_files = scan_ui_files()
    print(f"   Encontrados {len(ui_files)} arquivos .ui")
    
    print("🔗 Correlacionando componentes e arquivos...")
    correlate_components_and_files(components, ui_files)
    
    print("📝 Gerando relatório...")
    report = generate_report(components, ui_files)
    
    # Salvar relatório JSON
    report_path = PROJECT_ROOT / "ui_migration_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"   Relatório salvo em {report_path}")
    
    # Imprimir relatório
    print_report(report)
    
    # Retornar código de saída baseado no status
    if report["summary"]["programmatic"] > 0:
        print(f"\n⚠️ {report['summary']['programmatic']} componentes precisam de migração")
        return 1
    else:
        print("\n✅ Todos os componentes estão usando arquivos .ui")
        return 0


if __name__ == "__main__":
    sys.exit(main())
