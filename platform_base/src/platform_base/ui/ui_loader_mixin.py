"""
UiLoaderMixin - Mixin para carregar arquivos .ui do Qt Designer

Permite que qualquer QWidget ou QDialog carregue sua interface a partir de um arquivo .ui,
em vez de criá-la programaticamente.

Uso:
    class MyDialog(QDialog, UiLoaderMixin):
        def __init__(self):
            super().__init__()
            self.load_ui('path/to/file.ui')
            self.connect_signals()
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtUiTools import QUiLoader
from PyQt6.QtWidgets import QWidget

from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class UiLoaderMixin:
    """
    Mixin para carregar e gerenciar interfaces Qt criadas com Qt Designer (.ui)
    
    Atributos:
        ui: Objeto carregado do arquivo .ui contendo todos os widgets
        ui_file: Caminho do arquivo .ui carregado
    """

    ui: Any = None
    ui_file: str | None = None

    def load_ui(self, ui_file: str | Path, replace_current: bool = True) -> bool:
        """
        Carrega arquivo .ui e integra sua interface ao widget atual
        
        Args:
            ui_file: Caminho do arquivo .ui (relativo ou absoluto)
            replace_current: Se True, substitui layout atual; se False, carrega como filho
            
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        try:
            # Converter para Path
            ui_path = Path(ui_file)

            # Se caminho relativo, procurar em relação ao arquivo do módulo
            if not ui_path.is_absolute():
                # Tentar várias localizações padrão
                base_dirs = [
                    Path(__file__).parent / "ui_files",
                    Path(__file__).parent.parent / "ui",
                    Path(__file__).parent.parent.parent / "ui",
                    Path.cwd(),
                ]

                for base_dir in base_dirs:
                    candidate = base_dir / ui_file
                    if candidate.exists():
                        ui_path = candidate
                        break
                else:
                    # Tentar como é sem prefixo
                    if (Path.cwd() / ui_file).exists():
                        ui_path = Path.cwd() / ui_file
                    else:
                        logger.error(f"ui_file_not_found", file=ui_file)
                        return False

            # Verificar se arquivo existe
            if not ui_path.exists():
                logger.error(f"ui_file_not_found", path=str(ui_path))
                return False

            # Carregar arquivo
            loader = QUiLoader()
            with open(ui_path, 'r', encoding='utf-8') as f:
                self.ui = loader.load(f, self)

            if not self.ui:
                logger.error("ui_loading_failed", file=str(ui_path))
                return False

            # Se o arquivo .ui tem um layout de top-level, integrar
            if replace_current and self.ui != self:
                # Copiar todos os widgets do .ui para self
                try:
                    layout = self.ui.layout()
                    if layout:
                        # Transferir layout para self
                        if isinstance(self, QWidget):
                            if self.layout():
                                # Remover layout anterior
                                self.setLayout(None)
                            self.setLayout(layout)

                    # Transferir outros atributos
                    for widget in self.ui.findChildren(QWidget):
                        if not hasattr(self, widget.objectName()):
                            setattr(self, widget.objectName(), widget)

                except Exception as e:
                    logger.warning(f"ui_integration_warning", error=str(e))

            # Armazenar referência
            self.ui_file = str(ui_path)

            logger.info("ui_file_loaded", file=str(ui_path))
            return True

        except Exception as e:
            logger.exception(f"ui_loading_error: {e}")
            return False

    def get_ui_file(self) -> str | None:
        """Retorna caminho do arquivo .ui carregado"""
        return self.ui_file

    def find_widget(self, name: str) -> QWidget | None:
        """
        Encontra um widget pelo nome (objectName)
        
        Args:
            name: Nome do widget
            
        Returns:
            Widget encontrado ou None
        """
        if not self.ui:
            return None
        return self.ui.findChild(QWidget, name)

    def get_widget(self, name: str) -> Any:
        """
        Retorna um widget pelo nome, com fallback para atributo de classe
        
        Args:
            name: Nome do widget ou atributo
            
        Returns:
            Widget ou atributo encontrado
        """
        widget = self.find_widget(name)
        if widget:
            return widget

        # Fallback para atributo
        if hasattr(self, name):
            return getattr(self, name)

        return None

    def connect_dialog_buttons(self, ok_slot=None, cancel_slot=None):
        """
        Conecta botões OK/Cancel do .ui a slots
        
        Args:
            ok_slot: Função para chamar ao clicar OK
            cancel_slot: Função para chamar ao clicar Cancel
        """
        try:
            # Procurar por QDialogButtonBox
            button_box = self.ui.findChild(QWidget, "buttonBox")
            if not button_box:
                return False

            # Conectar signals padrão se não houver slot customizado
            if hasattr(button_box, 'accepted'):
                if ok_slot:
                    button_box.accepted.connect(ok_slot)
                else:
                    button_box.accepted.connect(self.accept if hasattr(self, 'accept') else None)

            if hasattr(button_box, 'rejected'):
                if cancel_slot:
                    button_box.rejected.connect(cancel_slot)
                else:
                    button_box.rejected.connect(self.reject if hasattr(self, 'reject') else None)

            return True

        except Exception as e:
            logger.exception(f"connect_dialog_buttons_error: {e}")
            return False

    def show_ui(self) -> None:
        """Exibe o UI carregado (atalho para show)"""
        if hasattr(self, 'show'):
            self.show()


class UiLoaderDialog(QObject):
    """
    Dialog helper com suporte a .ui files e signals automáticos
    
    Usa UiLoaderMixin para carregar interface do Qt Designer.
    """

    accepted = pyqtSignal()
    rejected = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_code = None

    def accept(self):
        """Aceita o diálogo"""
        self.result_code = 1
        self.accepted.emit()

    def reject(self):
        """Rejeita o diálogo"""
        self.result_code = 0
        self.rejected.emit()


# Função auxiliar para verificar se UI foi migrado
def is_ui_based(widget_class) -> bool:
    """
    Verifica se uma classe de widget usa UiLoaderMixin
    
    Args:
        widget_class: Classe a verificar
        
    Returns:
        True se herda de UiLoaderMixin
    """
    return issubclass(widget_class, UiLoaderMixin)
