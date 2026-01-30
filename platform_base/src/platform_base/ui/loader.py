"""
UI Loader - Sistema de carregamento de arquivos .ui do Qt Designer

Este módulo fornece funções e classes para carregar arquivos .ui criados
no Qt Designer e integrá-los com componentes PyQt6.
"""

from __future__ import annotations

from pathlib import Path
from typing import Type, TypeVar

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)

# Caminho base para arquivos .ui
DESIGNER_PATH = Path(__file__).parent / "designer"

# TypeVar para type hints
T = TypeVar('T', bound=QWidget)


def load_ui(ui_name: str, widget: QWidget) -> None:
    """
    Carrega um arquivo .ui do Qt Designer em um widget existente.
    
    Args:
        ui_name: Nome do arquivo .ui (sem extensão) ou caminho relativo
                 Ex: "main_window" ou "panels/data_panel"
        widget: Widget onde o .ui será carregado
        
    Raises:
        FileNotFoundError: Se o arquivo .ui não for encontrado
        Exception: Se houver erro ao carregar o .ui
        
    Example:
        >>> class MyWidget(QWidget):
        ...     def __init__(self):
        ...         super().__init__()
        ...         load_ui("panels/my_panel", self)
    """
    # Adiciona extensão .ui se não tiver
    if not ui_name.endswith('.ui'):
        ui_name = f"{ui_name}.ui"
    
    ui_path = DESIGNER_PATH / ui_name
    
    if not ui_path.exists():
        error_msg = f"UI file not found: {ui_path}"
        logger.error("ui_file_not_found", path=str(ui_path))
        raise FileNotFoundError(error_msg)
    
    try:
        uic.loadUi(str(ui_path), widget)
        logger.debug("ui_loaded_successfully", ui_name=ui_name, widget=widget.__class__.__name__)
    except Exception as e:
        logger.error("ui_load_failed", ui_name=ui_name, error=str(e))
        raise


def get_ui_class(ui_name: str) -> Type[QWidget]:
    """
    Retorna uma classe gerada a partir de um arquivo .ui.
    
    Esta função é útil quando você quer criar uma classe base a partir
    de um .ui sem ter que criar uma instância primeiro.
    
    Args:
        ui_name: Nome do arquivo .ui (sem extensão) ou caminho relativo
        
    Returns:
        Classe QWidget gerada a partir do .ui
        
    Raises:
        FileNotFoundError: Se o arquivo .ui não for encontrado
        
    Example:
        >>> DataPanelUI = get_ui_class("panels/data_panel")
        >>> class DataPanel(DataPanelUI):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self._setup_connections()
    """
    # Adiciona extensão .ui se não tiver
    if not ui_name.endswith('.ui'):
        ui_name = f"{ui_name}.ui"
    
    ui_path = DESIGNER_PATH / ui_name
    
    if not ui_path.exists():
        error_msg = f"UI file not found: {ui_path}"
        logger.error("ui_file_not_found", path=str(ui_path))
        raise FileNotFoundError(error_msg)
    
    try:
        # uic.loadUiType retorna (FormClass, BaseClass)
        form_class, base_class = uic.loadUiType(str(ui_path))
        logger.debug("ui_class_created", ui_name=ui_name)
        return form_class
    except Exception as e:
        logger.error("ui_class_creation_failed", ui_name=ui_name, error=str(e))
        raise


def validate_ui_file(ui_name: str) -> bool:
    """
    Valida se um arquivo .ui existe e pode ser carregado.
    
    Args:
        ui_name: Nome do arquivo .ui (sem extensão) ou caminho relativo
        
    Returns:
        True se o arquivo existe e é válido, False caso contrário
    """
    # Adiciona extensão .ui se não tiver
    if not ui_name.endswith('.ui'):
        ui_name = f"{ui_name}.ui"
    
    ui_path = DESIGNER_PATH / ui_name
    return ui_path.exists() and ui_path.is_file()
