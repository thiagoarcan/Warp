#!/usr/bin/env python3
"""
Script para migrar widgets e diálogos para usar arquivos .ui do Qt Designer.

Este script automatiza a migração de componentes PyQt6 que criam UI programaticamente
para usar arquivos .ui carregados dinamicamente.

Uso:
    python scripts/migrate_to_ui.py
"""

from __future__ import annotations

import re
from pathlib import Path


# Diretórios
SRC_DIR = Path(__file__).parent.parent / "src" / "platform_base"
DESKTOP_UI_FILES = SRC_DIR / "desktop" / "ui_files"
UI_DESIGNER_FILES = SRC_DIR / "ui" / "designer"


def get_ui_file_for_class(class_name: str) -> str | None:
    """Encontra o arquivo .ui correspondente a uma classe"""
    # Converter CamelCase para snake_case
    snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()

    # Tentar encontrar o arquivo .ui
    possible_names = [
        f"{class_name[0].lower()}{class_name[1:]}.ui",  # camelCase
        f"{snake_name}.ui",  # snake_case
        f"{class_name}.ui",  # PascalCase
    ]

    for name in possible_names:
        if (DESKTOP_UI_FILES / name).exists():
            return f"desktop/ui_files/{name}"
        if (UI_DESIGNER_FILES / name).exists():
            return f"ui/designer/{name}"

    return None


def generate_migration_report():
    """Gera relatório de migração mostrando status de cada componente"""

    # Encontrar todos os arquivos .ui
    ui_files = list(DESKTOP_UI_FILES.glob("*.ui")) + list(UI_DESIGNER_FILES.glob("**/*.ui"))

    print("\n" + "="*80)
    print("RELATÓRIO DE MIGRAÇÃO PARA .UI")
    print("="*80)

    print(f"\n📁 Total de arquivos .ui: {len(ui_files)}")
    print(f"   - desktop/ui_files/: {len(list(DESKTOP_UI_FILES.glob('*.ui')))}")
    print(f"   - ui/designer/: {len(list(UI_DESIGNER_FILES.glob('**/*.ui')))}")

    # Verificar quais são placeholders vs completos
    placeholder_count = 0
    complete_count = 0

    for ui_file in ui_files:
        content = ui_file.read_text(encoding="utf-8")
        if "UI for " in content and content.count("<widget") <= 3:
            placeholder_count += 1
        else:
            complete_count += 1

    print("\n📊 Status dos arquivos .ui:")
    print(f"   ✅ Completos (com widgets reais): {complete_count}")
    print(f"   ⚠️  Placeholders (templates vazios): {placeholder_count}")

    # Calcular porcentagem
    total = len(ui_files)
    if total > 0:
        percent_complete = (complete_count / total) * 100
        print(f"\n📈 Progresso da Fase 2: {percent_complete:.1f}% dos .ui são completos")

    # Listar arquivos completos
    print("\n✅ Arquivos .ui COMPLETOS (prontos para uso):")
    complete_files = []
    for ui_file in sorted(ui_files):
        content = ui_file.read_text(encoding="utf-8")
        if not ("UI for " in content and content.count("<widget") <= 3):
            complete_files.append(ui_file.name)
            print(f"   - {ui_file.name}")

    # Verificar conexão com classes Python
    print("\n🔗 Status de conexão UI ↔ Python:")

    # Arquivos Python que deveriam usar .ui
    widget_files = list((SRC_DIR / "desktop" / "widgets").glob("*.py"))
    dialog_files = list((SRC_DIR / "desktop" / "dialogs").glob("*.py"))

    connected = 0
    not_connected = 0

    for py_file in widget_files + dialog_files:
        content = py_file.read_text(encoding="utf-8")
        if "UiLoaderMixin" in content or "load_ui(" in content or "UI_FILE" in content:
            connected += 1
        else:
            not_connected += 1

    print(f"   ✅ Classes usando .ui: {connected}")
    print(f"   ❌ Classes com UI programática: {not_connected}")

    return {
        "total_ui_files": len(ui_files),
        "complete_ui_files": complete_count,
        "placeholder_ui_files": placeholder_count,
        "connected_classes": connected,
        "not_connected_classes": not_connected,
    }


def check_ui_completeness(ui_file: Path) -> dict:
    """Verifica se um arquivo .ui está completo ou é placeholder"""
    content = ui_file.read_text(encoding="utf-8")

    # Contar widgets
    widget_count = content.count("<widget")
    layout_count = content.count("<layout")

    # Verificar se é placeholder
    is_placeholder = "UI for " in content and widget_count <= 3

    return {
        "file": ui_file.name,
        "is_placeholder": is_placeholder,
        "widget_count": widget_count,
        "layout_count": layout_count,
        "size_bytes": ui_file.stat().st_size,
    }


def main():
    """Função principal"""
    print("\n🔄 Iniciando análise de migração para .ui...\n")

    report = generate_migration_report()

    print("\n" + "="*80)
    print("RESUMO DA FASE 2")
    print("="*80)

    total_ui = report["total_ui_files"]
    complete_ui = report["complete_ui_files"]
    connected = report["connected_classes"]
    not_connected = report["not_connected_classes"]

    # Calcular score
    ui_score = (complete_ui / total_ui * 100) if total_ui > 0 else 0
    connection_score = (connected / (connected + not_connected) * 100) if (connected + not_connected) > 0 else 0
    overall_score = (ui_score + connection_score) / 2

    print("\n📊 Scores:")
    print(f"   - Arquivos .ui completos: {ui_score:.1f}%")
    print(f"   - Classes conectadas: {connection_score:.1f}%")
    print(f"   - Score geral Fase 2: {overall_score:.1f}%")

    if overall_score >= 95:
        print("\n✅ FASE 2 CONCLUÍDA COM SUCESSO!")
    elif overall_score >= 50:
        print("\n⚠️  FASE 2 EM PROGRESSO - Mais trabalho necessário")
    else:
        print("\n❌ FASE 2 INCOMPLETA - Necessita atenção significativa")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
