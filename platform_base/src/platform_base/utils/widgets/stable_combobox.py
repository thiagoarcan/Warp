"""
StableComboBox - A robust QComboBox that doesn't auto-close on Windows.

This widget solves the QWindowsWindow::setMouseGrabEnabled issue on Windows
by using QTimer to prevent premature closing and managing mouse events.
"""

from __future__ import annotations

from PyQt6.QtCore import QEvent, QTimer, Qt
from PyQt6.QtWidgets import QComboBox


class StableComboBox(QComboBox):
    """
    ComboBox estável que não fecha automaticamente no Windows.
    
    Solução robusta para o problema de QWindowsWindow::setMouseGrabEnabled.
    Usa QTimer para evitar fechamento prematuro e gerencia eventos de mouse.
    
    Features:
    - Prevents premature popup closing on Windows
    - Supports keyboard navigation
    - Custom styling for modern UI
    - Mouse tracking with delayed selection
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(30)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMaxVisibleItems(20)
        
        # Flag para controlar estado do popup
        self._popup_visible = False
        self._ignore_hide = False
        
        # Configurações específicas para Windows
        self.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #0d6efd;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #ced4da;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                selection-background-color: #0d6efd;
                selection-color: white;
                background-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 8px;
                min-height: 24px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e9ecef;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0d6efd;
                color: white;
            }
        """)
        
        # Desabilitar context menu para evitar interferências
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        # Configurar a view para não fechar em eventos de mouse
        self.view().setMouseTracking(True)
        self.view().viewport().installEventFilter(self)
        
    def showPopup(self):
        """Override para garantir que o popup seja mostrado corretamente"""
        self._ignore_hide = True
        self._popup_visible = True
        super().showPopup()
        
        # Usar QTimer para garantir que o popup permaneça aberto
        QTimer.singleShot(100, self._enable_hide)
        
        # Focar na view para permitir navegação por teclado
        self.view().setFocus()
        
    def _enable_hide(self):
        """Re-habilita o fechamento após delay inicial"""
        self._ignore_hide = False
        
    def hidePopup(self):
        """Override para controlar quando o popup pode fechar"""
        if self._ignore_hide:
            return
        self._popup_visible = False
        super().hidePopup()
        
    def eventFilter(self, obj, event):
        """Filtrar eventos para evitar fechamento prematuro"""
        # Ignorar eventos que podem causar fechamento prematuro
        if obj == self.view().viewport():
            if event.type() == QEvent.Type.MouseButtonRelease:
                # Permitir seleção mas com delay para evitar bug do Windows
                index = self.view().indexAt(event.pos())
                if index.isValid():
                    QTimer.singleShot(50, lambda: self._select_item(index.row()))
                    return True
        return super().eventFilter(obj, event)
    
    def _select_item(self, row: int):
        """Seleciona item de forma segura"""
        if 0 <= row < self.count():
            self.setCurrentIndex(row)
            self._popup_visible = False
            super().hidePopup()
        
    def focusOutEvent(self, event):
        """Evitar fechamento prematuro do popup"""
        # Não propagar se o popup estiver visível
        if self._popup_visible:
            return
        super().focusOutEvent(event)
        
    def keyPressEvent(self, event):
        """Permitir navegação por teclado e seleção com Enter"""
        if self._popup_visible:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                # Selecionar item atual e fechar
                self._popup_visible = False
                super().hidePopup()
                return
            elif event.key() == Qt.Key.Key_Escape:
                # Fechar sem selecionar
                self._popup_visible = False
                super().hidePopup()
                return
        super().keyPressEvent(event)
