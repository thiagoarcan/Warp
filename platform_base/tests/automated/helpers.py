# -*- coding: utf-8 -*-
"""
helpers.py — Funções auxiliares para testes automatizados

Este módulo contém funções auxiliares que são usadas por múltiplos
arquivos de teste. Diferentes do conftest.py, que contém fixtures,
este módulo contém funções utilitárias que podem ser importadas
diretamente.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any


# ═══════════════════════════════════════════════════════════════════════════
# Constantes dos signals esperados
# ═══════════════════════════════════════════════════════════════════════════
SIGNAL_HUB_SIGNALS = [
    "dataset_loaded", "dataset_removed", "dataset_selected",
    "series_added", "series_removed", "series_selected",
    "series_deselected", "series_visibility_changed",
    "plot_created", "plot_updated", "plot_closed", "view_synchronized",
    "time_selection_changed", "value_selection_changed", "selection_cleared",
    "operation_started", "operation_progress", "operation_completed",
    "operation_failed", "operation_cancelled",
    "streaming_started", "streaming_stopped", "streaming_paused",
    "streaming_time_changed",
    "ui_mode_changed", "theme_changed", "layout_changed",
    "error_occurred", "status_updated", "progress_updated",
]

SESSION_STATE_SIGNALS = [
    "selection_changed", "view_state_changed", "processing_state_changed",
    "streaming_state_changed", "ui_state_changed", "dataset_changed",
    "operation_finished", "session_loaded", "session_saved", "session_cleared",
]


def validate_ui_xml(ui_file: Path) -> Tuple[bool, Optional[str]]:
    """Valida se um arquivo .ui é XML bem-formado.
    
    Retorna:
        Tupla (is_valid, error_message)
    """
    try:
        ET.parse(ui_file)
        return True, None
    except ET.ParseError as e:
        return False, str(e)


def get_widgets_from_ui_xml(ui_file: Path) -> List[Dict[str, str]]:
    """Extrai informações de widgets de um arquivo .ui.
    
    Retorna:
        Lista de dicts com 'name' e 'class' de cada widget
    """
    widgets = []
    try:
        tree = ET.parse(ui_file)
        root = tree.getroot()
        
        for widget in root.iter("widget"):
            name = widget.get("name", "")
            widget_class = widget.get("class", "")
            widgets.append({"name": name, "class": widget_class})
    except Exception:
        pass
    
    return widgets


def get_connections_from_ui_xml(ui_file: Path) -> List[Dict[str, str]]:
    """Extrai conexões signal/slot de um arquivo .ui.
    
    Retorna:
        Lista de dicts com detalhes de cada conexão
    """
    connections = []
    try:
        tree = ET.parse(ui_file)
        root = tree.getroot()
        
        for conn in root.iter("connection"):
            sender = conn.findtext("sender", "")
            signal = conn.findtext("signal", "")
            receiver = conn.findtext("receiver", "")
            slot = conn.findtext("slot", "")
            connections.append({
                "sender": sender,
                "signal": signal,
                "receiver": receiver,
                "slot": slot
            })
    except Exception:
        pass
    
    return connections


def get_resources_from_ui_xml(ui_file: Path) -> List[str]:
    """Extrai referências a recursos de um arquivo .ui.
    
    Retorna:
        Lista de caminhos de recursos referenciados
    """
    resources = []
    try:
        tree = ET.parse(ui_file)
        root = tree.getroot()
        
        # Procura referências de recursos
        for elem in root.iter():
            for key, value in elem.attrib.items():
                if "resource" in key.lower() or "icon" in key.lower():
                    resources.append(value)
            
            # Procura em textos também
            if elem.text and ":" in str(elem.text) and "/" in str(elem.text):
                resources.append(elem.text)
    except Exception:
        pass
    
    return resources


def get_all_widgets(widget) -> List:
    """Retorna todos os widgets filhos de um widget.
    
    Args:
        widget: Widget Qt raiz
        
    Retorna:
        Lista de todos os widgets descendentes
    """
    widgets = []
    try:
        for child in widget.findChildren(object):
            widgets.append(child)
    except Exception:
        pass
    return widgets


def get_ui_files_dir() -> Path:
    """Retorna o diretório de arquivos UI."""
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parents[1]
    return project_root / "src" / "platform_base" / "desktop" / "ui_files"


def get_all_ui_files() -> List[Path]:
    """Retorna lista de todos os arquivos .ui."""
    ui_dir = get_ui_files_dir()
    if ui_dir.exists():
        return sorted(ui_dir.glob("*.ui"))
    return []


def get_project_root() -> Path:
    """Retorna o diretório raiz do projeto."""
    tests_dir = Path(__file__).parent
    return tests_dir.parents[1]


# ═══════════════════════════════════════════════════════════════════════════
# Constantes de diretórios
# ═══════════════════════════════════════════════════════════════════════════
PROJECT_ROOT = get_project_root()
SRC_DIR = PROJECT_ROOT / "src"
UI_FILES_DIR = SRC_DIR / "platform_base" / "desktop" / "ui_files"
RESOURCES_DIR = SRC_DIR / "platform_base" / "desktop" / "resources"
CONFIGS_DIR = PROJECT_ROOT / "configs"
DATA_DIR = PROJECT_ROOT / "data"
