"""
UiLoaderMixin - Mixin para carregar arquivos .ui do Qt Designer

Permite que qualquer QWidget ou QDialog carregue sua interface a partir de um arquivo .ui,
em vez de criá-la programaticamente.

Uso:
    class MyDialog(QDialog, UiLoaderMixin):
        UI_FILE = "desktop/ui_files/myDialog.ui"
        
        def __init__(self):
            super().__init__()
            self._load_ui()  # Carrega UI do arquivo .ui
            self._connect_signals()  # Conecta signals após carregar
            
Nota: PyQt6 usa PyQt6.uic.loadUi() para carregar .ui diretamente no widget.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QDialogButtonBox, QWidget

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QDialog

logger = get_logger(__name__)


def _get_package_root() -> Path:
    """Retorna o diretório raiz do pacote platform_base"""
    return Path(__file__).parent.parent


class UiLoaderMixin:
    """
    Mixin para carregar e gerenciar interfaces Qt criadas com Qt Designer (.ui)
    
    Classes que usam este mixin devem definir:
        UI_FILE: str - Caminho relativo do arquivo .ui (relativo ao pacote platform_base)
        
    Atributos após load:
        _ui_loaded: bool - True se UI foi carregado com sucesso
        _ui_file_path: Path - Caminho absoluto do arquivo .ui carregado
    """
    
    # Deve ser definido pelas subclasses
    UI_FILE: ClassVar[str] = ""
    
    # Atributos de instância
    _ui_loaded: bool = False
    _ui_file_path: Path | None = None

    def _load_ui(self) -> bool:
        """
        Carrega arquivo .ui e integra sua interface ao widget atual.
        
        O arquivo .ui é localizado relativo ao diretório do pacote platform_base.
        Usa PyQt6.uic.loadUi() para carregar diretamente no widget.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        if not self.UI_FILE:
            logger.warning("ui_file_not_specified", cls=self.__class__.__name__)
            return False
            
        try:
            # Importar uic aqui para evitar problemas de import circular
            from PyQt6 import uic

            # Resolver caminho do arquivo .ui
            package_root = _get_package_root()
            ui_path = package_root / self.UI_FILE
            
            # Tentar localizações alternativas
            if not ui_path.exists():
                alt_paths = [
                    package_root / "desktop" / "ui_files" / Path(self.UI_FILE).name,
                    package_root / "ui" / "designer" / Path(self.UI_FILE).name,
                    Path(__file__).parent / "ui_files" / Path(self.UI_FILE).name,
                ]
                
                for alt_path in alt_paths:
                    if alt_path.exists():
                        ui_path = alt_path
                        break
                else:
                    logger.error(
                        "ui_file_not_found",
                        ui_file=self.UI_FILE,
                        searched_paths=[str(p) for p in [ui_path] + alt_paths]
                    )
                    return False
            
            # Verificar se arquivo existe
            if not ui_path.exists():
                logger.error("ui_file_does_not_exist", path=str(ui_path))
                return False
            
            # Carregar UI diretamente no widget
            uic.loadUi(str(ui_path), self)
            
            # Marcar como carregado
            self._ui_loaded = True
            self._ui_file_path = ui_path
            
            logger.debug(
                "ui_loaded_successfully",
                cls=self.__class__.__name__,
                path=str(ui_path)
            )
            return True
            
        except Exception as e:
            logger.exception(
                "ui_loading_error",
                cls=self.__class__.__name__,
                ui_file=self.UI_FILE,
                error=str(e)
            )
            return False

    def _find_widget(self, name: str, widget_type: type = QWidget) -> Any | None:
        """
        Encontra um widget pelo nome (objectName)
        
        Args:
            name: Nome do widget (objectName definido no Qt Designer)
            widget_type: Tipo esperado do widget (para type checking)
            
        Returns:
            Widget encontrado ou None
        """
        if not isinstance(self, QWidget):
            return None
            
        widget = self.findChild(widget_type, name)
        if widget is None:
            # Tentar como atributo direto (uic.loadUi cria atributos)
            widget = getattr(self, name, None)
            
        return widget

    def _get_widget(self, name: str, widget_type: type = QWidget) -> Any:
        """
        Retorna um widget pelo nome, levantando erro se não encontrado.
        
        Args:
            name: Nome do widget
            widget_type: Tipo esperado do widget
            
        Returns:
            Widget encontrado
            
        Raises:
            AttributeError: Se widget não for encontrado
        """
        widget = self._find_widget(name, widget_type)
        if widget is None:
            raise AttributeError(
                f"Widget '{name}' não encontrado em {self.__class__.__name__}. "
                f"Verifique se o objectName está correto no arquivo .ui"
            )
        return widget

    def _connect_button_box(
        self,
        button_box_name: str = "buttonBox",
        on_accept: Any = None,
        on_reject: Any = None
    ) -> bool:
        """
        Conecta botões de um QDialogButtonBox aos métodos accept/reject.
        
        Args:
            button_box_name: Nome do QDialogButtonBox no .ui
            on_accept: Callable para chamar ao aceitar (default: self.accept)
            on_reject: Callable para chamar ao rejeitar (default: self.reject)
            
        Returns:
            True se conectado com sucesso
        """
        try:
            button_box = self._find_widget(button_box_name, QDialogButtonBox)
            if not button_box:
                return False
            
            # Conectar accepted
            if on_accept is not None:
                button_box.accepted.connect(on_accept)
            elif hasattr(self, 'accept'):
                button_box.accepted.connect(self.accept)  # type: ignore
                
            # Conectar rejected
            if on_reject is not None:
                button_box.rejected.connect(on_reject)
            elif hasattr(self, 'reject'):
                button_box.rejected.connect(self.reject)  # type: ignore
                
            return True
            
        except Exception as e:
            logger.exception("button_box_connection_error", error=str(e))
            return False

    def is_ui_loaded(self) -> bool:
        """Verifica se UI foi carregado com sucesso"""
        return self._ui_loaded
        
    def get_ui_file_path(self) -> Path | None:
        """Retorna caminho do arquivo .ui carregado"""
        return self._ui_file_path


class UiLoaderDialog(QObject):
    """
    Dialog helper com suporte a .ui files e signals automáticos.
    
    Classe base para diálogos que usam arquivos .ui.
    """

    accepted = pyqtSignal()
    rejected = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.result_code: int | None = None

    def accept(self) -> None:
        """Aceita o diálogo"""
        self.result_code = 1
        self.accepted.emit()

    def reject(self) -> None:
        """Rejeita o diálogo"""
        self.result_code = 0
        self.rejected.emit()


def is_ui_based(widget_class: type) -> bool:
    """
    Verifica se uma classe de widget usa UiLoaderMixin
    
    Args:
        widget_class: Classe a verificar
        
    Returns:
        True se herda de UiLoaderMixin
    """
    try:
        return issubclass(widget_class, UiLoaderMixin)
    except TypeError:
        return False


def get_ui_file_for_class(widget_class: type) -> str | None:
    """
    Retorna o arquivo .ui associado a uma classe.
    
    Args:
        widget_class: Classe que usa UiLoaderMixin
        
    Returns:
        Caminho do arquivo .ui ou None
    """
    if is_ui_based(widget_class):
        return getattr(widget_class, 'UI_FILE', None)
    return None
