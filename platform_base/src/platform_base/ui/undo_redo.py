"""
Undo/Redo System - Sistema de desfazer/refazer para operações

Implementa QUndoStack para:
- Operações em dados (interpolação, filtros, etc.)
- Modificações de sessão
- Seleções e configurações
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QUndoCommand, QUndoStack

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class BaseCommand(QUndoCommand):
    """Comando base para todas as operações undoable"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.timestamp = datetime.now()
        self._executed = False
    
    def redo(self):
        """Executa ou refaz a operação"""
        if not self._executed:
            self._execute()
            self._executed = True
        else:
            self._redo_impl()
    
    def undo(self):
        """Desfaz a operação"""
        self._undo_impl()
    
    @abstractmethod
    def _execute(self):
        """Primeira execução da operação"""
        pass
    
    @abstractmethod
    def _redo_impl(self):
        """Implementação de redo"""
        pass
    
    @abstractmethod
    def _undo_impl(self):
        """Implementação de undo"""
        pass


class DataOperationCommand(BaseCommand):
    """
    Comando para operações em dados
    
    Guarda estado anterior e novo para permitir undo/redo
    """
    
    def __init__(self, operation_name: str, 
                 data_before: Any, 
                 execute_func: Callable[[], Any],
                 undo_func: Callable[[Any], None],
                 parent=None):
        super().__init__(f"Operação: {operation_name}", parent)
        
        self.operation_name = operation_name
        self._data_before = data_before
        self._data_after: Optional[Any] = None
        self._execute_func = execute_func
        self._undo_func = undo_func
    
    def _execute(self):
        """Executa operação e guarda resultado"""
        try:
            self._data_after = self._execute_func()
            logger.info(f"Operation executed: {self.operation_name}")
        except Exception as e:
            logger.error(f"Operation execution error: {e}")
            raise
    
    def _redo_impl(self):
        """Refaz operação aplicando dados guardados"""
        if self._data_after is not None:
            self._execute_func()
            logger.info(f"Operation redone: {self.operation_name}")
    
    def _undo_impl(self):
        """Desfaz operação restaurando dados anteriores"""
        if self._data_before is not None:
            self._undo_func(self._data_before)
            logger.info(f"Operation undone: {self.operation_name}")


class SelectionCommand(BaseCommand):
    """Comando para mudanças de seleção"""
    
    def __init__(self, description: str,
                 old_selection: Dict[str, Any],
                 new_selection: Dict[str, Any],
                 apply_func: Callable[[Dict[str, Any]], None],
                 parent=None):
        super().__init__(f"Seleção: {description}", parent)
        
        self._old_selection = old_selection
        self._new_selection = new_selection
        self._apply_func = apply_func
    
    def _execute(self):
        """Aplica nova seleção"""
        self._apply_func(self._new_selection)
    
    def _redo_impl(self):
        """Refaz seleção"""
        self._apply_func(self._new_selection)
    
    def _undo_impl(self):
        """Desfaz seleção"""
        self._apply_func(self._old_selection)


class ViewConfigCommand(BaseCommand):
    """Comando para mudanças de configuração de visualização"""
    
    def __init__(self, description: str,
                 old_config: Dict[str, Any],
                 new_config: Dict[str, Any],
                 apply_func: Callable[[Dict[str, Any]], None],
                 parent=None):
        super().__init__(f"Configuração: {description}", parent)
        
        self._old_config = old_config
        self._new_config = new_config
        self._apply_func = apply_func
    
    def _execute(self):
        """Aplica nova configuração"""
        self._apply_func(self._new_config)
    
    def _redo_impl(self):
        """Refaz configuração"""
        self._apply_func(self._new_config)
    
    def _undo_impl(self):
        """Desfaz configuração"""
        self._apply_func(self._old_config)


@dataclass
class UndoHistoryItem:
    """Item do histórico de undo/redo"""
    index: int
    text: str
    timestamp: datetime
    is_clean: bool


