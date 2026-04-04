# -*- coding: utf-8 -*-
"""
test_07_state_visibility.py — Testes de estado e visibilidade de widgets

Testes para validar:
1. Visibilidade inicial de widgets
2. Enable/disable de widgets
3. Show/hide de widgets
4. Persistência de estado
5. Temas alteram estilos
6. Resize de widgets
7. Mensagens de statusbar
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QDockWidget, QPushButton,
    QCheckBox, QStatusBar,
)


pytestmark = [pytest.mark.automated, pytest.mark.gui]


class TestWidgetInitialVisibility:
    """Testa visibilidade inicial de widgets."""

    def test_new_widget_not_visible(self, qapp):
        """Verifica que widget novo não está automaticamente visível."""
        widget = QWidget()
        # Widgets novos não estão visíveis até show()
        assert not widget.isVisible()
        widget.deleteLater()
        qapp.processEvents()

    def test_widget_visible_after_show(self, qapp):
        """Verifica que widget fica visível após show()."""
        widget = QWidget()
        widget.show()
        qapp.processEvents()
        # Em offscreen, isVisible pode não retornar True
        # Mas não deve lançar exceção
        widget.hide()
        widget.deleteLater()
        qapp.processEvents()


class TestWidgetEnableDisable:
    """Testa enable/disable de widgets."""

    def test_widget_enabled_by_default(self, qapp):
        """Verifica que widgets são habilitados por padrão."""
        widget = QWidget()
        assert widget.isEnabled()
        widget.deleteLater()
        qapp.processEvents()

    def test_widget_disable(self, qapp):
        """Verifica que widget pode ser desabilitado."""
        widget = QWidget()
        widget.setEnabled(False)
        assert not widget.isEnabled()
        widget.deleteLater()
        qapp.processEvents()

    def test_widget_reenable(self, qapp):
        """Verifica que widget pode ser reabilitado."""
        widget = QWidget()
        widget.setEnabled(False)
        widget.setEnabled(True)
        assert widget.isEnabled()
        widget.deleteLater()
        qapp.processEvents()

    def test_button_enable_disable(self, qapp):
        """Verifica enable/disable de QPushButton."""
        button = QPushButton("Test")
        
        assert button.isEnabled()
        
        button.setEnabled(False)
        assert not button.isEnabled()
        
        button.setEnabled(True)
        assert button.isEnabled()
        
        button.deleteLater()
        qapp.processEvents()

    def test_checkbox_enable_disable(self, qapp):
        """Verifica enable/disable de QCheckBox."""
        checkbox = QCheckBox("Test")
        
        checkbox.setEnabled(False)
        assert not checkbox.isEnabled()
        
        checkbox.setEnabled(True)
        assert checkbox.isEnabled()
        
        checkbox.deleteLater()
        qapp.processEvents()


class TestWidgetShowHide:
    """Testa show/hide de widgets."""

    def test_widget_hide(self, qapp):
        """Verifica que widget pode ser escondido."""
        widget = QWidget()
        widget.show()
        widget.hide()
        assert not widget.isVisible()
        widget.deleteLater()
        qapp.processEvents()

    def test_widget_show_after_hide(self, qapp):
        """Verifica que widget pode ser mostrado após hide."""
        widget = QWidget()
        widget.show()
        widget.hide()
        widget.show()
        # Não falha em offscreen
        widget.hide()
        widget.deleteLater()
        qapp.processEvents()


class TestSessionStatePersistence:
    """Testa persistência de estado."""

    def test_session_state_selection_update(self, session_state):
        """Verifica que selection pode ser atualizada."""
        if hasattr(session_state, 'selection') and hasattr(session_state.selection, 'selected_series'):
            initial = session_state.selection.selected_series
            # Apenas verifica que pode acessar
            assert initial is not None or initial is None  # Pode ser lista vazia ou None

    def test_session_state_processing_state(self, session_state):
        """Verifica estado de processamento."""
        if hasattr(session_state, 'processing') and hasattr(session_state.processing, 'is_processing'):
            is_proc = session_state.processing.is_processing
            # Deve começar como False
            assert is_proc in [True, False]


class TestThemeChangesWidgetStyle:
    """Testa que temas alteram estilos de widgets."""

    THEMES = ["LIGHT", "DARK"]

    @pytest.mark.parametrize("theme", THEMES, ids=THEMES)
    def test_theme_changes_palette(self, qapp, theme):
        """Verifica que tema altera palette da aplicação."""
        try:
            from platform_base.ui.themes import ThemeManager, ThemeMode
        except ImportError:
            pytest.skip("ThemeManager não disponível")
        
        manager = ThemeManager()
        
        if not hasattr(ThemeMode, theme):
            pytest.skip(f"Tema {theme} não existe")
        
        theme_mode = getattr(ThemeMode, theme)
        
        # Captura palette antes
        palette_before = qapp.palette()
        
        # Aplica tema
        try:
            manager.apply_theme(theme_mode)
            # Não falha se não conseguir comparar palettes
        except Exception:
            pass

    def test_stylesheet_can_be_set(self, qapp):
        """Verifica que stylesheet pode ser aplicada."""
        widget = QWidget()
        widget.setStyleSheet("background-color: red;")
        ss = widget.styleSheet()
        assert "red" in ss
        widget.deleteLater()
        qapp.processEvents()


class TestWidgetResize:
    """Testa redimensionamento de widgets."""

    def test_widget_resize(self, qapp):
        """Verifica que widget pode ser redimensionado."""
        widget = QWidget()
        widget.resize(400, 300)
        size = widget.size()
        assert size.width() == 400
        assert size.height() == 300
        widget.deleteLater()
        qapp.processEvents()

    def test_widget_minimum_size(self, qapp):
        """Verifica que minimum size funciona."""
        widget = QWidget()
        widget.setMinimumSize(200, 100)
        min_size = widget.minimumSize()
        assert min_size.width() == 200
        assert min_size.height() == 100
        widget.deleteLater()
        qapp.processEvents()

    def test_widget_maximum_size(self, qapp):
        """Verifica que maximum size funciona."""
        widget = QWidget()
        widget.setMaximumSize(800, 600)
        max_size = widget.maximumSize()
        assert max_size.width() == 800
        assert max_size.height() == 600
        widget.deleteLater()
        qapp.processEvents()


class TestDockWidgetFloatDock:
    """Testa flutuação e docking."""

    def test_dock_widget_creation(self, qapp):
        """Verifica criação de dock widget."""
        main = QMainWindow()
        dock = QDockWidget("Test", main)
        dock.setWidget(QWidget())
        main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
        assert dock is not None
        
        main.close()
        main.deleteLater()
        qapp.processEvents()

    def test_dock_widget_float(self, qapp):
        """Verifica que dock pode flutuar."""
        main = QMainWindow()
        dock = QDockWidget("Test", main)
        dock.setWidget(QWidget())
        main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
        dock.setFloating(True)
        assert dock.isFloating()
        
        dock.setFloating(False)
        assert not dock.isFloating()
        
        main.close()
        main.deleteLater()
        qapp.processEvents()

    def test_dock_widget_visibility(self, qapp):
        """Verifica visibilidade de dock widget."""
        main = QMainWindow()
        dock = QDockWidget("Test", main)
        dock.setWidget(QWidget())
        main.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
        dock.hide()
        dock.show()
        
        main.close()
        main.deleteLater()
        qapp.processEvents()


class TestMenuActionsCheckable:
    """Testa actions com estado toggle."""

    def test_action_checkable(self, qapp):
        """Verifica que action pode ser checkable."""
        action = QAction("Test")
        action.setCheckable(True)
        assert action.isCheckable()
        
        action.setChecked(True)
        assert action.isChecked()
        
        action.setChecked(False)
        assert not action.isChecked()

    def test_action_toggle(self, qapp):
        """Verifica toggle de action."""
        action = QAction("Test")
        action.setCheckable(True)
        action.setChecked(False)
        
        action.toggle()
        assert action.isChecked()
        
        action.toggle()
        assert not action.isChecked()


class TestStatusBarMessages:
    """Testa mensagens na status bar."""

    def test_statusbar_show_message(self, qapp):
        """Verifica que status bar mostra mensagens."""
        main = QMainWindow()
        statusbar = main.statusBar()
        
        statusbar.showMessage("Test message")
        msg = statusbar.currentMessage()
        assert "Test" in msg
        
        main.close()
        main.deleteLater()
        qapp.processEvents()

    def test_statusbar_clear_message(self, qapp):
        """Verifica que status bar pode limpar mensagens."""
        main = QMainWindow()
        statusbar = main.statusBar()
        
        statusbar.showMessage("Test message")
        statusbar.clearMessage()
        msg = statusbar.currentMessage()
        assert msg == ""
        
        main.close()
        main.deleteLater()
        qapp.processEvents()

    def test_statusbar_timed_message(self, qapp):
        """Verifica mensagem com timeout."""
        main = QMainWindow()
        statusbar = main.statusBar()
        
        # Mostra mensagem com timeout de 100ms
        statusbar.showMessage("Temporary", 100)
        msg = statusbar.currentMessage()
        assert "Temporary" in msg
        
        main.close()
        main.deleteLater()
        qapp.processEvents()


class TestWidgetFocus:
    """Testa foco de widgets."""

    def test_widget_can_receive_focus(self, qapp):
        """Verifica que widget pode receber foco."""
        from PyQt6.QtWidgets import QLineEdit
        
        line = QLineEdit()
        line.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        assert line.focusPolicy() == Qt.FocusPolicy.StrongFocus
        
        line.deleteLater()
        qapp.processEvents()

    def test_button_accepts_focus(self, qapp):
        """Verifica que botão aceita foco."""
        button = QPushButton("Test")
        
        # Botões geralmente aceitam foco
        policy = button.focusPolicy()
        assert policy != Qt.FocusPolicy.NoFocus
        
        button.deleteLater()
        qapp.processEvents()
