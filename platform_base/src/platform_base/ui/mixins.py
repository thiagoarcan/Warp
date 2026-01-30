"""
UI Mixins - Classes mixin para facilitar o uso de arquivos .ui

Este módulo fornece classes mixin que adicionam funcionalidades
de carregamento de .ui a widgets PyQt6.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QWidget

from platform_base.ui.loader import load_ui
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class UiLoaderMixin:
    """
    Mixin que adiciona funcionalidade de carregamento de .ui a um widget.
    
    Para usar este mixin, defina o atributo de classe UI_FILE com o caminho
    do arquivo .ui (sem extensão) e chame _load_ui() no __init__.
    
    Attributes:
        UI_FILE: Caminho do arquivo .ui (sem extensão). Ex: "panels/data_panel"
        
    Example:
        >>> class DataPanel(QWidget, UiLoaderMixin):
        ...     UI_FILE = "panels/data_panel"
        ...     
        ...     def __init__(self, session_state: SessionState):
        ...         super().__init__()
        ...         self.session_state = session_state
        ...         self._load_ui()
        ...         self._connect_signals()
        ...     
        ...     def _connect_signals(self):
        ...         self.load_button.clicked.connect(self._on_load_clicked)
    """
    
    UI_FILE: Optional[str] = None
    
    def _load_ui(self) -> None:
        """
        Carrega o arquivo .ui especificado em UI_FILE.
        
        Este método deve ser chamado no __init__ da classe que usa o mixin,
        após super().__init__() e antes de acessar qualquer widget do .ui.
        
        Raises:
            ValueError: Se UI_FILE não estiver definido
            FileNotFoundError: Se o arquivo .ui não for encontrado
        """
        if not self.UI_FILE:
            error_msg = f"{self.__class__.__name__} must define UI_FILE class attribute"
            logger.error("ui_file_not_defined", class_name=self.__class__.__name__)
            raise ValueError(error_msg)
        
        if not isinstance(self, QWidget):
            error_msg = f"{self.__class__.__name__} must inherit from QWidget to use UiLoaderMixin"
            logger.error("invalid_base_class", class_name=self.__class__.__name__)
            raise TypeError(error_msg)
        
        logger.debug("loading_ui", class_name=self.__class__.__name__, ui_file=self.UI_FILE)
        load_ui(self.UI_FILE, self)
        logger.info("ui_loaded", class_name=self.__class__.__name__)


class DialogLoaderMixin(UiLoaderMixin):
    """
    Mixin especializado para diálogos com funcionalidades extras.
    
    Adiciona funcionalidades comuns a diálogos como:
    - Carregamento automático de .ui
    - Configuração de botões padrão (OK/Cancel)
    
    Example:
        >>> class SettingsDialog(QDialog, DialogLoaderMixin):
        ...     UI_FILE = "dialogs/settings_dialog"
        ...     
        ...     def __init__(self, parent=None):
        ...         super().__init__(parent)
        ...         self._load_ui()
        ...         self._setup_dialog_buttons()
    """
    
    def _setup_dialog_buttons(self) -> None:
        """
        Configura os botões padrão do diálogo (OK/Cancel).
        
        Este método assume que o .ui contém um QDialogButtonBox
        chamado 'button_box' com botões OK e Cancel.
        """
        if hasattr(self, 'button_box'):
            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
            logger.debug("dialog_buttons_configured", class_name=self.__class__.__name__)
        else:
            logger.warning(
                "dialog_button_box_not_found",
                class_name=self.__class__.__name__,
                hint="Add a QDialogButtonBox named 'button_box' to the .ui file"
            )