class UndoRedoManager(QObject):
    """
    Gerenciador centralizado de Undo/Redo
    
    Características:
    - QUndoStack integrado
    - Histórico de operações
    - Signals para atualização de UI
    - Limite de operações configurável
    """
    
    # Signals
    can_undo_changed = pyqtSignal(bool)
    can_redo_changed = pyqtSignal(bool)
    undo_text_changed = pyqtSignal(str)
    redo_text_changed = pyqtSignal(str)
    clean_changed = pyqtSignal(bool)
    index_changed = pyqtSignal(int)
    
    _instance: Optional["UndoRedoManager"] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, undo_limit: int = 100):
        if self._initialized:
            return
        
        super().__init__()
        self._initialized = True
        
        # QUndoStack principal
        self._stack = QUndoStack()
        self._stack.setUndoLimit(undo_limit)
        
        # Conectar signals
        self._stack.canUndoChanged.connect(self.can_undo_changed.emit)
        self._stack.canRedoChanged.connect(self.can_redo_changed.emit)
        self._stack.undoTextChanged.connect(self.undo_text_changed.emit)
        self._stack.redoTextChanged.connect(self.redo_text_changed.emit)
        self._stack.cleanChanged.connect(self.clean_changed.emit)
        self._stack.indexChanged.connect(self.index_changed.emit)
        
        logger.debug(f"UndoRedoManager initialized with limit={undo_limit}")
    
    @property
    def stack(self) -> QUndoStack:
        """Acesso ao QUndoStack interno"""
        return self._stack
    
    def push(self, command: QUndoCommand) -> None:
        """
        Adiciona comando ao stack e executa
        
        Args:
            command: Comando a ser executado
        """
        self._stack.push(command)
        logger.debug(f"Command pushed: {command.text()}")
    
    def undo(self) -> None:
        """Desfaz última operação"""
        if self._stack.canUndo():
            self._stack.undo()
            logger.info(f"Undo: {self._stack.undoText()}")
    
    def redo(self) -> None:
        """Refaz última operação desfeita"""
        if self._stack.canRedo():
            self._stack.redo()
            logger.info(f"Redo: {self._stack.redoText()}")
    
    def clear(self) -> None:
        """Limpa histórico de undo/redo"""
        self._stack.clear()
        logger.info("Undo/Redo history cleared")
    
    def set_clean(self) -> None:
        """Marca estado atual como 'limpo' (salvo)"""
        self._stack.setClean()
    
    def is_clean(self) -> bool:
        """Verifica se estado atual é 'limpo'"""
        return self._stack.isClean()
    
    def can_undo(self) -> bool:
        """Verifica se pode desfazer"""
        return self._stack.canUndo()
    
    def can_redo(self) -> bool:
        """Verifica se pode refazer"""
        return self._stack.canRedo()
    
    def undo_text(self) -> str:
        """Texto da operação que será desfeita"""
        return self._stack.undoText()
    
    def redo_text(self) -> str:
        """Texto da operação que será refeita"""
        return self._stack.redoText()
    
    def count(self) -> int:
        """Número total de comandos no stack"""
        return self._stack.count()
    
    def index(self) -> int:
        """Índice atual no stack"""
        return self._stack.index()
    
    def get_history(self) -> List[UndoHistoryItem]:
        """
        Retorna histórico de operações
        
        Returns:
            Lista de itens do histórico
        """
        history = []
        clean_index = self._stack.cleanIndex()
        
        for i in range(self._stack.count()):
            cmd = self._stack.command(i)
            if cmd:
                timestamp = getattr(cmd, 'timestamp', datetime.now())
                history.append(UndoHistoryItem(
                    index=i,
                    text=cmd.text(),
                    timestamp=timestamp,
                    is_clean=(i == clean_index)
                ))
        
        return history
    
    def goto_index(self, index: int) -> None:
        """
        Vai para índice específico no histórico
        
        Args:
            index: Índice de destino
        """
        self._stack.setIndex(index)
        logger.info(f"Moved to index {index}")
    
    # === Convenience methods ===
    
    def push_data_operation(self, operation_name: str,
                           data_before: Any,
                           execute_func: Callable[[], Any],
                           undo_func: Callable[[Any], None]) -> None:
        """
        Adiciona operação de dados ao stack
        
        Args:
            operation_name: Nome da operação
            data_before: Estado dos dados antes da operação
            execute_func: Função para executar operação
            undo_func: Função para desfazer operação
        """
        cmd = DataOperationCommand(
            operation_name, data_before, execute_func, undo_func
        )
        self.push(cmd)
    
    def push_selection_change(self, description: str,
                              old_selection: Dict[str, Any],
                              new_selection: Dict[str, Any],
                              apply_func: Callable[[Dict[str, Any]], None]) -> None:
        """
        Adiciona mudança de seleção ao stack
        
        Args:
            description: Descrição da mudança
            old_selection: Seleção anterior
            new_selection: Nova seleção
            apply_func: Função para aplicar seleção
        """
        cmd = SelectionCommand(
            description, old_selection, new_selection, apply_func
        )
        self.push(cmd)
    
    def push_config_change(self, description: str,
                           old_config: Dict[str, Any],
                           new_config: Dict[str, Any],
                           apply_func: Callable[[Dict[str, Any]], None]) -> None:
        """
        Adiciona mudança de configuração ao stack
        
        Args:
            description: Descrição da mudança
            old_config: Configuração anterior
            new_config: Nova configuração
            apply_func: Função para aplicar configuração
        """
        cmd = ViewConfigCommand(
            description, old_config, new_config, apply_func
        )
        self.push(cmd)


def get_undo_manager() -> UndoRedoManager:
    """Retorna instância singleton do UndoRedoManager"""
    return UndoRedoManager()
